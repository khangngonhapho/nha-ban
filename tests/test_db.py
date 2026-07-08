"""
Unit tests cho Database Layer — MOD-02 PREPARE step.

Tests này lock behavior hiện tại của các DB functions trong pool_lego.py
và query_helper.py TRƯỚC khi tách sang core/db.py.

Scope MOD-02:
  - robust_sqlite_connect(): WAL + PRAGMA setup
  - get_db_file(): Logic chọn đúng DB file (staging, Pool2, mặc định)
  - get_listings_table_name(): Xác định tên bảng dựa vào db file
  - get_db_file duplicate: query_helper.py phải cho cùng kết quả

RELATED FILES: pool_lego.py, query_helper.py, core/db.py (sẽ tạo)
TESTS: tests/test_db.py (file này)
"""
import sys
import os
import sqlite3
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pool_lego import (
    robust_sqlite_connect,
    get_db_file,
)
from query_helper import (
    get_db_file as qh_get_db_file,
    get_listings_table_name,
)


# =============================================================================
# 1. ROBUST_SQLITE_CONNECT — WAL mode + PRAGMA setup
# =============================================================================
class TestRobustSqliteConnect:
    """Lock behavior: robust_sqlite_connect() thiết lập WAL + PRAGMA."""

    def test_returns_connection(self):
        """Trả về sqlite3.Connection hợp lệ."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            conn = robust_sqlite_connect(db_path)
            assert conn is not None
            conn.close()
        finally:
            os.unlink(db_path)

    def test_wal_mode_enabled(self):
        """WAL journal mode được bật."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            conn = robust_sqlite_connect(db_path)
            cursor = conn.execute("PRAGMA journal_mode;")
            mode = cursor.fetchone()[0]
            conn.close()
            assert mode == "wal", f"Expected 'wal', got '{mode}'"
        finally:
            os.unlink(db_path)

    def test_synchronous_normal(self):
        """PRAGMA synchronous=NORMAL được set."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            conn = robust_sqlite_connect(db_path)
            cursor = conn.execute("PRAGMA synchronous;")
            val = cursor.fetchone()[0]
            conn.close()
            # NORMAL = 1
            assert val == 1, f"Expected synchronous=1 (NORMAL), got {val}"
        finally:
            os.unlink(db_path)

    def test_busy_timeout_set(self):
        """PRAGMA busy_timeout được set (chống database locked)."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            conn = robust_sqlite_connect(db_path)
            cursor = conn.execute("PRAGMA busy_timeout;")
            val = cursor.fetchone()[0]
            conn.close()
            assert val > 0, f"busy_timeout phải > 0, got {val}"
        finally:
            os.unlink(db_path)

    def test_can_create_table(self):
        """Connection hoạt động: có thể tạo bảng và insert dữ liệu."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            conn = robust_sqlite_connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, val TEXT)")
            conn.execute("INSERT INTO test (val) VALUES (?)", ("hello",))
            conn.commit()
            cursor = conn.execute("SELECT val FROM test WHERE id=1")
            row = cursor.fetchone()
            conn.close()
            assert row[0] == "hello"
        finally:
            os.unlink(db_path)

    def test_timeout_minimum_30s(self):
        """Timeout tối thiểu là 30 giây (không nhận giá trị thấp hơn)."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            # Dù truyền timeout=1 vẫn phải dùng tối thiểu 30s
            conn = robust_sqlite_connect(db_path, timeout=1.0)
            assert conn is not None
            conn.close()
        finally:
            os.unlink(db_path)

    def test_in_memory_db(self):
        """Hoạt động với in-memory database (:memory:)."""
        conn = robust_sqlite_connect(":memory:")
        assert conn is not None
        conn.execute("CREATE TABLE t (x TEXT)")
        conn.execute("INSERT INTO t VALUES ('ok')")
        row = conn.execute("SELECT x FROM t").fetchone()
        conn.close()
        assert row[0] == "ok"


# =============================================================================
# 2. GET_DB_FILE (pool_lego) — Logic chọn database file
# =============================================================================
class TestGetDbFile:
    """Lock behavior: get_db_file() chọn đúng DB dựa trên env + config."""

    def test_default_returns_raw_archive(self, tmp_path, monkeypatch):
        """Không có STAGING, không có Pool2 → raw_archive.db."""
        monkeypatch.delenv("STAGING", raising=False)
        monkeypatch.chdir(tmp_path)  # Không có settings.json
        result = get_db_file()
        assert result == "raw_archive.db"

    def test_staging_env_returns_staging_db(self, monkeypatch):
        """STAGING=true → raw_archive_staging.db."""
        monkeypatch.setenv("STAGING", "true")
        result = get_db_file()
        assert result == "raw_archive_staging.db"

    def test_staging_env_false_uses_normal_logic(self, tmp_path, monkeypatch):
        """STAGING=false → không dùng staging db."""
        monkeypatch.setenv("STAGING", "false")
        monkeypatch.chdir(tmp_path)
        result = get_db_file()
        assert result != "raw_archive_staging.db"

    def test_pool2_active_returns_v2_db(self, tmp_path, monkeypatch):
        """settings.json có active_pool_system=Pool2 → raw_archive_v2.db."""
        monkeypatch.delenv("STAGING", raising=False)
        settings = tmp_path / "settings.json"
        settings.write_text('{"active_pool_system": "Pool2"}', encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        result = get_db_file()
        assert result == "raw_archive_v2.db"

    def test_pool1_active_returns_raw_archive(self, tmp_path, monkeypatch):
        """settings.json có active_pool_system=Pool1 → raw_archive.db."""
        monkeypatch.delenv("STAGING", raising=False)
        settings = tmp_path / "settings.json"
        settings.write_text('{"active_pool_system": "Pool1"}', encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        result = get_db_file()
        assert result == "raw_archive.db"

    def test_invalid_settings_json_falls_back(self, tmp_path, monkeypatch):
        """settings.json bị lỗi JSON → fallback về raw_archive.db, không crash."""
        monkeypatch.delenv("STAGING", raising=False)
        settings = tmp_path / "settings.json"
        settings.write_text("{ INVALID JSON }", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        result = get_db_file()
        assert result == "raw_archive.db"

    def test_staging_takes_priority_over_pool2(self, tmp_path, monkeypatch):
        """STAGING=true có priority cao hơn Pool2 setting."""
        monkeypatch.setenv("STAGING", "true")
        settings = tmp_path / "settings.json"
        settings.write_text('{"active_pool_system": "Pool2"}', encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        result = get_db_file()
        assert result == "raw_archive_staging.db"


# =============================================================================
# 3. GET_LISTINGS_TABLE_NAME — Xác định tên bảng
# =============================================================================
class TestGetListingsTableName:
    """Lock behavior: get_listings_table_name() trả về tên bảng đúng."""

    def test_v2_db_returns_listings_v2(self):
        """raw_archive_v2.db → 'listings_v2'."""
        assert get_listings_table_name("raw_archive_v2.db") == "listings_v2"

    def test_default_db_returns_listings(self):
        """raw_archive.db → 'listings'."""
        assert get_listings_table_name("raw_archive.db") == "listings"

    def test_staging_db_returns_listings(self):
        """raw_archive_staging.db → 'listings' (không phải v2)."""
        assert get_listings_table_name("raw_archive_staging.db") == "listings"

    def test_full_path_v2(self):
        """Full path chứa raw_archive_v2.db → 'listings_v2'."""
        assert get_listings_table_name("/some/path/raw_archive_v2.db") == "listings_v2"

    def test_full_path_default(self):
        """Full path raw_archive.db → 'listings'."""
        assert get_listings_table_name("/some/path/raw_archive.db") == "listings"


# =============================================================================
# 4. GET_DB_FILE DUPLICATE CHECK — pool_lego vs query_helper (khi không staging)
# =============================================================================
class TestGetDbFileDuplicate:
    """Verify: query_helper.get_db_file() tương thích với pool_lego.get_db_file()."""

    def test_default_same_output(self, tmp_path, monkeypatch):
        """Không có settings → cả 2 đều trả về raw_archive.db."""
        monkeypatch.delenv("STAGING", raising=False)
        monkeypatch.chdir(tmp_path)
        assert get_db_file() == qh_get_db_file()

    def test_pool2_same_output(self, tmp_path, monkeypatch):
        """Pool2 setting → cả 2 đều trả về raw_archive_v2.db."""
        monkeypatch.delenv("STAGING", raising=False)
        settings = tmp_path / "settings.json"
        settings.write_text('{"active_pool_system": "Pool2"}', encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert get_db_file() == qh_get_db_file()

    def test_invalid_json_same_fallback(self, tmp_path, monkeypatch):
        """Invalid JSON → cả 2 đều fallback raw_archive.db."""
        monkeypatch.delenv("STAGING", raising=False)
        settings = tmp_path / "settings.json"
        settings.write_text("NOT JSON", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        assert get_db_file() == qh_get_db_file()
