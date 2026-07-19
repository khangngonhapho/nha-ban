"""
Core Database Layer — BDS KhangNgo.

Tập trung toàn bộ SQLite connection management và database routing logic.
Được tách từ pool_lego.py và query_helper.py trong MOD-02.

SCOPE:
  - robust_sqlite_connect(): WAL + PRAGMA hardened connection
  - get_db_file():           Routing logic (staging / Pool2 / default)
  - get_listings_table_name(): Xác định tên bảng theo DB file

KHÔNG bao gồm (quá phức tạp, giữ trong pool_lego.py):
  - init_db():          Schema creation + migration (~400 lines)
  - save_raw_to_sqlite(): CRUD operations (~237 lines)

BUSINESS RULES:
  - docs/transformation_roadmap.md (MOD-02)

RELATED FILES:
  - pool_lego.py      → Delegate wrappers sau WIRE
  - query_helper.py   → Duplicate get_db_file sẽ delegate về đây
  - manager.py        → Consumer

TESTS: tests/test_db.py

OWNER: MOD-02 (Architecture Modernization)
"""

import os
import json
import sqlite3

# Lấy sqlite3.connect GỐC từ C extension, bypass monkey-patch của pool_lego.py.
# pool_lego.py gán sqlite3.connect = robust_sqlite_connect ở module level,
# nên nếu core/db.py được import SAU pool_lego.py thì sqlite3.connect
# đã bị patch. Ta cần truy cập C implementation trực tiếp.
try:
    import _sqlite3 as _sqlite3_c_ext
    _sqlite3_connect_original = _sqlite3_c_ext.connect
except ImportError:
    # Fallback: lấy trước khi bị patch (chỉ work nếu import trước pool_lego)
    _sqlite3_connect_original = sqlite3.connect


# =============================================================================
# 1. ROBUST SQLITE CONNECTION
# =============================================================================

def robust_sqlite_connect(database: str, timeout: float = 30.0, *args, **kwargs):
    """
    Bọc sqlite3.connect với WAL journal mode và PRAGMA tối ưu hóa.

    Chống các lỗi phổ biến:
    - "database is locked" → WAL mode + busy_timeout
    - "database disk image is malformed" → synchronous=FULL + timeout cao

    PRAGMAs được set:
    - journal_mode=WAL:     Multi-reader, single-writer, không block
    - synchronous=FULL:     Đảm bảo tuyệt đối toàn vẹn dữ liệu khi crash (WAL mode)
    - busy_timeout=30000:   Chờ tối đa 30 giây nếu DB bị lock

    Args:
        database: Đường dẫn file SQLite hoặc ':memory:'.
        timeout:  Connection timeout (giây). Tối thiểu 30s được đảm bảo.
        *args, **kwargs: Truyền thẳng vào sqlite3.connect.

    Returns:
        sqlite3.Connection đã được cấu hình WAL + PRAGMA.

    Examples:
        >>> conn = robust_sqlite_connect("raw_archive.db")
        >>> conn = robust_sqlite_connect(":memory:")
    """
    # Gọi trực tiếp _sqlite3_connect_original để tránh circular khi
    # pool_lego.py monkey-patch sqlite3.connect = robust_sqlite_connect
    conn = _sqlite3_connect_original(database, timeout=max(timeout, 30.0), *args, **kwargs)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=FULL;")
        conn.execute("PRAGMA busy_timeout=30000;")
    except Exception:
        pass
    return conn


# =============================================================================
# 2. DATABASE FILE ROUTING
# =============================================================================

def get_db_file() -> str:
    """
    Xác định và trả về đường dẫn tệp tin SQLite đang được hệ thống kích hoạt.

    Priority:
    1. Env var STAGING=true  → raw_archive_staging.db
    2. settings.json Pool2   → raw_archive_v2.db
    3. Default               → raw_archive.db

    Nếu có cấu hình database_dir trong settings.json và thư mục đó tồn tại trên đĩa,
    sẽ trả về đường dẫn tuyệt đối đầy đủ của tệp tin SQLite nằm trong thư mục đó.
    Nếu không, trả về tên tệp tin tương đối phục vụ tương thích ngược (fallback).
    """
    filename = "raw_archive.db"
    if os.environ.get("STAGING") == "true":
        filename = "raw_archive_staging.db"
    else:
        try:
            from core.config import read_settings
            cfg = read_settings()
            if cfg.get("active_pool_system") == "Pool2":
                filename = "raw_archive_v2.db"
        except Exception:
            pass

    try:
        from core.config import read_settings
        cfg = read_settings()
        db_dir = cfg.get("database_dir")
        if db_dir and os.path.exists(db_dir):
            return os.path.abspath(os.path.join(db_dir, filename))
    except Exception:
        pass

    return filename


# =============================================================================
# 3. TABLE NAME ROUTING
# =============================================================================

def get_listings_table_name(db_file: str) -> str:
    """
    Xác định tên bảng listings dựa trên tên file DB.

    Pool2 dùng bảng 'listings_v2', Pool1 dùng 'listings'.

    Args:
        db_file: Tên hoặc đường dẫn file DB.

    Returns:
        'listings_v2' nếu là Pool2, 'listings' trong các trường hợp còn lại.

    Examples:
        >>> get_listings_table_name("raw_archive_v2.db")
        'listings_v2'
        >>> get_listings_table_name("raw_archive.db")
        'listings'
        >>> get_listings_table_name("raw_archive_staging.db")
        'listings'
    """
    if "raw_archive_v2.db" in db_file:
        return "listings_v2"
    return "listings"


# =============================================================================
# 4. STARTUP INTEGRITY GUARD (Phương án C)
# =============================================================================

# Module-level state: kết quả kiểm tra toàn vẹn CSDL khi khởi động
_integrity_status = {
    "checked": False,
    "healthy": True,
    "details": "",
    "db_file": "",
    "checked_at": ""
}


def get_integrity_status() -> dict:
    """
    Trả về kết quả kiểm tra toàn vẹn CSDL gần nhất.
    
    Returns:
        Dict chứa trạng thái kiểm tra: checked, healthy, details, db_file, checked_at.
    
    Examples:
        >>> status = get_integrity_status()
        >>> status["healthy"]
        True
    """
    return _integrity_status.copy()


def startup_integrity_check(db_file: str) -> bool:
    """
    Kiểm tra toàn vẹn CSDL SQLite MỘT LẦN DUY NHẤT khi Flask app khởi động.
    
    Chạy PRAGMA integrity_check để phát hiện corruption sớm.
    Kết quả được lưu vào module-level `_integrity_status` để Admin UI 
    hiển thị banner cảnh báo nếu CSDL bị hỏng.
    
    Chi phí: ~200-500ms cho DB 90MB, chỉ chạy 1 lần khi startup.
    
    Args:
        db_file: Đường dẫn tuyệt đối tới file SQLite cần kiểm tra.
    
    Returns:
        True nếu CSDL toàn vẹn, False nếu phát hiện lỗi.
    
    Examples:
        >>> startup_integrity_check("raw_archive.db")
        True
    """
    global _integrity_status
    
    from datetime import datetime
    
    _integrity_status["db_file"] = db_file
    _integrity_status["checked_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _integrity_status["checked"] = True
    
    if not os.path.exists(db_file):
        _integrity_status["healthy"] = True
        _integrity_status["details"] = "File CSDL chưa tồn tại (sẽ được tạo mới)."
        return True
    
    conn = None
    try:
        conn = _sqlite3_connect_original(db_file, timeout=30.0)
        result = conn.execute("PRAGMA integrity_check;").fetchone()
        
        if result and result[0] == "ok":
            _integrity_status["healthy"] = True
            _integrity_status["details"] = "ok"
            return True
        else:
            error_detail = result[0] if result else "Không có phản hồi từ integrity_check"
            _integrity_status["healthy"] = False
            _integrity_status["details"] = error_detail
            return False
    except Exception as e:
        _integrity_status["healthy"] = False
        _integrity_status["details"] = f"Lỗi khi kiểm tra: {str(e)}"
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
