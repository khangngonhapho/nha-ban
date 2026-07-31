# -*- coding: utf-8 -*-
"""
==================================================
KHANG NGÔ NHÀ PHỐ - POOL LEGO BLOCK
Khối Lego Điều Phối Dữ Liệu và Đồng Bộ Google Sheets (Phase 1)
==================================================
"""

import os
import sys
import re
import json
import random
import sqlite3


# Tối ưu hóa SQLite WAL mode và Timeout chống lỗi "database disk image is malformed" / "database is locked"
_orig_sqlite_connect = sqlite3.connect
def robust_sqlite_connect(database, timeout=30.0, *args, **kwargs):
    """
    ⚠️ DELEGATED: Logic đã chuyển sang core.db.robust_sqlite_connect()
    Monkey-patch giữ nguyên để tất cả sqlite3.connect() trong app dùng WAL.
    """
    from core.db import robust_sqlite_connect as _robust_connect
    return _robust_connect(database, timeout, *args, **kwargs)

from core.business_rules import gen_unique_system_id
sqlite3.connect = robust_sqlite_connect

import time
import threading
from datetime import datetime

# Khóa Lock dùng chung bảo vệ ghi Google Sheets đồng thời (Thread Safety)
sheets_lock = threading.Lock()

# Ép mã hóa UTF-8
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ==================================================
# 89 CỘT NGHIỆP VỤ ĐỒNG NHẤT VỚI POOL SHEET SCHEMA
# ==================================================
POOL_HEADERS = [
    "Mã Hàng", "Hình Nhận Diện", "Tỉnh", "Quận", "Phường", "Đường", "Ngõ/Số nhà", "Phân loại",
    "Năm xây dựng", "Nội dung chính", "Mô tả chi tiết", "Giá chào", "Giá chốt",
    "DT Thực tế", "DT Trên sổ", "Số Tầng", "Mặt Tiền", "Hướng", "Tên Chủ Nhà",
    "Điện thoại 1", "Điện thoại 2", "Loại Hợp đồng", "Số ngày ký", "Ngày bắt đầu",
    "Ngày kết thúc", "Người ký", "Trạng thái",
    "Sơ đồ thửa đất 1", "Sơ đồ thửa đất 2",
    "Hình Mặt Tiền",
    "Hình Hẻm 1", "Hình Hẻm 2", "Hình Hẻm 3", "Hình Hẻm 4", "Hình Hẻm 5", 
    "Hình Hẻm 6", "Hình Hẻm 7", "Hình Hẻm 8", "Hình Hẻm 9", "Hình Hẻm 10",
    "Ảnh 1", "Ảnh 2", "Ảnh 3", "Ảnh 4", "Ảnh 5", "Ảnh 6", "Ảnh 7", "Ảnh 8",
    "Ảnh 9", "Ảnh 10", "Ảnh 11", "Ảnh 12", "Ảnh 13", "Ảnh 14", "Ảnh 15",
    "Mã Khang Ngô (ID)", "Tiêu đề Public", "Mô tả Public", "Giá Public", 
    "Phân loại Hẻm", "Đường trước nhà (m)", "Tình trạng nhà", "Ảnh Public (VD: 1,3,5)", "Ảnh Hẻm Public (VD: 1,2)",
    "Số phòng ngủ", "Số nhà vệ sinh", "Phường cũ (AI)",
    "Đánh giá (Admin)", "Ngủ trệt (Admin)", "CHDV (Admin)",
    "Duyệt Public", "Trạng thái Public", "System ID", "Link Gốc",
    "Điện thoại Đầu Chủ", "Tên Đầu Chủ (Hợp đồng)", "Điểm Facebook",
    "Last Crawl", "Last Sync", "Mã TK Mới",
    "Sơ đồ thửa đất 3", "Sơ đồ thửa đất 4", "Sơ đồ thửa đất 5",
    "Ảnh 16", "Ảnh 17", "Ảnh 18", "Ảnh 19", "Ảnh 20",
    "Ảnh 21", "Ảnh 22", "Ảnh 23", "Ảnh 24", "Ảnh 25",
    "JSON_UI", "Images_Admin_JSON"
]

# ==================================================
# HẰNG SỐ TOÀN CỤC CHUẨN HÓA SHEET SYSTEM (RULE 13)
# ==================================================
HEADER_ROW_INDEX = 1
BLANK_ROW_INDEX = 2
DATA_START_ROW = 3
LOG_EVENT_COL_NAME = "Log event"
LOG_TIME_COL_NAME = "Log Time"

SOURCE_HEADERS = [
    "Hinh_mat_tien", "Cu_phap", "Note", "id", "tieu_de", "dien_tich", "so_tang", "mat_tien", "gia", "quan", "phuong",
    "loai_hinh", "huong_nha", "duong_truoc_nha", "do_rong_hem", "tinh_trang_nha", "danh_gia", "ngu_tang_tret", "chdv", "mo_ta",
    "anh_1", "anh_2", "anh_3", "anh_4", "anh_5", "anh_6", "anh_7", "anh_8", "anh_9", "anh_10",
    "Last updated", "phuong_cu", "so_pn", "so_wc", "ten_duong", "gio_dang", "trang_thai", "System ID", "Link mặt tiền",
    "Tiêu đề BDS", "Đăng BDS", "anh_11", "anh_12", "anh_13", "anh_14", "anh_15", "JSON_UI", "DT Trên sổ", "Images_Public_JSON"
]

POOL_LOG_HEADERS = list(POOL_HEADERS) + [LOG_EVENT_COL_NAME, LOG_TIME_COL_NAME]
SOURCE_LOG_HEADERS = list(SOURCE_HEADERS) + [LOG_EVENT_COL_NAME, LOG_TIME_COL_NAME]

GLOBAL_SHEET_CONFIG = {
    "Pool": {
        "header_row": HEADER_ROW_INDEX,
        "blank_row": BLANK_ROW_INDEX,
        "data_start_row": DATA_START_ROW,
        "headers": POOL_HEADERS
    },
    "Pool_Log": {
        "header_row": HEADER_ROW_INDEX,
        "blank_row": BLANK_ROW_INDEX,
        "data_start_row": DATA_START_ROW,
        "headers": POOL_LOG_HEADERS
    },
    "Source": {
        "header_row": HEADER_ROW_INDEX,
        "blank_row": BLANK_ROW_INDEX,
        "data_start_row": DATA_START_ROW,
        "headers": SOURCE_HEADERS
    },
    "Source_Log": {
        "header_row": HEADER_ROW_INDEX,
        "blank_row": BLANK_ROW_INDEX,
        "data_start_row": DATA_START_ROW,
        "headers": SOURCE_LOG_HEADERS
    }
}

LISTINGS_V2_COLS = [
    # Định danh & Trạng thái
    "System_ID", "Ma_Hang", "isSigned", "status_nguon", "commissionAgent",
    "ownerSideUserId", "certificateSeries", "latitude", "longitude", "placeName",
    "streetName", "Quan", "Phuong", "Ngo_So_nha",
    # Kỹ thuật & Tiêu chí phong phú từ API
    "bedrooms", "restrooms", "balconies", "sidewalk", "behindOpenSpace",
    "sideOpenSpace", "minimumRoadWidth", "createdAt", "updatedAt", "commissionType",
    "commissionValue", "isDispute", "createdAtSigned", "CCCD_Dau_Chu", "Kenh_tin_TK",
    "The_tags_TK",
    # Tiêu chí & Nghiệp vụ kế thừa từ Pool Headers (chỉ giữ phần cào được từ TK)
    "Noi_dung_chinh", "Mo_ta_chi_tiet", "Gia_chao", "DT_Thuc_te",
    "DT_Tren_so", "So_Tang", "Mat_Tien", "Chieu_dai", "Huong", "Ten_Chu_Nha",
    "Dien_thoai_1", "Ten_Dau_Chu", "Dien_thoai_Dau_Chu", "Diem_Facebook",
    "Link_Goc", "Last_Crawl", "Last_Sync"
]




def remove_accents(input_str):
    """
    Khử toàn bộ dấu tiếng Việt từ chuỗi đầu vào.
    
    ⚠️ DELEGATED: Logic đã chuyển sang core.business_rules.remove_accents()
    """
    from core.business_rules import remove_accents as _remove_accents
    return _remove_accents(input_str)

def get_safe_col_name(header):
    """
    Chuyển đổi nhãn cột tiếng Việt có dấu thành tên cột SQLite hợp lệ.
    
    ⚠️ DELEGATED: Logic đã chuyển sang core.business_rules.get_safe_col_name()
    """
    from core.business_rules import get_safe_col_name as _get_safe_col_name
    return _get_safe_col_name(header)


def parse_criteria_groups(criteria_list):
    """
    Phân loại các đặc tính (criteria) theo groupCode của TK thành 19 nhóm Tiếng Việt tương ứng.
    
    ⚠️ DELEGATED: Logic đã chuyển sang core.business_rules.parse_criteria_groups()
    """
    from core.business_rules import parse_criteria_groups as _parse_criteria_groups
    return _parse_criteria_groups(criteria_list)


def extract_json_ui_data(raw_json_dict):
    """
    Trích xuất các trường cấu hình từ raw_json_dict (detail_data của Thiên Khôi)
    để tạo thành đối tượng JSON UI tinh gọn.
    """
    from core.config import read_settings
    cfg = read_settings()
        
    fields = cfg.get("json_ui_fields") or ["Criteria_Duong_truoc_nha"]
    
    result = {}
    criteria_list = raw_json_dict.get("criteria") or []
    criteria_cols = {}
    if criteria_list:
        try:
            criteria_cols = parse_criteria_groups(criteria_list)
        except Exception:
            pass
            
    for f in fields:
        if f.startswith("Criteria_"):
            result[f] = criteria_cols.get(f, "")
        elif f == "latitude":
            result[f] = str((raw_json_dict.get("coordinate") or {}).get("latitude") or raw_json_dict.get("latitude") or "")
        elif f == "longitude":
            result[f] = str((raw_json_dict.get("coordinate") or {}).get("longitude") or raw_json_dict.get("longitude") or "")
        else:
            result[f] = raw_json_dict.get(f, "")
            
    return result


# ==================================================
# POOL2 HEADERS DEFINITIONS
# ==================================================

# 19 cột tiêu chí Criteria_... tường minh
EXPLICIT_CRITERIA_COLS = [
    "Criteria_Tiem_nang_Rui_ro",
    "Criteria_Duong_truoc_nha",
    "Criteria_Loai_BDS",
    "Criteria_Giay_to_phap_ly",
    "Criteria_Hinh_dang_dat",
    "Criteria_Tinh_trang_xay_dung",
    "Criteria_Cau_truc_nha",
    "Criteria_Noi_that",
    "Criteria_Thang_may",
    "Criteria_Loai_ngo",
    "Criteria_Vi_tri_tinh_thue",
    "Criteria_Mat_thoang",
    "Criteria_Khoang_cach_bai_do_xe",
    "Criteria_Kinh_doanh_Dong_tien",
    "Criteria_Tien_ich",
    "Criteria_Phong_thuy",
    "Criteria_Huong_nha",
    "Criteria_Vi_tri_trong_ngo",
    "Criteria_Khoang_cach_duong_oto"
]

# Danh sách cột cho File 1 Raw (tab Listings)
RAW_LISTINGS_HEADERS = [
    "tk_id", "status", "raw_images_tk_json", "raw_drive_images_json", "curated_config_json"
] + [col for col in LISTINGS_V2_COLS if col not in ["tk_id", "status"]] + EXPLICIT_CRITERIA_COLS

# Đảm bảo không trùng cột trong RAW_LISTINGS_HEADERS và chuẩn hóa tên cột SQLite
_seen = set()
_raw_dedup = []
for _col in RAW_LISTINGS_HEADERS:
    _name = get_safe_col_name(_col)
    if _name not in _seen:
        _seen.add(_name)
        _raw_dedup.append(_name)
RAW_LISTINGS_HEADERS = _raw_dedup

# Danh sách cột cho File 2 Custom (tab Custom)
CUSTOM_HEADERS = [
    "System_ID", "Ma_Khang_Ngo", "Gia_Public", "Tieu_De_Public", "Mo_ta_Public",
    "Note_Noi_Bo", "Trang_Thai_Giao_Dich", "Ngu_Tret", "CHDV", "Trang_Thai_KN",
    "images_metadata_json", "Dia_Chi_That", "So_Nha", "Ten_Duong", "Quan",
    "Phuong", "Duong", "Ngo_So_nha", "bedrooms", "restrooms", "minimumRoadWidth",
    "Noi_dung_chinh", "Mo_ta_chi_tiet", "Gia_chao", "DT_Thuc_te", "DT_Tren_so",
    "So_Tang", "Mat_Tien", "Chieu_dai", "Huong", "Criteria_Duong_truoc_nha",
    "Criteria_Noi_that", "Criteria_Thang_may", "Criteria_Loai_ngo",
    "Criteria_Khoang_cach_bai_do_xe", "Criteria_Kinh_doanh_Dong_tien",
    "Criteria_Huong_nha", "Criteria_Khoang_cach_duong_oto", "latitude", "longitude"
]

# Danh sách cột cho File 3 Public (tab Public)
PUBLIC_WHITELIST_HEADERS_BASE = [
    "System_ID",
    "Ma_Khang_Ngo",
    "Tieu_De_Public",
    "Mo_ta_Public",
    "Gia_Public",
    "Trang_Thai_Giao_Dich",
    "Ngu_Tret",
    "CHDV",
    "Trang_Thai_KN",
    "Ten_Duong",
    "Quan",
    "Phuong",
    "Duong",
    "bedrooms",
    "restrooms",
    "minimumRoadWidth",
    "DT_Thuc_te",
    "DT_Tren_so",
    "So_Tang",
    "Mat_Tien",
    "Chieu_dai",
    "Huong",
    "Criteria_Duong_truoc_nha",
    "Criteria_Noi_that",
    "Criteria_Thang_may",
    "Criteria_Loai_ngo",
    "Criteria_Khoang_cach_bai_do_xe",
    "Criteria_Kinh_doanh_Dong_tien",
    "Criteria_Huong_nha",
    "Criteria_Khoang_cach_duong_oto",
    "Last updated"
]

def escape_sheets_value(val):
    """
    Tránh lỗi công thức khi ghi lên Google Sheets bằng USER_ENTERED.
    
    ⚠️ DELEGATED: Logic đã chuyển sang core.business_rules.escape_sheets_value()
    """
    from core.business_rules import escape_sheets_value as _escape_sheets_value
    return _escape_sheets_value(val)

def build_row_data(headers, data_dict):
    """
    Phân giải chỉ số cột động.
    
    ⚠️ DELEGATED: Logic đã chuyển sang core.business_rules.build_row_data()
    """
    from core.business_rules import build_row_data as _build_row_data
    return _build_row_data(headers, data_dict)

def gen_id_khang_ngo_python(so_nha, duong, quan):
    """
    Tự động sinh mã ID Khang Ngô độc nhất dựa trên số nhà, tên đường, tên quận.
    
    ⚠️ DELEGATED: Logic đã chuyển sang core.business_rules.gen_id_khang_ngo_python()
    """
    from core.business_rules import gen_id_khang_ngo_python as _gen_id
    return _gen_id(so_nha, duong, quan)

def clean_sheet_formula_prefix(val):
    """
    Loại bỏ ký tự khởi đầu công thức Google Sheets ở đầu chuỗi văn bản thô.
    
    ⚠️ DELEGATED: Logic đã chuyển sang core.business_rules.clean_sheet_formula_prefix()
    """
    from core.business_rules import clean_sheet_formula_prefix as _clean
    return _clean(val)

def get_db_file():
    """
    Xác định và trả về đường dẫn tệp tin SQLite đang được hệ thống kích hoạt.
    
    ⚠️ DELEGATED: Logic đã chuyển sang core.db.get_db_file()
    """
    from core.db import get_db_file as _get_db_file
    return _get_db_file()

def init_db(db_file=None):
    """
    Khởi tạo cơ sở dữ liệu SQLite cục bộ, bao gồm việc định nghĩa schema bảng listings 
    và crawl_sessions. Tự động nâng cấp (migration) thêm cột mới nếu POOL_HEADERS thay đổi.
    
    Args:
        db_file (str/None): Tên file SQLite cần khởi tạo.
        
    Storage:
        Ghi đè/Tạo tệp SQLite trên đĩa cứng cục bộ.
    """
    if not db_file:
        db_file = get_db_file()
        
    conn = sqlite3.connect(db_file, timeout=30.0)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL;")
    except Exception:
        pass

    # Xác định pool system đang hoạt động
    is_pool2 = False
    try:
        from core.config import read_settings
        cfg = read_settings()
        if cfg.get("active_pool_system") == "Pool2":
            is_pool2 = True
    except Exception:
        pass

    if is_pool2:
        # 19 cột tiêu chí Criteria_... tường minh
        explicit_criteria_cols = [
            "Criteria_Tiem_nang_Rui_ro",
            "Criteria_Duong_truoc_nha",
            "Criteria_Loai_BDS",
            "Criteria_Giay_to_phap_ly",
            "Criteria_Hinh_dang_dat",
            "Criteria_Tinh_trang_xay_dung",
            "Criteria_Cau_truc_nha",
            "Criteria_Noi_that",
            "Criteria_Thang_may",
            "Criteria_Loai_ngo",
            "Criteria_Vi_tri_tinh_thue",
            "Criteria_Mat_thoang",
            "Criteria_Khoang_cach_bai_do_xe",
            "Criteria_Kinh_doanh_Dong_tien",
            "Criteria_Tien_ich",
            "Criteria_Phong_thuy",
            "Criteria_Huong_nha",
            "Criteria_Vi_tri_trong_ngo",
            "Criteria_Khoang_cach_duong_oto"
        ]

        # Self-healing Schema alignment for listings_v2 (US-089A)
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings_v2'")
            if cursor.fetchone():
                cursor.execute("PRAGMA table_info(listings_v2)")
                actual_cols = [row[1] for row in cursor.fetchall()]
                
                # Define correct allowed columns for listings_v2
                correct_cols = {
                    "tk_id", "status", "raw_images_tk_json", "raw_drive_images_json", "curated_config_json", "Chieu_dai"
                }
                for col in explicit_criteria_cols:
                    correct_cols.add(col)
                for col in LISTINGS_V2_COLS:
                    correct_cols.add(get_safe_col_name(col))
                
                # Check if there are dirty columns (like custom V1 columns)
                dirty_cols = [c for c in actual_cols if c not in correct_cols]
                if dirty_cols:
                    print(f"[🛡️ SCHEMA REALIGNMENT] Found invalid columns in listings_v2: {dirty_cols}. Re-aligning schema...")
                    
                    # Fetch all existing rows
                    cursor.execute("SELECT * FROM listings_v2")
                    rows = cursor.fetchall()
                    
                    # Drop the old table
                    cursor.execute("DROP TABLE listings_v2")
                    conn.commit()
                    
                    # Re-create table using correct columns definition
                    columns_def = [
                        "tk_id TEXT PRIMARY KEY",
                        "status TEXT DEFAULT 'raw_text'",
                        "raw_images_tk_json TEXT",
                        "raw_drive_images_json TEXT",
                        "curated_config_json TEXT",
                        "Chieu_dai TEXT"
                    ]
                    for col in explicit_criteria_cols:
                        columns_def.append(f"`{col}` TEXT")
                    for col in LISTINGS_V2_COLS:
                        col_name = get_safe_col_name(col)
                        if col_name not in ["tk_id", "status"] and col_name not in explicit_criteria_cols:
                            if not any(c.startswith(f"`{col_name}` ") or c.startswith(f"{col_name} ") for c in columns_def):
                                columns_def.append(f"`{col_name}` TEXT")
                                
                    create_table_sql = f"CREATE TABLE listings_v2 ({', '.join(columns_def)})"
                    cursor.execute(create_table_sql)
                    conn.commit()
                    
                    # Restore rows
                    if rows:
                        common_cols = [c for c in actual_cols if c in correct_cols]
                        placeholders = ", ".join(["?" for _ in common_cols])
                        cols_str = ", ".join([f"`{c}`" for c in common_cols])
                        col_indices = [actual_cols.index(c) for c in common_cols]
                        
                        for row in rows:
                            row_data_vals = [row[idx] for idx in col_indices]
                            cursor.execute(f"INSERT OR REPLACE INTO listings_v2 ({cols_str}) VALUES ({placeholders})", row_data_vals)
                        conn.commit()
                        print(f"[✅ SCHEMA REALIGNMENT] Restored {len(rows)} rows into clean listings_v2.")
        except Exception as e_realignment:
            print(f"[❌ SCHEMA REALIGNMENT ERROR] {str(e_realignment)}")

        # Bảng listings_v2 (Chứa metadata văn bản thô đầy đủ trường)
        columns_def = [
            "tk_id TEXT PRIMARY KEY",
            "status TEXT DEFAULT 'raw_text'",
            "raw_images_tk_json TEXT",
            "raw_drive_images_json TEXT",
            "curated_config_json TEXT",
            "Chieu_dai TEXT",
            "pending_diff_json TEXT"
        ]
        for col in explicit_criteria_cols:
            columns_def.append(f"`{col}` TEXT")

        # Sinh thêm cột từ LISTINGS_V2_COLS (nếu chưa có trong list trên)
        for col in LISTINGS_V2_COLS:
            col_name = get_safe_col_name(col)
            if col_name not in ["tk_id", "status"] and col_name not in explicit_criteria_cols:
                if not any(c.startswith(f"`{col_name}` ") or c.startswith(f"{col_name} ") for c in columns_def):
                    columns_def.append(f"`{col_name}` TEXT")

        create_table_sql = f"CREATE TABLE IF NOT EXISTS listings_v2 ({', '.join(columns_def)})"
        cursor.execute(create_table_sql)
        conn.commit()

        # Bảng listings_images (Lưu trữ ảnh dạng dòng)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tk_id TEXT NOT NULL,
            system_id TEXT,
            image_url TEXT,
            r2_url TEXT,
            role TEXT,
            sequence_index INTEGER,
            edited_by TEXT,
            origin TEXT DEFAULT 'crawl',
            is_hidden INTEGER DEFAULT 0,
            uploaded_at TEXT
        )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_listings_images_tk_id ON listings_images(tk_id)")
        conn.commit()

        # Bảng listings_custom_v2 (Lưu thông tin tùy biến của Admin, cột đè trùng tên listings_v2)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings_custom_v2 (
            System_ID TEXT PRIMARY KEY,
            Ma_Khang_Ngo TEXT,
            Gia_Public TEXT,
            Tieu_De_Public TEXT,
            Mo_ta_Public TEXT,
            Note_Noi_Bo TEXT,
            Trang_Thai_Giao_Dich TEXT,
            Ngu_Tret TEXT,
            CHDV TEXT,
            Trang_Thai_KN TEXT,
            images_metadata_json TEXT,
            Dia_Chi_That TEXT,
            So_Nha TEXT,
            Ten_Duong TEXT,
            Quan TEXT,
            Phuong TEXT,
            Duong TEXT,
            Ngo_So_nha TEXT,
            bedrooms TEXT,
            restrooms TEXT,
            minimumRoadWidth TEXT,
            Noi_dung_chinh TEXT,
            Mo_ta_chi_tiet TEXT,
            Gia_chao TEXT,
            DT_Thuc_te TEXT,
            DT_Tren_so TEXT,
            So_Tang TEXT,
            Mat_Tien TEXT,
            Chieu_dai TEXT,
            Huong TEXT,
            Criteria_Duong_truoc_nha TEXT,
            Criteria_Noi_that TEXT,
            Criteria_Thang_may TEXT,
            Criteria_Loai_ngo TEXT,
            Criteria_Khoang_cach_bai_do_xe TEXT,
            Criteria_Kinh_doanh_Dong_tien TEXT,
            Criteria_Huong_nha TEXT,
            Criteria_Khoang_cach_duong_oto TEXT,
            latitude TEXT,
            longitude TEXT
        )
        """)
        conn.commit()

        # Di cư tự động (Migration) cho listings_v2
        try:
            cursor.execute("PRAGMA table_info(listings_v2)")
            existing_cols = [row[1] for row in cursor.fetchall()]
            
            if "Chieu_dai" not in existing_cols:
                cursor.execute("ALTER TABLE listings_v2 ADD COLUMN Chieu_dai TEXT")
                conn.commit()
                
            if "pending_diff_json" not in existing_cols:
                cursor.execute("ALTER TABLE listings_v2 ADD COLUMN pending_diff_json TEXT")
                conn.commit()
                
            for col in explicit_criteria_cols:
                if col not in existing_cols:
                    cursor.execute(f"ALTER TABLE listings_v2 ADD COLUMN `{col}` TEXT")
                    conn.commit()

            for col in LISTINGS_V2_COLS:
                new_col = get_safe_col_name(col)
                if new_col not in existing_cols and new_col not in ["tk_id", "status"] and new_col not in explicit_criteria_cols:
                    cursor.execute(f"ALTER TABLE listings_v2 ADD COLUMN `{new_col}` TEXT")
                    conn.commit()
        except Exception:
            pass

        # Di cư tự động (Migration) cho listings_images
        try:
            cursor.execute("PRAGMA table_info(listings_images)")
            existing_img_cols = [row[1] for row in cursor.fetchall()]
            if "origin" not in existing_img_cols:
                cursor.execute("ALTER TABLE listings_images ADD COLUMN origin TEXT DEFAULT 'crawl'")
                conn.commit()
            if "cloudinary_url" in existing_img_cols and "r2_url" not in existing_img_cols:
                cursor.execute("ALTER TABLE listings_images RENAME COLUMN cloudinary_url TO r2_url")
                conn.commit()
        except Exception:
            pass

        # Di cư tự động (Migration) cho listings_custom_v2
        try:
            cursor.execute("PRAGMA table_info(listings_custom_v2)")
            custom_existing_cols = [row[1] for row in cursor.fetchall()]
            custom_cols = [
                "Ma_Khang_Ngo", "Gia_Public", "Tieu_De_Public", "Mo_ta_Public", "Note_Noi_Bo",
                "Trang_Thai_Giao_Dich", "Ngu_Tret", "CHDV", "Trang_Thai_KN", "images_metadata_json",
                "Dia_Chi_That", "So_Nha", "Ten_Duong", "Quan", "Phuong", "Duong", "Ngo_So_nha",
                "bedrooms", "restrooms", "minimumRoadWidth", "Noi_dung_chinh", "Mo_ta_chi_tiet",
                "Gia_chao", "DT_Thuc_te", "DT_Tren_so", "So_Tang", "Mat_Tien", "Chieu_dai", "Huong",
                "Criteria_Duong_truoc_nha", "Criteria_Noi_that", "Criteria_Thang_may", "Criteria_Loai_ngo",
                "Criteria_Khoang_cach_bai_do_xe", "Criteria_Kinh_doanh_Dong_tien", "Criteria_Huong_nha",
                "Criteria_Khoang_cach_duong_oto", "latitude", "longitude"
            ]
            for col in custom_cols:
                if col not in custom_existing_cols:
                    cursor.execute(f"ALTER TABLE listings_custom_v2 ADD COLUMN `{col}` TEXT")
                    conn.commit()
        except Exception:
            pass

    else:
        # Chế độ cũ Pool1
        columns_def = [
            "id INTEGER PRIMARY KEY AUTOINCREMENT",
            "tk_id TEXT UNIQUE",
            "status TEXT DEFAULT 'raw_text'",
            "raw_images_tk_json TEXT",
            "raw_drive_images_json TEXT",
            "curated_config_json TEXT",
            "Chieu_dai TEXT",
            "raw_json_full TEXT",
            "images_mapping_json TEXT",
            "manual_images_json TEXT",
            "raw_sodo_tk_json TEXT",
            "custom_huong TEXT DEFAULT ''",
            "custom_phuong TEXT DEFAULT ''",
            "custom_quan TEXT DEFAULT ''",
            "custom_dt_so TEXT DEFAULT ''",
            "custom_dt_thuc_te TEXT DEFAULT ''"
        ]

        for header in POOL_HEADERS:
            col_name = get_safe_col_name(header)
            columns_def.append(f"`{col_name}` TEXT")
            
        create_table_sql = f"CREATE TABLE IF NOT EXISTS listings ({', '.join(columns_def)})"
        cursor.execute(create_table_sql)
        conn.commit()

        # Bảng listings_images cho Pool1
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tk_id TEXT,
            system_id TEXT,
            image_url TEXT,
            r2_url TEXT,
            role TEXT,
            sequence_index INTEGER,
            edited_by TEXT,
            origin TEXT DEFAULT 'crawl',
            is_hidden INTEGER DEFAULT 0,
            uploaded_at TEXT,
            FOREIGN KEY(tk_id) REFERENCES listings(tk_id) ON DELETE CASCADE
        )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_listings_images_tk_id ON listings_images(tk_id)")
        conn.commit()

        # Di cư tự động (Migration) cho listings Pool1
        try:
            cursor.execute("PRAGMA table_info(listings)")
            existing_cols = [row[1] for row in cursor.fetchall()]
            
            if "Chieu_dai" not in existing_cols:
                cursor.execute("ALTER TABLE listings ADD COLUMN Chieu_dai TEXT")
                conn.commit()
                
            if "raw_json_full" not in existing_cols:
                cursor.execute("ALTER TABLE listings ADD COLUMN raw_json_full TEXT")
                conn.commit()

            if "images_mapping_json" not in existing_cols:
                cursor.execute("ALTER TABLE listings ADD COLUMN images_mapping_json TEXT")
                conn.commit()

            if "manual_images_json" not in existing_cols:
                cursor.execute("ALTER TABLE listings ADD COLUMN manual_images_json TEXT")
                conn.commit()

            if "raw_sodo_tk_json" not in existing_cols:
                cursor.execute("ALTER TABLE listings ADD COLUMN raw_sodo_tk_json TEXT")
                conn.commit()
                
            if "custom_huong" not in existing_cols:
                cursor.execute("ALTER TABLE listings ADD COLUMN custom_huong TEXT DEFAULT ''")
                conn.commit()
                
            if "custom_phuong" not in existing_cols:
                cursor.execute("ALTER TABLE listings ADD COLUMN custom_phuong TEXT DEFAULT ''")
                conn.commit()
                
            if "custom_quan" not in existing_cols:
                cursor.execute("ALTER TABLE listings ADD COLUMN custom_quan TEXT DEFAULT ''")
                conn.commit()
                
            if "custom_dt_so" not in existing_cols:
                cursor.execute("ALTER TABLE listings ADD COLUMN custom_dt_so TEXT DEFAULT ''")
                conn.commit()
                
            if "custom_dt_thuc_te" not in existing_cols:
                cursor.execute("ALTER TABLE listings ADD COLUMN custom_dt_thuc_te TEXT DEFAULT ''")
                conn.commit()

            existing_cols_lower = [c.lower() for c in existing_cols]
            if "images_admin_json" not in existing_cols_lower:
                cursor.execute("ALTER TABLE listings ADD COLUMN images_admin_json TEXT")
                conn.commit()

            if "images_public_json" not in existing_cols_lower:
                cursor.execute("ALTER TABLE listings ADD COLUMN images_public_json TEXT")
                conn.commit()
                
            for header in POOL_HEADERS:
                new_col = get_safe_col_name(header)
                if new_col not in existing_cols and new_col != "Chieu_dai":
                    try:
                        cursor.execute(f"ALTER TABLE listings ADD COLUMN `{new_col}` TEXT")
                        conn.commit()
                    except Exception:
                        pass

            for header in POOL_HEADERS:
                old_col = re.sub(r'[^a-zA-Z0-9_]', '_', header)
                new_col = get_safe_col_name(header)
                if old_col in existing_cols and new_col not in existing_cols and old_col != new_col:
                    try:
                        cursor.execute(f"ALTER TABLE listings RENAME COLUMN `{old_col}` TO `{new_col}`")
                        conn.commit()
                    except Exception:
                        pass
        except Exception:
            pass

    # Luôn khởi tạo crawl_sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crawl_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cookie_sig TEXT,
        start_time TEXT,
        end_time TEXT,
        duration REAL,
        crawled_count INTEGER,
        status TEXT
    )
    """)
    conn.commit()

    # Bảng shared_links để quản lý liên kết gửi khách hàng (US-138)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shared_links (
        link_id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        customer_note TEXT,
        shared_house_ids TEXT NOT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT,
        bound_phone_hash TEXT,
        status TEXT NOT NULL DEFAULT 'Active'
    )
    """)
    
    # Bảng phone_blacklist để chặn số điện thoại khách hàng có vấn đề (US-138)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phone_blacklist (
        raw_phone TEXT,
        phone_hash TEXT PRIMARY KEY,
        blocked_at TEXT NOT NULL,
        reason TEXT,
        status TEXT NOT NULL DEFAULT 'Active'
    )
    """)
    
    # Bảng customer_profiles để lưu ghi chú và trạng thái vòng đời khách hàng (US-140)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_profiles (
        raw_phone TEXT,
        phone_hash TEXT PRIMARY KEY,
        name TEXT,
        note TEXT,
        lifecycle_status TEXT DEFAULT 'LẠNH',
        updated_at TEXT
    )
    """)

    # Bảng exclusion_filters để lưu các tiêu chí loại trừ động của Admin (US-143)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exclusion_filters (
        id TEXT PRIMARY KEY,
        field TEXT NOT NULL,
        operator TEXT NOT NULL,
        value TEXT,
        status TEXT NOT NULL DEFAULT 'Active',
        note TEXT
    )
    """)
    conn.commit()
    conn.close()


def save_raw_to_sqlite(tk_id, metadata, images_tk_list, db_file=None):
    """
    Lưu hoặc cập nhật thông tin chi tiết căn nhà cào thô từ đối tác vào bảng listings SQLite.
    
    Args:
        tk_id (str): Mã căn thô của đối tác.
        metadata (dict): Thông tin chi tiết bóc tách từ DOM.
        images_tk_list (list): Danh sách URLs ảnh gốc từ đối tác.
        db_file (str/None): Tên file database.
        
    Storage:
        Ghi/Cập nhật dòng dữ liệu tương ứng trong bảng listings SQLite.
    """
    if not db_file:
        db_file = get_db_file()
        
    conn = None
    try:
        conn = sqlite3.connect(db_file, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        
        # Xác định pool system đang hoạt động
        is_pool2 = False
        try:
            from core.config import read_settings
            cfg = read_settings()
            if cfg.get("active_pool_system") == "Pool2":
                is_pool2 = True
        except Exception:
            pass
    
        target_table = "listings_v2" if is_pool2 else "listings"
        
        # Lấy danh sách cột thực tế của bảng SQLite mục tiêu để lọc cột động
        cursor.execute(f"PRAGMA table_info({target_table})")
        db_cols = {row[1] for row in cursor.fetchall()}
    
        explicit_criteria_cols = [
            "Criteria_Tiem_nang_Rui_ro", "Criteria_Duong_truoc_nha", "Criteria_Loai_BDS",
            "Criteria_Giay_to_phap_ly", "Criteria_Hinh_dang_dat", "Criteria_Tinh_trang_xay_dung",
            "Criteria_Cau_truc_nha", "Criteria_Noi_that", "Criteria_Thang_may", "Criteria_Loai_ngo",
            "Criteria_Vi_tri_tinh_thue", "Criteria_Mat_thoang", "Criteria_Khoang_cach_bai_do_xe",
            "Criteria_Kinh_doanh_Dong_tien", "Criteria_Tien_ich", "Criteria_Phong_thuy",
            "Criteria_Huong_nha", "Criteria_Vi_tri_trong_ngo", "Criteria_Khoang_cach_duong_oto"
        ]
    
        # Tiền xử lý metadata để đồng bộ chuẩn hóa tên cột
        cleaned_metadata = {}
        
        # Tự động sinh System ID và Mã Hàng nếu chưa có trong metadata
        if is_pool2:
            if "System ID" not in metadata and "system_id" not in metadata and "System_ID" not in metadata:
                metadata["System ID"] = gen_unique_system_id()
            if "Mã Hàng" not in metadata and "ma_hang" not in metadata and "Ma_Hang" not in metadata:
                parts = tk_id.split('-')
                suffix = parts[-1].upper() if parts else ""
                metadata["Mã Hàng"] = f"TK-{suffix}"
    
        for key, val in metadata.items():
            safe_col = key if key in explicit_criteria_cols else get_safe_col_name(key)
            # Chỉ giữ lại những cột thực sự tồn tại trong CSDL mục tiêu
            if safe_col in db_cols and safe_col not in ["tk_id", "status", "raw_images_tk_json", "raw_drive_images_json", "curated_config_json"]:
                cleaned_metadata[safe_col] = clean_sheet_formula_prefix(val)
    
        # Đảm bảo Last_Crawl luôn nằm trong JSON_UI để đồng bộ lên Vercel
        json_ui_str = cleaned_metadata.get("JSON_UI", "")
        if json_ui_str:
            try:
                json_ui_obj = json.loads(json_ui_str)
                if isinstance(json_ui_obj, dict):
                    json_ui_obj["Last_Crawl"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    cleaned_metadata["JSON_UI"] = json.dumps(json_ui_obj, ensure_ascii=False)
            except Exception:
                pass
    
        # Lưu hoặc Cập nhật bảng
        existing = cursor.execute(f"SELECT tk_id FROM {target_table} WHERE tk_id = ?", (tk_id,)).fetchone()
    
        # US-110: Tự động khởi tạo custom_huong bằng Hướng thô nếu chưa có
        if "custom_huong" in db_cols:
            huong_raw = cleaned_metadata.get("Huong") or ""
            if huong_raw:
                is_new = not existing
                db_custom_huong = ""
                if existing:
                    row_ch = cursor.execute(f"SELECT custom_huong FROM {target_table} WHERE tk_id = ?", (tk_id,)).fetchone()
                    if row_ch and row_ch[0]:
                        db_custom_huong = str(row_ch[0]).strip()
                
                if is_new or not db_custom_huong:
                    cleaned_metadata["custom_huong"] = huong_raw
                    
        # US-153: Tự động khởi tạo custom_phuong và custom_quan bằng Phường/Quận thô nếu chưa có
        if "custom_phuong" in db_cols and "custom_quan" in db_cols:
            phuong_raw = cleaned_metadata.get("Phuong") or ""
            quan_raw = cleaned_metadata.get("Quan") or ""
            is_new = not existing
            db_custom_phuong = ""
            db_custom_quan = ""
            if existing:
                row_cpq = cursor.execute(f"SELECT custom_phuong, custom_quan FROM {target_table} WHERE tk_id = ?", (tk_id,)).fetchone()
                if row_cpq:
                    if row_cpq[0]: db_custom_phuong = str(row_cpq[0]).strip()
                    if row_cpq[1]: db_custom_quan = str(row_cpq[1]).strip()
            
            if phuong_raw and (is_new or not db_custom_phuong):
                cleaned_metadata["custom_phuong"] = phuong_raw
            if quan_raw and (is_new or not db_custom_quan):
                cleaned_metadata["custom_quan"] = quan_raw

        # Dò tìm các ảnh sơ đồ (diagram) từ metadata trước để phục vụ phân loại và phân nhóm
        diagram_urls = []
        for idx in range(1, 6):
            sodo_key = f"Sơ đồ thửa đất {idx}"
            if sodo_key in metadata and metadata[sodo_key]:
                url = metadata[sodo_key].strip()
                if url and url not in diagram_urls:
                    diagram_urls.append(url)
    
        # Đọc danh sách ảnh sắp xếp gốc từ TK nếu có
        ordered_urls = metadata.get("raw_images_tk_ordered")
        if isinstance(ordered_urls, str):
            try:
                ordered_urls = json.loads(ordered_urls)
            except Exception:
                pass
    
        # Phân nhóm hình ảnh theo đúng yêu cầu: Nhóm nội thất trước (interior), rồi tới sơ đồ sau (diagram)
        if ordered_urls and isinstance(ordered_urls, list):
            ordered_interiors = [url for url in ordered_urls if url.strip() not in diagram_urls]
            ordered_diagrams = [url for url in ordered_urls if url.strip() in diagram_urls]
            # Đảm bảo không bị thiếu ảnh sơ đồ nào khai báo trong metadata
            for d_url in diagram_urls:
                if d_url not in ordered_diagrams:
                    ordered_diagrams.append(d_url)
            grouped_urls = ordered_interiors + ordered_diagrams
        else:
            # Fallback khi không có ordered_urls
            ordered_interiors = [url for url in images_tk_list if url.strip() not in diagram_urls]
            ordered_diagrams = [url for url in diagram_urls]
            grouped_urls = ordered_interiors + ordered_diagrams
    
        raw_images_tk_json_val = json.dumps(grouped_urls)
        raw_sodo_tk_json_val = json.dumps(ordered_diagrams)
        status_to_update = "raw_text"
        
        # Nhận diện thay đổi và ghi nhận lịch sử vào JSON_UI
        if existing:
            try:
                # Lấy dòng cũ từ SQLite
                db_row = cursor.execute(
                    f"SELECT `Gia_chao`, `Mo_ta_chi_tiet`, `Trang_thai`, `JSON_UI` FROM {target_table} WHERE tk_id = ?",
                    (tk_id,)
                ).fetchone()
                
                if db_row:
                    old_price_str = db_row[0] or ""
                    old_desc_str = db_row[1] or ""
                    old_status_str = db_row[2] or ""
                    old_json_ui_str = db_row[3] or ""
                    
                    # Phân tích JSON_UI cũ để lấy mảng history
                    old_history = []
                    if old_json_ui_str:
                        try:
                            old_json_ui = json.loads(old_json_ui_str)
                            if isinstance(old_json_ui, dict) and "history" in old_json_ui:
                                old_history = old_json_ui["history"]
                                if not isinstance(old_history, list):
                                    old_history = []
                        except Exception:
                            pass
                    
                    # Phân tích dữ liệu mới từ cleaned_metadata
                    new_price_str = cleaned_metadata.get("Gia_chao", "")
                    new_desc_str = cleaned_metadata.get("Mo_ta_chi_tiet", "")
                    new_status_str = cleaned_metadata.get("Trang_thai", "")
                    
                    # Trích xuất ngày cập nhật thực tế của căn từ JSON_UI mới cào
                    updated_at_raw = ""
                    new_json_ui_str = cleaned_metadata.get("JSON_UI", "")
                    if new_json_ui_str:
                        try:
                            new_json_ui_dict = json.loads(new_json_ui_str)
                            updated_at_raw = new_json_ui_dict.get("updatedAt", "")
                        except Exception:
                            pass
                    
                    if not updated_at_raw and existing:
                        try:
                            if old_json_ui_str:
                                old_json_ui_dict = json.loads(old_json_ui_str)
                                updated_at_raw = old_json_ui_dict.get("updatedAt", "")
                        except Exception:
                            pass
    
                    def parse_proptech_date(iso_str):
                        if not iso_str or iso_str == "None":
                            return datetime.now().strftime("%d/%m/%Y")
                        try:
                            s = str(iso_str).replace("Z", "")
                            if "." in s:
                                s = s.split(".")[0]
                            dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
                            return dt.strftime("%d/%m/%Y")
                        except Exception:
                            try:
                                dt = datetime.fromisoformat(iso_str)
                                return dt.strftime("%d/%m/%Y")
                            except Exception:
                                if re.match(r'^\d{2}/\d{2}/\d{4}', str(iso_str)):
                                    return str(iso_str).split(' ')[0]
                                return datetime.now().strftime("%d/%m/%Y")
    
                    hist_date_str = parse_proptech_date(updated_at_raw)
                    new_history_entries = []
                    
                    # 1. Kiểm tra đổi giá
                    try:
                        def parse_price(val_str):
                            if not val_str: return 0.0
                            val_str = str(val_str).replace(",", ".").strip()
                            m = re.search(r'(\d+(?:\.\d+)?)', val_str)
                            return float(m.group(1)) if m else 0.0
                        
                        p_old = parse_price(old_price_str)
                        p_new = parse_price(new_price_str)
                        if p_old > 0 and p_new > 0 and abs(p_old - p_new) > 0.01:
                            new_history_entries.append({
                                "type": "price",
                                "field": "offeringPrice",
                                "old": str(p_old),
                                "new": str(p_new),
                                "date": hist_date_str
                            })
                            print(f"[🔄 Lịch sử Giá] Căn {tk_id}: Giá thay đổi {p_old} tỷ -> {p_new} tỷ")
                    except Exception as e_price_comp:
                        print(f"[⚠️ WARNING] Lỗi so sánh giá lịch sử căn {tk_id}: {str(e_price_comp)}")
                    
                    # 2. Kiểm tra đổi trạng thái
                    if old_status_str and new_status_str and old_status_str.strip() != new_status_str.strip():
                        new_history_entries.append({
                            "type": "status",
                            "field": "status",
                            "old": old_status_str.strip(),
                            "new": new_status_str.strip(),
                            "date": hist_date_str
                        })
                    
                    # 3. Kiểm tra đổi mô tả (chỉ lưu dạng flag thông báo đổi để tránh tràn ô)
                    if old_desc_str and new_desc_str and old_desc_str.strip() != new_desc_str.strip():
                        new_history_entries.append({
                            "type": "info",
                            "field": "description",
                            "old": "Mô tả cũ",
                            "new": "Mô tả mới",
                            "date": hist_date_str
                        })
                    
                    # Nếu có thay đổi mới, trộn vào JSON_UI
                    if new_history_entries or old_history:
                        merged_history = old_history + new_history_entries
                        
                        new_json_ui_str = cleaned_metadata.get("JSON_UI", "")
                        new_json_ui_dict = {}
                        if new_json_ui_str:
                            try:
                                new_json_ui_dict = json.loads(new_json_ui_str)
                            except Exception:
                                pass
                        
                        new_json_ui_dict["history"] = merged_history
                        cleaned_metadata["JSON_UI"] = json.dumps(new_json_ui_dict, ensure_ascii=False)
            except Exception as e_hist:
                print(f"[⚠️ WARNING] Lỗi ghi nhận lịch sử thay đổi căn {tk_id}: {str(e_hist)}")
    
        if existing:
    
            update_parts = ["status = ?", "raw_images_tk_json = ?"]
            values = [status_to_update, raw_images_tk_json_val]
            if "raw_sodo_tk_json" in db_cols:
                update_parts.append("raw_sodo_tk_json = ?")
                values.append(raw_sodo_tk_json_val)
            
            for safe_col, val in cleaned_metadata.items():
                update_parts.append(f"`{safe_col}` = ?")
                values.append(val)
                
            values.append(tk_id)
            update_sql = f"UPDATE {target_table} SET {', '.join(update_parts)} WHERE tk_id = ?"
            cursor.execute(update_sql, values)
        else:
            columns = ["tk_id", "status", "raw_images_tk_json"]
            placeholders = ["?", "?", "?"]
            values = [tk_id, "raw_text", raw_images_tk_json_val]
            if "raw_sodo_tk_json" in db_cols:
                columns.append("raw_sodo_tk_json")
                placeholders.append("?")
                values.append(raw_sodo_tk_json_val)
            
            for safe_col, val in cleaned_metadata.items():
                columns.append(f"`{safe_col}`")
                placeholders.append("?")
                values.append(val)
                
            insert_sql = f"INSERT OR IGNORE INTO {target_table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(insert_sql, values)
            
            # Nếu INSERT OR IGNORE bị bỏ qua (do trùng tk_id từ luồng cào song song),
            # thực hiện UPDATE để đảm bảo dữ liệu mới nhất vẫn được lưu
            if cursor.rowcount == 0:
                update_parts = ["status = ?", "raw_images_tk_json = ?"]
                update_vals = [status_to_update, raw_images_tk_json_val]
                if "raw_sodo_tk_json" in db_cols:
                    update_parts.append("raw_sodo_tk_json = ?")
                    update_vals.append(raw_sodo_tk_json_val)
                for safe_col, val in cleaned_metadata.items():
                    update_parts.append(f"`{safe_col}` = ?")
                    update_vals.append(val)
                update_vals.append(tk_id)
                cursor.execute(f"UPDATE {target_table} SET {', '.join(update_parts)} WHERE tk_id = ?", update_vals)
            
        conn.commit()
    
        # Ở chế độ Pool2, lưu ảnh sơ đồ và ảnh nội thất thô vào listings_images
        if is_pool2:
            # Lấy danh sách ảnh hiện tại trong db để lọc trùng
            existing_images = cursor.execute(
                "SELECT image_url FROM listings_images WHERE tk_id = ?", (tk_id,)
            ).fetchall()
            existing_urls = set(row[0] for row in existing_images)
    
            # Xác định chỉ số thứ tự (sequence_index) tiếp theo
            max_seq_row = cursor.execute(
                "SELECT MAX(sequence_index) FROM listings_images WHERE tk_id = ?", (tk_id,)
            ).fetchone()
            next_seq = (max_seq_row[0] or 0) + 1 if max_seq_row and max_seq_row[0] is not None else 0
    
            # Lưu hình ảnh theo đúng thứ tự đã phân nhóm (nội thất trước, sơ đồ sau)
            for url in grouped_urls:
                url = url.strip()
                if url and url not in existing_urls:
                    role = "diagram" if url in diagram_urls else "interior"
                    cursor.execute("""
                        INSERT INTO listings_images (tk_id, image_url, role, sequence_index)
                        VALUES (?, ?, ?, ?)
                    """, (tk_id, url, role, next_seq))
                    next_seq += 1
                    existing_urls.add(url)
            conn.commit()
    
        # Tự động đánh dấu ảnh bị xóa từ TK
        try:
            # Kiểm tra xem bảng listings_images có tồn tại không
            cursor.execute("SELECT 1 FROM listings_images LIMIT 1")
            
            grouped_urls_set = set(url.strip() for url in grouped_urls if url.strip())
            
            # Lấy các ảnh cào cũ trong db
            cursor.execute(
                "SELECT image_url, r2_url, role FROM listings_images WHERE tk_id = ? AND (origin = 'crawl' OR origin IS NULL OR origin = '')",
                (tk_id,)
            )
            db_crawled_imgs = cursor.fetchall()
            
            has_updates = False
            deleted_urls = set()
            for db_url, r2_url, db_role in db_crawled_imgs:
                if db_url not in grouped_urls_set and db_role != "deleted":
                    cursor.execute(
                        "UPDATE listings_images SET role = 'deleted', is_hidden = 1 WHERE tk_id = ? AND image_url = ?",
                        (tk_id, db_url)
                    )
                    deleted_urls.add(db_url)
                    if r2_url:
                        deleted_urls.add(r2_url)
                    has_updates = True
                    
            if has_updates:
                # Đồng bộ sang curated_config_json trong bảng listings/listings_v2
                row_cur = cursor.execute(f"SELECT curated_config_json FROM {target_table} WHERE tk_id = ?", (tk_id,)).fetchone()
                if row_cur and row_cur[0]:
                    try:
                        curated_data = json.loads(row_cur[0])
                        curated_images = []
                        if isinstance(curated_data, dict):
                            curated_images = curated_data.get("images", [])
                        elif isinstance(curated_data, list):
                            curated_images = curated_data
                            
                        cur_updated = False
                        for img in curated_images:
                            if isinstance(img, dict) and img.get("url"):
                                img_url = img["url"].strip()
                                if img_url in deleted_urls and img.get("role") != "deleted":
                                    img["role"] = "deleted"
                                    img["visible"] = False
                                    cur_updated = True
                                    
                        if cur_updated:
                            new_curated_json = json.dumps(curated_data if isinstance(curated_data, dict) else {"images": curated_images}, ensure_ascii=False)
                            cursor.execute(f"UPDATE {target_table} SET curated_config_json = ? WHERE tk_id = ?", (new_curated_json, tk_id))
                    except Exception:
                        pass
                conn.commit()
        except Exception:
            pass
    
    finally:
        if conn:
            conn.close()


def get_table_end_row_index(sheet_id, creds, add_log_message):
    """
    Truy vấn Google Sheets API lấy chỉ số dòng kết thúc thực tế của Table chính thức trên tab "Pool".
    
    Args:
        sheet_id (str): Spreadsheet ID.
        creds: Credentials xác thực Google Cloud.
        add_log_message (func): Hàm ghi log callback.
        
    Returns:
        int/None: Dòng kết thúc (hoặc None nếu lỗi).
        
    Storage:
        Không lưu đĩa.
    """
    try:
        import requests
        import google.auth.transport.requests
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        token = creds.token
        
        if not token:
            return None
            
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}"
        headers = {"Authorization": f"Bearer {token}"}
        
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            spreadsheet = r.json()
            for sheet in spreadsheet.get('sheets', []):
                properties = sheet.get('properties', {})
                if properties.get('title') == 'Pool' or properties.get('sheetId') == 0:
                    tables = sheet.get('tables', [])
                    for t in tables:
                        range_data = t.get('range', {})
                        end_row = range_data.get('endRowIndex')
                        if end_row is not None:
                            return int(end_row)
    except Exception as e:
        add_log_message(f"[⚠️ WARNING] Không thể lấy Table endRowIndex: {str(e)}")
    return None

def escape_tsv_field(val):
    """
    Chuẩn hóa trường dữ liệu văn bản trước khi đưa vào hàng xuất TSV để copy thủ công.
    
    Args:
        val: Giá trị trường dữ liệu cần chuẩn hóa.
        
    Returns:
        str: Chuỗi văn bản đã được escape an toàn.
        
    Storage:
        RAM (Không lưu đĩa).
    """
    if val is None:
        return ""
    val_str = str(val).strip()
    val_str = val_str.replace("\t", " ")
    if "\n" in val_str or "\r" in val_str or '"' in val_str:
        val_str = val_str.replace('"', '""')
        return f'"{val_str}"'
    return val_str

def publish_listing_pool2(tk_id, get_google_credentials, load_config, add_log_message, db_file=None):
    """
    Đồng bộ dữ liệu chế độ Pool2 lên 3 file Google Sheets độc lập (Raw, Custom, Public).
    """
    with sheets_lock:
        if not db_file:
            db_file = get_db_file()
        
        if not os.path.exists(db_file):
            return {"status": "error", "message": "Database không tồn tại"}
        
        conn = None
        try:
            conn = sqlite3.connect(db_file, timeout=30.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        
            # 1. Đọc dữ liệu thô từ listings_v2
            raw_row = cursor.execute("SELECT * FROM listings_v2 WHERE tk_id = ?", (tk_id,)).fetchone()
            if not raw_row:
                # conn.close() handled by finally
                return {"status": "error", "message": f"Mã căn {tk_id} không tồn tại trong SQLite"}
            
            d_v2 = dict(raw_row)
            system_id = d_v2.get("System_ID")
            if not system_id:
                system_id = gen_unique_system_id()
                cursor.execute("UPDATE listings_v2 SET System_ID = ? WHERE tk_id = ?", (system_id, tk_id))
                conn.commit()
                d_v2["System_ID"] = system_id
            
            # 2. Kiểm tra/Tự khởi tạo dữ liệu Custom
            custom_row = cursor.execute("SELECT * FROM listings_custom_v2 WHERE System_ID = ?", (system_id,)).fetchone()
            if not custom_row:
                add_log_message(f"[ℹ] Tự động tạo dữ liệu Custom mặc định cho System ID {system_id}...")
                # Lọc danh sách ảnh an toàn (loại bỏ facade và diagram)
                cursor.execute(
                    "SELECT image_url, r2_url, role FROM listings_images WHERE tk_id = ? ORDER BY sequence_index ASC", 
                    (tk_id,)
                )
                img_rows = cursor.fetchall()
                safe_images = []
                for img_url, r2_url, role in img_rows:
                    url = r2_url if r2_url else img_url
                    if not url:
                        continue
                    if role not in ["facade", "cover", "diagram", "deleted", "hidden"]:
                        safe_images.append({"url": url, "role": role or "interior"})
                    
                ma_khang_ngo = gen_id_khang_ngo_python(d_v2.get("Ngo_So_nha", ""), d_v2.get("streetName", ""), d_v2.get("Quan", ""))
            
                custom_fields = {
                    "System_ID": system_id,
                    "Ma_Khang_Ngo": ma_khang_ngo,
                    "Gia_Public": d_v2.get("Gia_chao", ""),
                    "Tieu_De_Public": d_v2.get("Noi_dung_chinh", ""),
                    "Mo_ta_Public": d_v2.get("Mo_ta_chi_tiet", ""),
                    "Note_Noi_Bo": "",
                    "Trang_Thai_Giao_Dich": d_v2.get("status_nguon", "Đang bán"),
                    "Ngu_Tret": "N",
                    "CHDV": "N",
                    "Trang_Thai_KN": "Hàng Ngon",
                    "images_metadata_json": json.dumps(safe_images),
                    "Dia_Chi_That": f"{d_v2.get('Ngo_So_nha', '')} {d_v2.get('streetName', '')}, {d_v2.get('Phuong', '')}, {d_v2.get('Quan', '')}",
                    "So_Nha": d_v2.get("Ngo_So_nha", ""),
                    "Ten_Duong": d_v2.get("streetName", ""),
                    "Quan": d_v2.get("Quan", ""),
                    "Phuong": d_v2.get("Phuong", ""),
                    "Duong": d_v2.get("streetName", ""),
                    "Ngo_So_nha": d_v2.get("Ngo_So_nha", ""),
                    "bedrooms": d_v2.get("bedrooms", ""),
                    "restrooms": d_v2.get("restrooms", ""),
                    "minimumRoadWidth": d_v2.get("minimumRoadWidth", ""),
                    "Noi_dung_chinh": d_v2.get("Noi_dung_chinh", ""),
                    "Mo_ta_chi_tiet": d_v2.get("Mo_ta_chi_tiet", ""),
                    "Gia_chao": d_v2.get("Gia_chao", ""),
                    "DT_Thuc_te": d_v2.get("DT_Thuc_te", ""),
                    "DT_Tren_so": d_v2.get("DT_Tren_so", ""),
                    "So_Tang": d_v2.get("So_Tang", ""),
                    "Mat_Tien": d_v2.get("Mat_Tien", ""),
                    "Chieu_dai": d_v2.get("Chieu_dai", ""),
                    "Huong": d_v2.get("Huong", ""),
                    "Criteria_Duong_truoc_nha": d_v2.get("Criteria_Duong_truoc_nha", ""),
                    "Criteria_Noi_that": d_v2.get("Criteria_Noi_that", ""),
                    "Criteria_Thang_may": d_v2.get("Criteria_Thang_may", ""),
                    "Criteria_Loai_ngo": d_v2.get("Criteria_Loai_ngo", ""),
                    "Criteria_Khoang_cach_bai_do_xe": d_v2.get("Criteria_Khoang_cach_bai_do_xe", ""),
                    "Criteria_Kinh_doanh_Dong_tien": d_v2.get("Criteria_Kinh_doanh_Dong_tien", ""),
                    "Criteria_Huong_nha": d_v2.get("Criteria_Huong_nha", ""),
                    "Criteria_Khoang_cach_duong_oto": d_v2.get("Criteria_Khoang_cach_duong_oto", "")
                }
            
                cursor.execute("PRAGMA table_info(listings_custom_v2)")
                custom_db_cols = [r[1] for r in cursor.fetchall()]
                valid_custom_fields = {k: v for k, v in custom_fields.items() if k in custom_db_cols}
            
                cols = list(valid_custom_fields.keys())
                vals = [valid_custom_fields[k] for k in cols]
                placeholders = ", ".join(["?"] * len(cols))
                cursor.execute(
                    f"INSERT INTO listings_custom_v2 ({', '.join([f'`{c}`' for c in cols])}) VALUES ({placeholders})",
                    vals
                )
                conn.commit()
                custom_row = cursor.execute("SELECT * FROM listings_custom_v2 WHERE System_ID = ?", (system_id,)).fetchone()
            
            d_custom = dict(custom_row)
        finally:
            if conn:
                conn.close()
    
        # 3. Lấy cấu hình các Spreadsheet ID
        creds = get_google_credentials()
        cfg = load_config()
        if os.environ.get("STAGING") == "true":
            raw_sheet_id = cfg.get("staging_pool_sheet_id") or cfg.get("pool2_raw_sheet_id")
            custom_sheet_id = cfg.get("staging_source_sheet_id") or cfg.get("pool2_custom_sheet_id")
            public_sheet_id = cfg.get("staging_public_sheet_id") or cfg.get("pool2_public_sheet_id")
        else:
            raw_sheet_id = cfg.get("pool2_raw_sheet_id")
            custom_sheet_id = cfg.get("pool2_custom_sheet_id")
            public_sheet_id = cfg.get("pool2_public_sheet_id")
    
        if not (creds and raw_sheet_id and custom_sheet_id and public_sheet_id):
            add_log_message("[❌ LỖI] Thiếu cấu hình Spreadsheet IDs Pool2 trong settings.json")
            return {"status": "error", "message": "Thiếu Spreadsheet IDs Pool2 trong settings.json"}
        
        import gspread
        client = gspread.authorize(creds)
        client.http_client.session.timeout = 30
    
        # helper lấy chữ cái cột
        def get_col_letter(col_idx):
            return gspread.utils.rowcol_to_a1(1, col_idx).replace("1", "")
        
        # --- ĐỒNG BỘ FILE 1 RAW ---
        try:
            add_log_message(f"[⚡] Đang đồng bộ File 1 Raw (ID: {raw_sheet_id})...")
            raw_spreadsheet = client.open_by_key(raw_sheet_id)
            try:
                raw_sheet = raw_spreadsheet.worksheet("Listings")
            except Exception:
                raw_sheet = raw_spreadsheet.get_worksheet(0)
                raw_sheet.update_title("Listings")
            
            raw_values = raw_sheet.get_all_values()
            if not raw_values:
                raw_headers = RAW_LISTINGS_HEADERS
                raw_sheet.insert_row(raw_headers, index=1, value_input_option='USER_ENTERED')
            else:
                raw_headers = raw_values[0]
                missing = [c for c in RAW_LISTINGS_HEADERS if c not in raw_headers]
                if missing:
                    add_log_message(f"[🛠️ SCHEMA] Bổ sung cột cho File 1 Raw: {missing}")
                    raw_sheet.add_cols(len(missing))
                    for col in missing:
                        raw_headers.append(col)
                    col_letter = get_col_letter(len(raw_headers))
                    raw_sheet.update(range_name=f"A1:{col_letter}1", values=[raw_headers], value_input_option='USER_ENTERED')
                    
            raw_row_data = build_row_data(raw_headers, d_v2)
            tk_id_col = raw_headers.index("tk_id") + 1 if "tk_id" in raw_headers else 1
        
            found_raw_idx = -1
            col_vals = raw_sheet.col_values(tk_id_col)
            col_cleaned = [str(x).strip() for x in col_vals]
            if tk_id.strip() in col_cleaned:
                found_raw_idx = col_cleaned.index(tk_id.strip()) + 1
            
            if found_raw_idx > 0:
                col_letter = get_col_letter(len(raw_headers))
                raw_sheet.update(range_name=f"A{found_raw_idx}:{col_letter}{found_raw_idx}", values=[raw_row_data], value_input_option='USER_ENTERED')
            else:
                insert_idx = max(len(col_cleaned) + 1, 2)
                col_letter = get_col_letter(len(raw_headers))
                raw_sheet.update(range_name=f"A{insert_idx}:{col_letter}{insert_idx}", values=[raw_row_data], value_input_option='USER_ENTERED')
            
        except Exception as e_raw:
            add_log_message(f"[❌ LỖI] Lỗi đồng bộ File 1 Raw: {str(e_raw)}")
            return {"status": "error", "message": f"Lỗi đồng bộ File 1 Raw: {str(e_raw)}"}
        
        # --- ĐỒNG BỘ FILE 2 CUSTOM ---
        try:
            add_log_message(f"[⚡] Đang đồng bộ File 2 Custom (ID: {custom_sheet_id})...")
            custom_spreadsheet = client.open_by_key(custom_sheet_id)
            try:
                custom_sheet = custom_spreadsheet.worksheet("Custom")
            except Exception:
                custom_sheet = custom_spreadsheet.get_worksheet(0)
                custom_sheet.update_title("Custom")
            
            custom_values = custom_sheet.get_all_values()
            if not custom_values:
                custom_headers = CUSTOM_HEADERS
                custom_sheet.insert_row(custom_headers, index=1, value_input_option='USER_ENTERED')
            else:
                custom_headers = custom_values[0]
                missing = [c for c in CUSTOM_HEADERS if c not in custom_headers]
                if missing:
                    add_log_message(f"[🛠️ SCHEMA] Bổ sung cột cho File 2 Custom: {missing}")
                    custom_sheet.add_cols(len(missing))
                    for col in missing:
                        custom_headers.append(col)
                    col_letter = get_col_letter(len(custom_headers))
                    custom_sheet.update(range_name=f"A1:{col_letter}1", values=[custom_headers], value_input_option='USER_ENTERED')
                    
            custom_row_data = build_row_data(custom_headers, d_custom)
            sys_col = custom_headers.index("System_ID") + 1 if "System_ID" in custom_headers else 1
        
            found_cust_idx = -1
            col_vals = custom_sheet.col_values(sys_col)
            col_cleaned = [str(x).strip() for x in col_vals]
            if system_id.strip() in col_cleaned:
                found_cust_idx = col_cleaned.index(system_id.strip()) + 1
            
            if found_cust_idx > 0:
                col_letter = get_col_letter(len(custom_headers))
                custom_sheet.update(range_name=f"A{found_cust_idx}:{col_letter}{found_cust_idx}", values=[custom_row_data], value_input_option='USER_ENTERED')
            else:
                insert_idx = max(len(col_cleaned) + 1, 2)
                col_letter = get_col_letter(len(custom_headers))
                custom_sheet.update(range_name=f"A{insert_idx}:{col_letter}{insert_idx}", values=[custom_row_data], value_input_option='USER_ENTERED')
            
        except Exception as e_custom:
            add_log_message(f"[❌ LỖI] Lỗi đồng bộ File 2 Custom: {str(e_custom)}")
            return {"status": "error", "message": f"Lỗi đồng bộ File 2 Custom: {str(e_custom)}"}
        
        # --- ĐỒNG BỘ FILE 3 PUBLIC ---
        try:
            add_log_message(f"[⚡] Đang đồng bộ File 3 Public (ID: {public_sheet_id})...")
            public_spreadsheet = client.open_by_key(public_sheet_id)
            try:
                public_sheet = public_spreadsheet.worksheet("Public")
            except Exception:
                public_sheet = public_spreadsheet.get_worksheet(0)
                public_sheet.update_title("Public")
            
            public_values = public_sheet.get_all_values()
            if not public_values:
                public_headers = list(PUBLIC_WHITELIST_HEADERS_BASE)
                public_sheet.insert_row(public_headers, index=1, value_input_option='USER_ENTERED')
            else:
                public_headers = public_values[0]
                missing = [c for c in PUBLIC_WHITELIST_HEADERS_BASE if c not in public_headers]
                if missing:
                    add_log_message(f"[🛠️ SCHEMA] Bổ sung cột cơ bản cho File 3 Public: {missing}")
                    if "Last updated" in public_headers:
                        last_updated_idx = public_headers.index("Last updated")
                        public_sheet.insert_cols([[col] for col in missing], col=last_updated_idx + 1)
                        for col in missing:
                            public_headers.insert(last_updated_idx, col)
                            last_updated_idx += 1
                    else:
                        public_sheet.add_cols(len(missing))
                        for col in missing:
                            public_headers.append(col)
                        col_letter = get_col_letter(len(public_headers))
                        public_sheet.update(range_name=f"A1:{col_letter}1", values=[public_headers], value_input_option='USER_ENTERED')
                        
            safe_images = []
            try:
                safe_images = json.loads(d_custom.get("images_metadata_json") or "[]")
            except Exception:
                pass
            
            num_images = len(safe_images)
            required_image_cols = [f"Ảnh {i+1}" for i in range(num_images)]
            missing_image_cols = [c for c in required_image_cols if c not in public_headers]
            if missing_image_cols:
                add_log_message(f"[🛠️ SCHEMA] Thêm {len(missing_image_cols)} cột ảnh ở đuôi sheet Public: {missing_image_cols}")
                public_sheet.add_cols(len(missing_image_cols))
                for col in missing_image_cols:
                    public_headers.append(col)
                col_letter = get_col_letter(len(public_headers))
                public_sheet.update(range_name=f"A1:{col_letter}1", values=[public_headers], value_input_option='USER_ENTERED')
                
            # Chuẩn bị dữ liệu dòng Public
            public_data_dict = {}
            for key in PUBLIC_WHITELIST_HEADERS_BASE:
                if key == "Last updated":
                    public_data_dict[key] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                else:
                    public_data_dict[key] = d_custom.get(key) or ""
                
            for i, img_obj in enumerate(safe_images):
                img_url = img_obj.get("url") if isinstance(img_obj, dict) else str(img_obj)
                public_data_dict[f"Ảnh {i+1}"] = img_url
            
            public_row_data = build_row_data(public_headers, public_data_dict)
            sys_col_pub = public_headers.index("System_ID") + 1 if "System_ID" in public_headers else 1
        
            found_pub_idx = -1
            col_vals = public_sheet.col_values(sys_col_pub)
            col_cleaned = [str(x).strip() for x in col_vals]
            if system_id.strip() in col_cleaned:
                found_pub_idx = col_cleaned.index(system_id.strip()) + 1
            
            if found_pub_idx > 0:
                col_letter = get_col_letter(len(public_headers))
                public_sheet.update(range_name=f"A{found_pub_idx}:{col_letter}{found_pub_idx}", values=[public_row_data], value_input_option='USER_ENTERED')
            else:
                insert_idx = max(len(col_cleaned) + 1, 2)
                col_letter = get_col_letter(len(public_headers))
                public_sheet.update(range_name=f"A{insert_idx}:{col_letter}{insert_idx}", values=[public_row_data], value_input_option='USER_ENTERED')
            
        except Exception as e_pub:
            add_log_message(f"[❌ LỖI] Lỗi đồng bộ File 3 Public: {str(e_pub)}")
            return {"status": "error", "message": f"Lỗi đồng bộ File 3 Public: {str(e_pub)}"}
        
        # --- CẬP NHẬT TRẠNG THÁI DB LOCAL ---
        try:
            conn = sqlite3.connect(db_file, timeout=30.0)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE listings_v2 SET status = 'published', `Last_Sync` = ? WHERE tk_id = ?",
                (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tk_id)
            )
            conn.commit()
            conn.close()
        except Exception as e_db:
            add_log_message(f"[⚠️ WARNING] Lỗi cập nhật SQLite: {str(e_db)}")
        
        add_log_message(f"[✅] ĐÃ ĐỒNG BỘ THÀNH CÔNG CAN {tk_id} SANG 3 FILE GOOGLE SHEETS!")
def append_audit_log_py(spreadsheet, log_sheet_name, row_values, log_event="Update"):
    """
    US-157: Tự động ghi chép (append) một dòng dữ liệu thô sang sheet log tuân thủ Rule 13.
    Dùng biến cấu hình config["data_start_row"], KHÔNG hardcode số 3.
    """
    if not spreadsheet or not log_sheet_name or not row_values:
        return
    try:
        config = GLOBAL_SHEET_CONFIG.get(log_sheet_name, {
            "headers": [],
            "data_start_row": DATA_START_ROW
        })
        
        full_headers = config["headers"]
        data_start_row = config["data_start_row"]
        raw_len = len(full_headers) - 1 if full_headers else len(row_values)

        try:
            log_sheet = spreadsheet.worksheet(log_sheet_name)
        except Exception:
            log_sheet = spreadsheet.add_worksheet(title=log_sheet_name, rows="1000", cols=str(len(full_headers) or 100))
            
        # 1. Đồng bộ Dòng 1 Header bằng range 1:1 (Không hardcode DZ1)
        try:
            row1 = log_sheet.row_values(HEADER_ROW_INDEX)
            if not row1 or (full_headers and (len(row1) < len(full_headers) or row1[0] != full_headers[0])):
                log_sheet.update(range_name="1:1", values=[full_headers], value_input_option="USER_ENTERED")
        except Exception:
            pass
            
        # 2. Padding mảng dữ liệu theo raw_len chuẩn + Log event ở cuối
        log_row = list(row_values)
        while len(log_row) < raw_len:
            log_row.append("")
        log_row = log_row[:raw_len]
        log_row.append(log_event)
        from datetime import datetime
        log_row.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # 3. Phân giải chỉ số dòng tiếp theo BẰNG BIẾN data_start_row
        all_vals = log_sheet.get_all_values()
        next_row = max(len(all_vals) + 1, data_start_row)
        
        # Mở rộng số dòng vật lý nếu bảng đã đầy
        if next_row > log_sheet.row_count:
            log_sheet.add_rows(next_row - log_sheet.row_count + 100)
            
        # 4. Ghi trực tiếp từ Cột A tại dòng next_row đã tính toán
        log_sheet.update(range_name=f"A{next_row}", values=[log_row], value_input_option="USER_ENTERED")
    except Exception as e:
        print(f"[⚠️ WARNING] Không thể ghi audit log sang tab {log_sheet_name}: {str(e)}")

def publish_listing(tk_id, get_google_credentials, load_config, add_log_message, db_file=None):
    """
    Thực hiện đồng bộ xuất bản dữ liệu của một căn nhà từ SQLite local lên Google Sheets trực tuyến.
    Tự động kiểm tra trùng Mã Hàng để chép đè có chọn lọc hoặc chèn dòng mới ở cuối bảng Table.
    Đồng bộ mã ID Khang Ngô mới sang sheet Source và cập nhật trạng thái trong SQLite.
    """
    with sheets_lock:
        if not db_file:
            db_file = get_db_file()
        
        if not os.path.exists(db_file):
            return {"status": "error", "message": "Database không tồn tại"}
        
        # Xác định pool system đang hoạt động
        is_pool2 = False
        try:
            from core.config import read_settings
            cfg = read_settings()
            if cfg.get("active_pool_system") == "Pool2":
                is_pool2 = True
        except Exception:
            pass
        
        if is_pool2:
            return publish_listing_pool2(tk_id, get_google_credentials, load_config, add_log_message, db_file)


        conn = sqlite3.connect(db_file, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        listings_table = "listings_v2" if is_pool2 else "listings"
        if is_pool2:
            sql = """
                SELECT listings_v2.*, 
                       listings_custom_v2.Ma_Khang_Ngo AS custom_Ma_Khang_Ngo, 
                       listings_custom_v2.Gia_Public AS custom_Gia_Public, 
                       listings_custom_v2.Tieu_De_Public AS custom_Tieu_De_Public, 
                       listings_custom_v2.Mo_ta_Public AS custom_Mo_ta_Public, 
                       listings_custom_v2.Note_Noi_Bo AS custom_Note_Noi_Bo, 
                       listings_custom_v2.Trang_Thai_Giao_Dich AS custom_Trang_Thai_Giao_Dich, 
                       listings_custom_v2.Ngu_Tret AS custom_Ngu_Tret, 
                       listings_custom_v2.CHDV AS custom_CHDV, 
                       listings_custom_v2.Trang_Thai_KN AS custom_Trang_Thai_KN, 
                       listings_custom_v2.images_metadata_json AS custom_images_metadata_json, 
                       listings_custom_v2.Dia_Chi_That AS custom_Dia_Chi_That, 
                       listings_custom_v2.So_Nha AS custom_So_Nha, 
                       listings_custom_v2.Ten_Duong AS custom_Ten_Duong,
                       listings_custom_v2.bedrooms AS custom_bedrooms,
                       listings_custom_v2.restrooms AS custom_restrooms,
                       listings_custom_v2.minimumRoadWidth AS custom_minimumRoadWidth,
                       listings_custom_v2.Noi_dung_chinh AS custom_Noi_dung_chinh,
                       listings_custom_v2.Mo_ta_chi_tiet AS custom_Mo_ta_chi_tiet,
                       listings_custom_v2.Gia_chao AS custom_Gia_chao,
                       listings_custom_v2.DT_Thuc_te AS custom_DT_Thuc_te,
                       listings_custom_v2.DT_Tren_so AS custom_DT_Tren_so,
                       listings_custom_v2.So_Tang AS custom_So_Tang,
                       listings_custom_v2.Mat_Tien AS custom_Mat_Tien,
                       listings_custom_v2.Chieu_dai AS custom_Chieu_dai,
                       listings_custom_v2.Huong AS custom_Huong,
                       listings_custom_v2.Criteria_Duong_truoc_nha AS custom_Criteria_Duong_truoc_nha,
                       listings_custom_v2.Criteria_Noi_that AS custom_Criteria_Noi_that,
                       listings_custom_v2.Criteria_Thang_may AS custom_Criteria_Thang_may,
                       listings_custom_v2.Criteria_Loai_ngo AS custom_Criteria_Loai_ngo,
                       listings_custom_v2.Criteria_Khoang_cach_bai_do_xe AS custom_Criteria_Khoang_cach_bai_do_xe,
                       listings_custom_v2.Criteria_Kinh_doanh_Dong_tien AS custom_Criteria_Kinh_doanh_Dong_tien,
                       listings_custom_v2.Criteria_Huong_nha AS custom_Criteria_Huong_nha,
                       listings_custom_v2.Criteria_Khoang_cach_duong_oto AS custom_Criteria_Khoang_cach_duong_oto
                FROM listings_v2 
                LEFT JOIN listings_custom_v2 ON listings_v2.System_ID = listings_custom_v2.System_ID
                WHERE listings_v2.tk_id = ?
            """
            row = cursor.execute(sql, (tk_id,)).fetchone()
        else:
            row = cursor.execute(f"SELECT * FROM {listings_table} WHERE tk_id = ?", (tk_id,)).fetchone()
    
        if not row:
            conn.close()
            return {"status": "error", "message": "Mã căn không tồn tại"}
        
        d = dict(row)
    
        # Phân rã curated_config_json và dàn phẳng động cho Pool1
        if not is_pool2:
            curated_json = d.get("curated_config_json")
            if curated_json:
                try:
                    curated_data = json.loads(curated_json)
                except Exception:
                    curated_data = None
                
                if curated_data:
                    images_list = []
                    if isinstance(curated_data, dict):
                        images_list = curated_data.get("images", [])
                    elif isinstance(curated_data, list):
                        images_list = curated_data
                
                    filtered_images = []
                    for img in images_list:
                        if not isinstance(img, dict):
                            continue
                        role = img.get("role")
                        is_hidden = role in ["Ẩn", "hidden", "deleted"]
                        if is_hidden:
                            continue
                        filtered_images.append(img)
                
                    diagrams = []
                    facades = []
                    covers = []
                    alleys = []
                    interiors = []
                
                    for img in filtered_images:
                        url = img.get("url")
                        role = img.get("role")
                        if not url:
                            continue
                        if role == "Sơ đồ":
                            diagrams.append(url)
                        elif role == "Mặt tiền":
                            facades.append(url)
                        elif role == "Bìa":
                            covers.append(url)
                        elif role == "Hẻm":
                            alleys.append(url)
                        elif role == "Nội thất":
                            interiors.append(url)
                        else:
                            interiors.append(url)
                
                    cover_url = ""
                    if covers:
                        cover_url = covers[0]
                    elif facades:
                        cover_url = facades[0]
                    elif interiors:
                        cover_url = interiors[0]
                    d[get_safe_col_name("Hình Nhận Diện")] = cover_url
                
                    d[get_safe_col_name("Hình Mặt Tiền")] = facades[0] if facades else ""
                
                    for idx in range(5):
                        col_name = get_safe_col_name(f"Sơ đồ thửa đất {idx+1}")
                        d[col_name] = diagrams[idx] if idx < len(diagrams) else ""
                    
                    for idx in range(10):
                        col_name = get_safe_col_name(f"Hình Hẻm {idx+1}")
                        d[col_name] = alleys[idx] if idx < len(alleys) else ""
                    
                    for idx in range(25):
                        col_name = get_safe_col_name(f"Ảnh {idx+1}")
                        d[col_name] = interiors[idx] if idx < len(interiors) else ""

        if is_pool2:
            try:
                # Fetch images from listings_images since listings_v2 has no image columns
                cursor.execute(
                    "SELECT image_url, r2_url, role, sequence_index FROM listings_images WHERE tk_id = ? ORDER BY sequence_index ASC", 
                    (tk_id,)
                )
                img_rows = cursor.fetchall()
            
                diagrams = []
                facades = []
                alleys = []
                interiors = []
                for img_url, r2_url, role, seq in img_rows:
                    url = r2_url if r2_url else img_url
                    if not url:
                        continue
                    if role in ["diagram", "sodo"]:
                        diagrams.append(url)
                    elif role in ["facade", "cover"]:
                        facades.append(url)
                    elif role == "alley":
                        alleys.append(url)
                    elif role == "interior":
                        interiors.append(url)
            
                # Map them into safe column name keys
                for idx in range(5):
                    d[get_safe_col_name(f"Sơ đồ thửa đất {idx+1}")] = diagrams[idx] if idx < len(diagrams) else ""
                d[get_safe_col_name("Hình Mặt Tiền")] = facades[0] if facades else (interiors[0] if interiors else "")
                for idx in range(10):
                    d[get_safe_col_name(f"Hình Hẻm {idx+1}")] = alleys[idx] if idx < len(alleys) else ""
                for idx in range(25):
                    d[get_safe_col_name(f"Ảnh {idx+1}")] = interiors[idx] if idx < len(interiors) else ""
            except Exception as e_img_fetch:
                add_log_message(f"[⚠️ WARNING] Không thể truy vấn ảnh từ listings_images cho publish: {str(e_img_fetch)}")
        if is_pool2 and "custom_Ma_Khang_Ngo" in d:
            if d.get("custom_Ma_Khang_Ngo"): d["Ma_Khang_Ngo_ID"] = d["custom_Ma_Khang_Ngo"]
            if d.get("custom_Tieu_De_Public"): d["Tieu_de_Public"] = d["custom_Tieu_De_Public"]
            if d.get("custom_Mo_ta_Public"): d["Mo_ta_Public"] = d["custom_Mo_ta_Public"]
            if d.get("custom_Gia_Public"): d["Gia_Public"] = d["custom_Gia_Public"]
            if d.get("custom_Note_Noi_Bo"): d["Note_Noi_Bo"] = d["custom_Note_Noi_Bo"]
            if d.get("custom_Trang_Thai_Giao_Dich"): d["Tinh_trang_nha"] = d["custom_Trang_Thai_Giao_Dich"]
            if d.get("custom_Ngu_Tret"): d["Ngu_tret_Admin"] = d["custom_Ngu_Tret"]
            if d.get("custom_CHDV"): d["CHDV_Admin"] = d["custom_CHDV"]
            if d.get("custom_Trang_Thai_KN"): d["Danh_gia_Admin"] = d["custom_Trang_Thai_KN"]
        
            # Nhóm đè địa chỉ / kỹ thuật
            if d.get("custom_So_Nha"): d["Ngo_So_nha"] = d["custom_So_Nha"]
            if d.get("custom_Ten_Duong"): d["Duong"] = d["custom_Ten_Duong"]
            if d.get("custom_Quan"): d["Quan"] = d["custom_Quan"]
            if d.get("custom_Phuong"): d["Phuong"] = d["custom_Phuong"]
            if d.get("custom_bedrooms"): d["bedrooms"] = d["custom_bedrooms"]
            if d.get("custom_restrooms"): d["restrooms"] = d["custom_restrooms"]
            if d.get("custom_minimumRoadWidth"): d["minimumRoadWidth"] = d["custom_minimumRoadWidth"]
            if d.get("custom_Noi_dung_chinh"): d["Noi_dung_chinh"] = d["custom_Noi_dung_chinh"]
            if d.get("custom_Mo_ta_chi_tiet"): d["Mo_ta_chi_tiet"] = d["custom_Mo_ta_chi_tiet"]
            if d.get("custom_Gia_chao"): d["Gia_chao"] = d["custom_Gia_chao"]
            if d.get("custom_DT_Thuc_te"): d["DT_Thuc_te"] = d["custom_DT_Thuc_te"]
            if d.get("custom_DT_Tren_so"): d["DT_Tren_so"] = d["custom_DT_Tren_so"]
            if d.get("custom_So_Tang"): d["So_Tang"] = d["custom_So_Tang"]
            if d.get("custom_Mat_Tien"): d["Mat_Tien"] = d["custom_Mat_Tien"]
            if d.get("custom_Chieu_dai"): d["Chieu_dai"] = d["custom_Chieu_dai"]
            huong_val = d.get("custom_huong") or d.get("custom_Huong")
            if huong_val: d["Huong"] = huong_val
            phuong_val = d.get("custom_phuong")
            if phuong_val: d["Phuong"] = phuong_val
            quan_val = d.get("custom_quan")
            if quan_val: d["Quan"] = quan_val
    
        # Khử va chạm Mã Hàng
        ma_hang_db = d.get("M__H_ng", "") or d.get("Ma_Hang", "")
        if ma_hang_db:
            collision_count = cursor.execute(
                f"SELECT COUNT(DISTINCT tk_id) FROM {listings_table} WHERE Ma_Hang = ?",
                (ma_hang_db,)
            ).fetchone()[0]
            if collision_count > 1:
                parts = tk_id.split('-')
                suffix = parts[-1].upper() if parts else ""
                target_ma_hang = f"TK-{suffix}"
                add_log_message(f"[🛡️ COLLISION RESOLUTION] Phát hiện mã hàng gốc '{ma_hang_db}' bị trùng lặp trong SQLite. Tự động chuyển đổi thành mã hàng 8 ký tự độc nhất: '{target_ma_hang}'")
            else:
                target_ma_hang = ma_hang_db
        else:
            parts = tk_id.split('-')
            suffix = parts[-1].upper() if parts else ""
            target_ma_hang = f"TK-{suffix}"
        
        conn.close()
    
        creds = get_google_credentials()
        cfg = load_config()
        if os.environ.get("STAGING") == "true":
            sheet_id = cfg.get("staging_pool_sheet_id") or cfg.get("sheet_id")
        else:
            sheet_id = cfg.get("sheet_id")
    
        next_row = 3
        sheet = None
        existing_row_index = None
    
        if creds and sheet_id:
            try:
                import gspread
                client = gspread.authorize(creds)
                client.http_client.session.timeout = 30
                spreadsheet = client.open_by_key(sheet_id)
            
                try:
                    sheet = spreadsheet.worksheet("Pool")
                except Exception as e:
                    # Throw a clear exception if 'Pool' worksheet is missing, preventing dangerous write fallbacks to 'Source'
                    raise Exception(
                        f"Không tìm thấy tab 'Pool' trong Google Sheet '{spreadsheet.title}' (ID: {sheet_id}). "
                        f"Vui lòng kiểm tra lại cấu hình ID Google Sheets hoặc cấu trúc các tab."
                    )
                    
                try:
                    col_a_values = sheet.col_values(1)
                    col_a_cleaned = [str(x).strip() for x in col_a_values]
                    target_stripped = target_ma_hang.strip()
                    if target_stripped in col_a_cleaned:
                        existing_row_index = col_a_cleaned.index(target_stripped) + 1
                        add_log_message(f"[ℹ] Phát hiện Mã Hàng {target_stripped} đã tồn tại ở dòng {existing_row_index} trong Sheets. Kích hoạt chế độ CẬP NHẬT CHÉP ĐÈ chỉ dành riêng cho HÌNH ẢNH và LAST CRAWL.")
                except Exception as e:
                    add_log_message(f"[⚠️ WARNING] Không thể kiểm tra trùng Mã Hàng trong Sheets: {str(e)}")

                if existing_row_index:
                    next_row = existing_row_index
                else:
                    table_end_row = get_table_end_row_index(sheet_id, creds, add_log_message)
                    if table_end_row:
                        next_row = table_end_row + 1
                        add_log_message(f"[ℹ] Phát hiện Table chính thức kết thúc ở dòng {table_end_row}. Thực hiện chèn tại dòng {next_row} (cuối bảng) để thêm dòng mới vào cuối.")
                    else:
                        try:
                            next_row = max(len(sheet.get_all_values()) + 1, GLOBAL_SHEET_CONFIG["Pool"]["data_start_row"])
                        except Exception as e:
                            add_log_message(f"[⚠️ WARNING] Không lấy được số dòng hiện tại của Sheet, fallback về mặc định: {str(e)}")
                            next_row = GLOBAL_SHEET_CONFIG["Pool"]["data_start_row"]
            except Exception as e:
                add_log_message(f"[❌ LỖI] Lỗi kết nối API Google Sheets: {str(e)}")
            
        row_data = []
        row_data_escaped = []
    
        if existing_row_index and sheet:
            try:
                existing_row = sheet.row_values(existing_row_index)
            except Exception as e:
                add_log_message(f"[❌ LỖI] Lỗi khi đọc dữ liệu cũ của dòng {existing_row_index}: {str(e)}")
                existing_row = []
            
            updated_row = list(existing_row)
            while len(updated_row) < len(POOL_HEADERS):
                updated_row.append("")
            
            PROTECTED_HEADERS = {
                "Mã Hàng", "System ID", "Mã Khang Ngô (ID)",
                "Hình Nhận Diện", "Hình Mặt Tiền",
                "Ảnh 1", "Ảnh 2", "Ảnh 3", "Ảnh 4", "Ảnh 5", "Ảnh 6", "Ảnh 7", "Ảnh 8",
                "Ảnh 9", "Ảnh 10", "Ảnh 11", "Ảnh 12", "Ảnh 13", "Ảnh 14", "Ảnh 15",
                "Ảnh 16", "Ảnh 17", "Ảnh 18", "Ảnh 19", "Ảnh 20",
                "Ảnh 21", "Ảnh 22", "Ảnh 23", "Ảnh 24", "Ảnh 25",
                "Tiêu đề Public", "Mô tả Public", "Giá Public",
                "Phân loại Hẻm", "Đường trước nhà (m)", "Tình trạng nhà",
                "Ảnh Public (VD: 1,3,5)", "Ảnh Hẻm Public (VD: 1,2)",
                "Phường cũ (AI)", "Đánh giá (Admin)", "Ngủ trệt (Admin)",
                "CHDV (Admin)", "Duyệt Public", "Trạng thái Public"
            }
        
            for idx, header in enumerate(POOL_HEADERS):
                # Bảo vệ cột nếu nằm trong danh sách PROTECTED_HEADERS hoặc tên cột chứa chữ "custom" (không phân biệt hoa thường)
                if header in PROTECTED_HEADERS or "custom" in header.lower():
                    is_image_col = (header in ["Hình Nhận Diện", "Hình Mặt Tiền"] or "Ảnh " in header or "Sơ đồ thửa đất " in header or "Hình Hẻm " in header)
                    old_val = existing_row[idx] if idx < len(existing_row) else ""
                    safe_col = get_safe_col_name(header)
                    sqlite_val = d.get(safe_col, "")
                    
                    # Kiểm tra xem link cũ trên Sheets có phải là link R2 của căn khác hay không
                    is_mismatched_r2 = False
                    old_val_str = str(old_val).strip()
                    if is_image_col and old_val_str and (".r2.dev" in old_val_str or "r2.cloudflarestorage.com" in old_val_str):
                        # Nếu URL R2 cũ không chứa tk_id hiện tại của listing, đây là ảnh của căn khác
                        if tk_id not in old_val_str:
                            is_mismatched_r2 = True
                            
                    is_r2_url = (".r2.dev" in str(sqlite_val) or "r2.cloudflarestorage.com" in str(sqlite_val) or "cloudinary.com" in str(sqlite_val))
                    if is_image_col and (not old_val_str or is_r2_url or is_mismatched_r2):
                        val = sqlite_val
                    else:
                        val = old_val

                else:
                    safe_col = get_safe_col_name(header)
                    val = d.get(safe_col, "")
                    
                    # Các xử lý ghi đè đặc trưng
                    if header == "Last Crawl":
                        val = d.get("Last_Crawl", "") or datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    elif header == "Last Sync":
                        val = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    elif header == "Tên đầu chủ (BX)":
                        val = d.get("Ten_Dau_Chu_Hop_dong", "")
                
                val_str = str(val) if val is not None else ""
                updated_row[idx] = val_str
                
            row_data = updated_row
            row_data_escaped = [escape_tsv_field(str(x)) for x in row_data]
        else:
            for header in POOL_HEADERS:
                safe_col = get_safe_col_name(header)
                val = d.get(safe_col, "")
            
                if header == "Mã Hàng":
                    val = target_ma_hang
                elif header == "Hình Nhận Diện":
                    val = f"=IMAGE(AD{next_row})"
                elif header == "Mã Khang Ngô (ID)" and not val:
                    so_nha = d.get("Ngo_So_nha", "") or d.get("Ng__S__nh_", "")
                    duong = d.get("Duong", "") or d.get("___ng", "")
                    quan = d.get("Quan", "") or d.get("Qu_n", "")
                    val = gen_id_khang_ngo_python(so_nha, duong, quan)
                    d["Ma_Khang_Ngo_ID"] = val
                    try:
                        conn_db = sqlite3.connect(db_file, timeout=30.0)
                        cursor_db = conn_db.cursor()
                        col_ma_kn_safe = get_safe_col_name("Mã Khang Ngô (ID)")
                        cursor_db.execute(f"UPDATE {listings_table} SET `{col_ma_kn_safe}` = ? WHERE tk_id = ?", (val, tk_id))
                        conn_db.commit()
                        conn_db.close()
                    except Exception as e_db:
                        add_log_message(f"[⚠️ WARNING] Không thể lưu Mã Khang Ngô mới vào SQLite: {str(e_db)}")
                elif header in ["Tiêu đề Public", "Mô tả Public", "Last Sync"]:
                    val = ""
                elif header == "Tên đầu chủ (BX)":
                    val = d.get("Ten_Dau_Chu_Hop_dong", "")
                elif header == "System ID" and not val:
                    val = gen_unique_system_id()
                    d["System_ID"] = val
                    try:
                        conn_db = sqlite3.connect(db_file, timeout=30.0)
                        cursor_db = conn_db.cursor()
                        col_sys_safe = get_safe_col_name("System ID")
                        cursor_db.execute(f"UPDATE {listings_table} SET `{col_sys_safe}` = ? WHERE tk_id = ?", (val, tk_id))
                        conn_db.commit()
                        conn_db.close()
                    except Exception as e_db:
                        add_log_message(f"[⚠️ WARNING] Không thể lưu System ID mới vào SQLite: {str(e_db)}")
                
                val_str = str(val) if val is not None else ""
                row_data.append(escape_sheets_value(val_str))
                row_data_escaped.append(escape_tsv_field(val_str))
        
        if sheet:
            try:
                if existing_row_index:
                    add_log_message(f"[⚡] Đang chép đè dòng dữ liệu lên Sheet '{sheet.title}' (dòng {existing_row_index})...")
                    sheet.update(range_name=f"A{existing_row_index}:DZ{existing_row_index}", values=[row_data], value_input_option='USER_ENTERED')
                    try:
                        append_audit_log_py(spreadsheet, "Pool_Log", row_data, log_event="Update")
                    except Exception as e_plog:
                        add_log_message(f"[⚠️ WARNING] Không thể ghi Pool_Log: {str(e_plog)}")
                else:
                    add_log_message(f"[⚡] Đang chèn chốt dòng mới lên Sheet '{sheet.title}' (dòng {next_row} - chèn để thừa hưởng định dạng bảng)...")
                    sheet.insert_row(row_data, index=next_row, value_input_option='USER_ENTERED', inherit_from_before=True)
                    try:
                        append_audit_log_py(spreadsheet, "Pool_Log", row_data, log_event="New")
                    except Exception as e_plog:
                        add_log_message(f"[⚠️ WARNING] Không thể ghi Pool_Log: {str(e_plog)}")
            
                try:
                    raw_imgs = []
                    images_admin_json_str = d.get("images_admin_json") or d.get("Images_Admin_JSON")
                    if images_admin_json_str:
                        try:
                            parsed = json.loads(images_admin_json_str)
                            if isinstance(parsed, list):
                                for img in parsed:
                                    if isinstance(img, dict) and img.get("role") != "deleted":
                                        url = img.get("r2_url") or img.get("image_url") or ""
                                        if url.strip():
                                            import re
                                            origin = img.get("origin")
                                            is_self = False
                                            if origin:
                                                is_self = origin in ["self", "user"]
                                            else:
                                                filename = url.split("/")[-1]
                                                is_self = (
                                                    filename.startswith("SYS-") or
                                                    bool(re.search(r'_(interior|sodo|facade|alley|cover)_\d{13}', filename)) or
                                                    ("BDS-KhangNgo/" in url and not bool(re.search(r'img_[a-f0-9-]{36}_\d+', filename)))
                                                )
                                            if not is_self:
                                                raw_imgs.append(url.strip())
                        except Exception:
                            pass
                    if not raw_imgs and d.get("raw_drive_images_json"):
                        try:
                            raw_imgs = json.loads(d.get("raw_drive_images_json"))
                        except Exception:
                            pass
                    if not raw_imgs and d.get("raw_images_tk_json"):
                        try:
                            raw_imgs = json.loads(d.get("raw_images_tk_json"))
                        except Exception:
                            pass
                    
                    # Ngõ/Số nhà ở index 6, Đường ở index 5
                    address_str = ""
                    if len(row_data) > 6:
                        address_str = f"{row_data[6]} {row_data[5]}".strip()
                    
                    # Trích xuất ảnh tự up (self)
                    self_imgs = []
                    admin_json_str = d.get("Images_Admin_JSON")
                    if admin_json_str:
                        try:
                            admin_imgs = json.loads(admin_json_str)
                            self_imgs = [
                                img.get("r2_url") or img.get("image_url")
                                for img in admin_imgs
                                if img.get("origin") in ["self", "user"]
                            ]
                            self_imgs = [x for x in self_imgs if x]
                        except Exception:
                            pass
                    init_pool_images_rows(spreadsheet, tk_id, address_str, raw_imgs)
                    update_pool_images_crawl_row(spreadsheet, tk_id, address_str, raw_imgs)
                    if self_imgs:
                        update_pool_images_self_row(spreadsheet, tk_id, address_str, self_imgs)
                except Exception as e_backup:
                    add_log_message(f"[⚠️ WARNING] Không thể xử lý backup trên Pool_Images: {str(e_backup)}")

                if os.environ.get("STAGING") == "true":
                    source_sheet_id = cfg.get("staging_source_sheet_id") or "1ljauQNEPA-8wM0vlJDRQkWjT2KQUwdR8tcq0r69dikk"
                else:
                    source_sheet_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
                try:
                    source_spreadsheet = client.open_by_key(source_sheet_id)
                    source_sheet = source_spreadsheet.worksheet("Source")
                    source_values = source_sheet.get_all_values()
                
                    system_id = d.get("System_ID", "")
                    if system_id and source_values:
                        # 1. Tìm dòng header động trên sheet Source
                        header_row_idx = -1
                        for idx, row in enumerate(source_values):
                            if "System_ID" in row or "id" in row or "Cu_phap" in row or "System ID" in row:
                                header_row_idx = idx
                                break
                        
                        if header_row_idx == -1:
                            header_row_idx = 0 # Fallback dòng 1
                        
                        headers = source_values[header_row_idx]
                        
                        # 2. Tìm index các cột động
                        sys_id_col_idx = -1
                        if "System_ID" in headers:
                            sys_id_col_idx = headers.index("System_ID")
                        elif "System ID" in headers:
                            sys_id_col_idx = headers.index("System ID")
                            
                        id_col_idx = -1
                        if "id" in headers:
                            id_col_idx = headers.index("id")
                            
                        if sys_id_col_idx == -1:
                            sys_id_col_idx = 37 # Fallback cột AL (38)
                        if id_col_idx == -1:
                            id_col_idx = 3 # Fallback cột D (4)
                            
                        # 3. Quét tìm dòng trùng khớp bắt đầu từ dòng dữ liệu thực tế (Dòng 3+)
                        found_source_row_idx = -1
                        start_data_idx = GLOBAL_SHEET_CONFIG["Source"]["data_start_row"] - 1
                        for s_idx in range(start_data_idx, len(source_values)):
                            s_row = source_values[s_idx]
                            if len(s_row) > sys_id_col_idx and s_row[sys_id_col_idx].strip() == system_id:
                                found_source_row_idx = s_idx + 1 # 1-indexed for Sheets
                                break
                    
                        if found_source_row_idx > -1:
                            new_ma_kn = d.get("Ma_Khang_Ngo_ID", "")
                            if new_ma_kn:
                                add_log_message(f"[⚡] Đồng bộ Mã Khang Ngô '{new_ma_kn}' sang cột id của sheet Source (dòng {found_source_row_idx})...")
                                source_sheet.update_cell(found_source_row_idx, id_col_idx + 1, new_ma_kn)
                                try:
                                    # Lấy dòng đã cập nhật và ghi log
                                    s_row_updated = source_sheet.row_values(found_source_row_idx)
                                    append_audit_log_py(source_spreadsheet, "Source_Log", s_row_updated, log_event="Update")
                                except Exception as e_slog:
                                    add_log_message(f"[⚠️ WARNING] Không thể ghi Source_Log: {str(e_slog)}")
                except Exception as e_source:
                    add_log_message(f"[⚠️ WARNING] Không thể tự động đồng bộ Mã Khang Ngô sang sheet Source: {str(e_source)}")
            
                conn = sqlite3.connect(db_file, timeout=30.0)
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE {listings_table} SET status = 'published', `Last_Sync` = ? WHERE tk_id = ?",
                    (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), tk_id)
                )
                conn.commit()
                conn.close()
            
                add_log_message(f"[✅] ĐÃ XUẤT BẢN THÀNH CÔNG lên Google Sheets căn {tk_id}!")
                return {
                    "status": "success",
                    "published_to_cloud": True,
                    "message": "Đã xuất bản thành công trực tiếp lên Google Sheets!",
                    "row_data": row_data_escaped
                }
            
            except Exception as e:
                add_log_message(f"[❌ LỖI] Lỗi ghi dữ liệu lên Google Sheets: {str(e)}")
                return {
                    "status": "warning",
                    "published_to_cloud": False,
                    "message": f"Lỗi Google API: {str(e)}. Tuy nhiên dữ liệu 79 cột đã được chuẩn bị bên dưới để bạn sao chép thủ công!",
                    "row_data": row_data_escaped
                }
        else:
            add_log_message("[⚠️ COPIED] Google Sheets credentials không được tìm thấy hoặc lỗi kết nối. Bạn có thể sao chép dòng dữ liệu bên dưới.")
            return {
                "status": "warning",
                "published_to_cloud": False,
                "message": "Chưa cấu hình hoặc lỗi kết nối Google Sheets. Vui lòng sao chép mảng dữ liệu 79 cột bên dưới để paste thủ công vào Google Sheets!",
                "row_data": row_data_escaped
            }


# ==================================================
# US-089C: CROSS-POOL SYNC & RECRAWL DIFF TRACKING
# ==================================================

def normalize_address(so_nha, duong):
    """
    Chuẩn hóa số nhà và tên đường phục vụ so khớp địa chỉ giữa hai Pool.
    
    ⚠️ DELEGATED: Logic đã chuyển sang core.business_rules.normalize_address()
    """
    from core.business_rules import normalize_address as _normalize_address
    return _normalize_address(so_nha, duong)

def get_flattened_images_pool2(cursor, tk_id):
    """
    Lấy hình ảnh từ Pool 2, phân loại và làm phẳng thành các cột tương thích với Pool 1.
    """
    cursor.execute(
        "SELECT image_url, r2_url, role FROM listings_images WHERE tk_id = ? ORDER BY sequence_index ASC",
        (tk_id,)
    )
    img_rows = cursor.fetchall()
    diagrams = []
    facades = []
    alleys = []
    interiors = []
    for img_url, r2_url, role in img_rows:
        url = r2_url if r2_url else img_url
        if not url:
            continue
        if role == "diagram":
            diagrams.append(url)
        elif role in ["facade", "cover"]:
            facades.append(url)
        elif role == "alley":
            alleys.append(url)
        elif role == "interior":
            interiors.append(url)
            
    hinh_mat_tien = facades[0] if facades else (interiors[0] if interiors else "")
    
    flat = {}
    for i in range(1, 6):
        flat[get_safe_col_name(f"Sơ đồ thửa đất {i}")] = diagrams[i-1] if i-1 < len(diagrams) else ""
    flat[get_safe_col_name("Hình Mặt Tiền")] = hinh_mat_tien
    for i in range(1, 11):
        flat[get_safe_col_name(f"Hình Hẻm {i}")] = alleys[i-1] if i-1 < len(alleys) else ""
    for i in range(1, 26):
        flat[get_safe_col_name(f"Ảnh {i}")] = interiors[i-1] if i-1 < len(interiors) else ""
        
    return flat

def sync_between_databases(source_pool, target_pool, tk_id=None, so_nha=None, duong=None, add_log_message=None):
    """
    Điều phối đồng bộ chéo giữa Pool 1 (raw_archive.db) và Pool 2 (raw_archive_v2.db).
    """
    if add_log_message is None:
        def add_log_message(msg):
            print(msg)
            
    def get_db_path(name):
        if not name:
            return None
        if name == "Pool1":
            return "raw_archive.db"
        if name == "Pool2":
            return "raw_archive_v2.db"
        return name
        
    src_db = get_db_path(source_pool)
    tgt_db = get_db_path(target_pool)
    
    if not src_db or not tgt_db:
        return {"status": "error", "message": "Thiếu thông tin database nguồn hoặc đích."}
        
    if not os.path.exists(src_db):
        return {"status": "error", "message": f"Database nguồn {src_db} không tồn tại."}
        
    init_db(tgt_db)
    
    is_p2_to_p1 = ("raw_archive_v2.db" in src_db) and ("raw_archive.db" in tgt_db)
    is_p1_to_p2 = ("raw_archive.db" in src_db) and ("raw_archive_v2.db" in tgt_db)
    
    if is_p2_to_p1:
        return sync_p2_to_p1(src_db, tgt_db, tk_id, add_log_message)
    elif is_p1_to_p2:
        if not so_nha or not duong:
            return {"status": "error", "message": "Đồng bộ từ Pool1 sang Pool2 yêu cầu cung cấp số nhà và tên đường."}
        return sync_p1_to_p2(src_db, tgt_db, so_nha, duong, add_log_message)
    else:
        return {"status": "error", "message": "Hướng đồng bộ không hợp lệ hoặc chưa được hỗ trợ."}

def sync_p2_to_p1(src_db, tgt_db, tk_id, add_log_message):
    add_log_message(f"[⚡] Bắt đầu đồng bộ xuôi từ Pool 2 ({src_db}) sang Pool 1 ({tgt_db})...")
    
    s_conn = None
    t_conn = None
    try:
        s_conn = sqlite3.connect(src_db)
        s_conn.row_factory = sqlite3.Row
        s_cursor = s_conn.cursor()
    
        t_conn = sqlite3.connect(tgt_db)
        t_conn.row_factory = sqlite3.Row
        t_cursor = t_conn.cursor()
        
        # Get target columns of listings table in Pool 1
        t_cursor.execute("PRAGMA table_info(listings)")
        t_cols = [row[1] for row in t_cursor.fetchall() if row[1] != 'id']
        
        # Query source listings
        if tk_id:
            s_cursor.execute("""
                SELECT l.*, c.Ma_Khang_Ngo AS custom_Ma_Khang_Ngo, c.Gia_Public AS custom_Gia_Public,
                       c.Tieu_De_Public AS custom_Tieu_De_Public, c.Mo_ta_Public AS custom_Mo_ta_Public,
                       c.Note_Noi_Bo AS custom_Note_Noi_Bo, c.Trang_Thai_Giao_Dich AS custom_Trang_Thai_Giao_Dich,
                       c.Ngu_Tret AS custom_Ngu_Tret, c.CHDV AS custom_CHDV, c.Trang_Thai_KN AS custom_Trang_Thai_KN,
                       c.images_metadata_json AS custom_images_metadata_json, c.Dia_Chi_That AS custom_Dia_Chi_That,
                       c.So_Nha AS custom_So_Nha, c.Ten_Duong AS custom_Ten_Duong, c.Quan AS custom_Quan,
                       c.Phuong AS custom_Phuong, c.Duong AS custom_Duong, c.Ngo_So_nha AS custom_Ngo_So_nha,
                       c.bedrooms AS custom_bedrooms, c.restrooms AS custom_restrooms,
                       c.minimumRoadWidth AS custom_minimumRoadWidth, c.Noi_dung_chinh AS custom_Noi_dung_chinh,
                       c.Mo_ta_chi_tiet AS custom_Mo_ta_chi_tiet, c.Gia_chao AS custom_Gia_chao,
                       c.DT_Thuc_te AS custom_DT_Thuc_te, c.DT_Tren_so AS custom_DT_Tren_so,
                       c.So_Tang AS custom_So_Tang, c.Mat_Tien AS custom_Mat_Tien, c.Chieu_dai AS custom_Chieu_dai,
                       c.Huong AS custom_Huong, c.Criteria_Duong_truoc_nha AS custom_Criteria_Duong_truoc_nha,
                       c.Criteria_Noi_that AS custom_Criteria_Noi_that, c.Criteria_Thang_may AS custom_Criteria_Thang_may,
                       c.Criteria_Loai_ngo AS custom_Criteria_Loai_ngo, c.Criteria_Khoang_cach_bai_do_xe AS custom_Criteria_Khoang_cach_bai_do_xe,
                       c.Criteria_Kinh_doanh_Dong_tien AS custom_Criteria_Kinh_doanh_Dong_tien,
                       c.Criteria_Huong_nha AS custom_Criteria_Huong_nha, c.Criteria_Khoang_cach_duong_oto AS custom_Criteria_Khoang_cach_duong_oto
                FROM listings_v2 l
                LEFT JOIN listings_custom_v2 c ON l.System_ID = c.System_ID
                WHERE l.tk_id = ?
            """, (tk_id,))
            rows = s_cursor.fetchall()
        else:
            s_cursor.execute("""
                SELECT l.*, c.Ma_Khang_Ngo AS custom_Ma_Khang_Ngo, c.Gia_Public AS custom_Gia_Public,
                       c.Tieu_De_Public AS custom_Tieu_De_Public, c.Mo_ta_Public AS custom_Mo_ta_Public,
                       c.Note_Noi_Bo AS custom_Note_Noi_Bo, c.Trang_Thai_Giao_Dich AS custom_Trang_Thai_Giao_Dich,
                       c.Ngu_Tret AS custom_Ngu_Tret, c.CHDV AS custom_CHDV, c.Trang_Thai_KN AS custom_Trang_Thai_KN,
                       c.images_metadata_json AS custom_images_metadata_json, c.Dia_Chi_That AS custom_Dia_Chi_That,
                       c.So_Nha AS custom_So_Nha, c.Ten_Duong AS custom_Ten_Duong, c.Quan AS custom_Quan,
                       c.Phuong AS custom_Phuong, c.Duong AS custom_Duong, c.Ngo_So_nha AS custom_Ngo_So_nha,
                       c.bedrooms AS custom_bedrooms, c.restrooms AS custom_restrooms,
                       c.minimumRoadWidth AS custom_minimumRoadWidth, c.Noi_dung_chinh AS custom_Noi_dung_chinh,
                       c.Mo_ta_chi_tiet AS custom_Mo_ta_chi_tiet, c.Gia_chao AS custom_Gia_chao,
                       c.DT_Thuc_te AS custom_DT_Thuc_te, c.DT_Tren_so AS custom_DT_Tren_so,
                       c.So_Tang AS custom_So_Tang, c.Mat_Tien AS custom_Mat_Tien, c.Chieu_dai AS custom_Chieu_dai,
                       c.Huong AS custom_Huong, c.Criteria_Duong_truoc_nha AS custom_Criteria_Duong_truoc_nha,
                       c.Criteria_Noi_that AS custom_Criteria_Noi_that, c.Criteria_Thang_may AS custom_Criteria_Thang_may,
                       c.Criteria_Loai_ngo AS custom_Criteria_Loai_ngo, c.Criteria_Khoang_cach_bai_do_xe AS custom_Criteria_Khoang_cach_bai_do_xe,
                       c.Criteria_Kinh_doanh_Dong_tien AS custom_Criteria_Kinh_doanh_Dong_tien,
                       c.Criteria_Huong_nha AS custom_Criteria_Huong_nha, c.Criteria_Khoang_cach_duong_oto AS custom_Criteria_Khoang_cach_duong_oto
                FROM listings_v2 l
                LEFT JOIN listings_custom_v2 c ON l.System_ID = c.System_ID
            """)
            rows = s_cursor.fetchall()
            
        if not rows:
            # s_conn.close() handled by finally
            # t_conn.close() handled by finally
            return {"status": "success", "message": "Không tìm thấy căn nào để đồng bộ."}
            
        sync_count = 0
        for r in rows:
            r2 = dict(r)
            curr_tk_id = r2.get('tk_id')
            
            p1_data = {}
            p1_data['tk_id'] = curr_tk_id
            p1_data['status'] = r2.get('status', 'raw_text')
            p1_data['raw_images_tk_json'] = r2.get('raw_images_tk_json', '[]')
            p1_data['raw_drive_images_json'] = r2.get('raw_drive_images_json', '[]')
            p1_data['curated_config_json'] = r2.get('curated_config_json') or r2.get('custom_images_metadata_json') or '[]'
            p1_data['Chieu_dai'] = r2.get('custom_Chieu_dai') or r2.get('Chieu_dai') or ''
            p1_data['System_ID'] = r2.get('System_ID', '')
            p1_data['Link_Goc'] = r2.get('Link_Goc', '')
            p1_data['Dien_thoai_Dau_Chu'] = r2.get('Dien_thoai_Dau_Chu', '')
            p1_data['Ten_Dau_Chu_Hop_dong'] = r2.get('Ten_Dau_Chu') or r2.get('custom_Ten_Dau_Chu') or ''
            p1_data['Diem_Facebook'] = r2.get('Diem_Facebook', '')
            p1_data['Last_Crawl'] = r2.get('Last_Crawl', '')
            p1_data['Last_Sync'] = r2.get('Last_Sync', '')
            p1_data['Ma_TK_Moi'] = curr_tk_id
            
            so_nha = r2.get('custom_So_Nha') or r2.get('Ngo_So_nha') or ''
            duong = r2.get('custom_Ten_Duong') or r2.get('streetName') or ''
            quan = r2.get('custom_Quan') or r2.get('Quan') or ''
            phuong = r2.get('custom_Phuong') or r2.get('Phuong') or ''
            
            p1_data['Ngo_So_nha'] = so_nha
            p1_data['Duong'] = duong
            p1_data['Quan'] = quan
            p1_data['Phuong'] = phuong
            p1_data['T_nh'] = r2.get('placeName') or 'Hồ Chí Minh'
            
            ma_khang_ngo = r2.get('custom_Ma_Khang_Ngo') or r2.get('Ma_Khang_Ngo_ID') or gen_id_khang_ngo_python(so_nha, duong, quan)
            p1_data['Ma_Khang_Ngo_ID'] = ma_khang_ngo
            p1_data['Ma_Hang'] = r2.get('custom_Ma_Khang_Ngo') or r2.get('Ma_Hang') or f"TK-{curr_tk_id.split('-')[-1].upper()}"
            
            p1_data['Noi_dung_chinh'] = r2.get('custom_Noi_dung_chinh') or r2.get('Noi_dung_chinh') or ''
            p1_data['Mo_ta_chi_tiet'] = r2.get('custom_Mo_ta_chi_tiet') or r2.get('Mo_ta_chi_tiet') or ''
            p1_data['Gia_chao'] = r2.get('custom_Gia_chao') or r2.get('Gia_chao') or ''
            p1_data['DT_Thuc_te'] = r2.get('custom_DT_Thuc_te') or r2.get('DT_Thuc_te') or ''
            p1_data['DT_Tren_so'] = r2.get('custom_DT_Tren_so') or r2.get('DT_Tren_so') or ''
            p1_data['So_Tang'] = r2.get('custom_So_Tang') or r2.get('So_Tang') or ''
            p1_data['Mat_Tien'] = r2.get('custom_Mat_Tien') or r2.get('Mat_Tien') or ''
            p1_data['Huong'] = r2.get('custom_Huong') or r2.get('Huong') or ''
            p1_data['Ten_Chu_Nha'] = r2.get('Ten_Chu_Nha', '')
            p1_data['Dien_thoai_1'] = r2.get('Dien_thoai_1', '')
            p1_data['Trang_thai'] = r2.get('custom_Trang_Thai_Giao_Dich') or r2.get('status_nguon') or ''
            
            p1_data['Tieu_de_Public'] = r2.get('custom_Tieu_De_Public') or r2.get('Noi_dung_chinh') or ''
            p1_data['Mo_ta_Public'] = r2.get('custom_Mo_ta_Public') or r2.get('Mo_ta_chi_tiet') or ''
            p1_data['Gia_Public'] = r2.get('custom_Gia_Public') or r2.get('Gia_chao') or ''
            p1_data['Duong_truoc_nha_m'] = r2.get('custom_minimumRoadWidth') or r2.get('minimumRoadWidth') or ''
            p1_data['Tinh_trang_nha'] = r2.get('custom_Trang_Thai_Giao_Dich') or r2.get('status_nguon') or ''
            p1_data['So_phong_ngu'] = r2.get('custom_bedrooms') or r2.get('bedrooms') or ''
            p1_data['So_nha_ve_sinh'] = r2.get('custom_restrooms') or r2.get('restrooms') or ''
            p1_data['Danh_gia_Admin'] = r2.get('custom_Trang_Thai_KN') or ''
            p1_data['Ngu_tret_Admin'] = r2.get('custom_Ngu_Tret') or 'N'
            p1_data['CHDV_Admin'] = r2.get('custom_CHDV') or 'N'
            p1_data['Trang_thai_Public'] = r2.get('custom_Trang_Thai_Giao_Dich') or ''
            p1_data['Phuong_cu_AI'] = r2.get('Phuong_cu_AI_') or r2.get('Phuong_cu_AI') or ''
            
            flat_imgs = get_flattened_images_pool2(s_cursor, curr_tk_id)
            p1_data.update(flat_imgs)
            p1_data['Hinh_Nhan_Dien'] = r2.get('Hinh_Nhan_Dien') or flat_imgs.get(get_safe_col_name("Hình Mặt Tiền")) or ''
            
            for col in t_cols:
                if col not in p1_data:
                    p1_data[col] = str(r2.get(col) or '')
                    
            p1_match = None
            if p1_data.get('System_ID'):
                p1_match = t_cursor.execute("SELECT id, tk_id FROM listings WHERE System_ID = ?", (p1_data['System_ID'],)).fetchone()
            if not p1_match and p1_data.get('Ma_Khang_Ngo_ID'):
                p1_match = t_cursor.execute("SELECT id, tk_id FROM listings WHERE Ma_Khang_Ngo_ID = ?", (p1_data['Ma_Khang_Ngo_ID'],)).fetchone()
                
            if p1_match:
                set_clause = ", ".join([f"`{col}` = ?" for col in t_cols])
                update_vals = [p1_data[col] for col in t_cols] + [p1_match[0]]
                t_cursor.execute(f"UPDATE listings SET {set_clause} WHERE id = ?", update_vals)
                add_log_message(f"[🔄] Đã cập nhật đè dòng cũ khớp địa chỉ/System_ID cho căn {curr_tk_id} (Dòng ID Pool1: {p1_match[0]})")
            else:
                col_names = ", ".join([f"`{col}`" for col in t_cols])
                placeholders = ", ".join(["?" for _ in t_cols])
                insert_vals = [p1_data[col] for col in t_cols]
                t_cursor.execute(f"INSERT INTO listings ({col_names}) VALUES ({placeholders})", insert_vals)
                add_log_message(f"[➕] Đã chèn mới dòng cho căn {curr_tk_id} vào Pool 1")
                
            sync_count += 1
            
        t_conn.commit()
    finally:
        if s_conn:
            s_conn.close()
        if t_conn:
            t_conn.close()
        # t_conn.close() handled by finally
    
    add_log_message(f"[✅] Đã đồng bộ thành công {sync_count} căn từ Pool 2 sang Pool 1.")
    return {"status": "success", "message": f"Đồng bộ thành công {sync_count} căn sang Pool 1."}

def sync_p1_to_p2(src_db, tgt_db, input_so_nha, input_duong, add_log_message):
    add_log_message(f"[⚡] Bắt đầu đồng bộ ngược ad-hoc căn '{input_so_nha}' đường '{input_duong}' từ Pool 1 sang Pool 2...")
    
    s_conn = None
    t_conn = None
    try:
        s_conn = sqlite3.connect(src_db)
        s_conn.row_factory = sqlite3.Row
        s_cursor = s_conn.cursor()
    
        t_conn = sqlite3.connect(tgt_db)
        t_conn.row_factory = sqlite3.Row
        t_cursor = t_conn.cursor()
        
        target_ma_kn = gen_id_khang_ngo_python(input_so_nha, input_duong, "")
        s_cursor.execute("SELECT * FROM listings WHERE Ma_Khang_Ngo_ID = ?", (target_ma_kn,))
        p1_row = s_cursor.fetchone()
        
        if not p1_row:
            norm_input_so_nha, norm_input_duong = normalize_address(input_so_nha, input_duong)
            s_cursor.execute("SELECT * FROM listings")
            for r in s_cursor.fetchall():
                r_dict = dict(r)
                r_so_nha, r_duong = normalize_address(r_dict.get('Ngo_So_nha'), r_dict.get('Duong'))
                if r_so_nha == norm_input_so_nha and r_duong == norm_input_duong:
                    p1_row = r
                    break
                    
        if not p1_row:
            # s_conn.close() handled by finally
            # t_conn.close() handled by finally
            add_log_message(f"[❌ LỖI] Không tìm thấy căn nhà khớp địa chỉ '{input_so_nha} {input_duong}' trong Pool 1.")
            return {"status": "error", "message": f"Không tìm thấy căn nhà khớp địa chỉ '{input_so_nha} {input_duong}' trong Pool 1."}
            
        p1_dict = dict(p1_row)
        old_tk_id = p1_dict.get('tk_id', '')
        new_tk_id = f"LEGACY-{old_tk_id}"
        system_id = p1_dict.get('System_ID') or gen_unique_system_id()
        ma_khang_ngo = p1_dict.get('Ma_Khang_Ngo_ID') or target_ma_kn
        
        add_log_message(f"[ℹ] Tìm thấy căn khớp: {old_tk_id} (System ID: {system_id}). Thực hiện di trú sang mã mới: {new_tk_id}")
        
        v2_fields = {}
        v2_fields['tk_id'] = new_tk_id
        v2_fields['status'] = 'published_legacy'
        v2_fields['System_ID'] = system_id
        v2_fields['Ma_Hang'] = p1_dict.get('Ma_Hang') or new_tk_id
        v2_fields['isSigned'] = '0'
        v2_fields['status_nguon'] = p1_dict.get('Trang_thai') or 'Đang bán'
        v2_fields['streetName'] = p1_dict.get('Duong', '')
        v2_fields['Quan'] = p1_dict.get('Quan', '')
        v2_fields['Phuong'] = p1_dict.get('Phuong', '')
        v2_fields['Ngo_So_nha'] = p1_dict.get('Ngo_So_nha', '')
        v2_fields['Noi_dung_chinh'] = p1_dict.get('Noi_dung_chinh', '')
        v2_fields['Mo_ta_chi_tiet'] = p1_dict.get('Mo_ta_chi_tiet', '')
        v2_fields['Gia_chao'] = p1_dict.get('Gia_chao', '')
        v2_fields['DT_Thuc_te'] = p1_dict.get('DT_Thuc_te', '')
        v2_fields['DT_Tren_so'] = p1_dict.get('DT_Tren_so', '')
        v2_fields['So_Tang'] = p1_dict.get('So_Tang', '')
        v2_fields['Mat_Tien'] = p1_dict.get('Mat_Tien', '')
        v2_fields['Huong'] = p1_dict.get('Huong', '')
        v2_fields['bedrooms'] = p1_dict.get('So_phong_ngu', '')
        v2_fields['restrooms'] = p1_dict.get('So_nha_ve_sinh', '')
        v2_fields['minimumRoadWidth'] = p1_dict.get('Duong_truoc_nha_m', '')
        v2_fields['Ten_Chu_Nha'] = p1_dict.get('Ten_Chu_Nha', '')
        v2_fields['Dien_thoai_1'] = p1_dict.get('Dien_thoai_1', '')
        v2_fields['Dien_thoai_Dau_Chu'] = p1_dict.get('Dien_thoai_Dau_Chu', '')
        v2_fields['Ten_Dau_Chu'] = p1_dict.get('Ten_Dau_Chu_Hop_dong', '')
        v2_fields['Link_Goc'] = p1_dict.get('Link_Goc', '')
        v2_fields['Last_Crawl'] = p1_dict.get('Last_Crawl') or datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        v2_fields['Last_Sync'] = p1_dict.get('Last_Sync') or datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        v2_fields['Chieu_dai'] = p1_dict.get('Chieu_dai', '')
        v2_fields['raw_images_tk_json'] = p1_dict.get('raw_images_tk_json', '[]')
        v2_fields['raw_drive_images_json'] = p1_dict.get('raw_drive_images_json', '[]')
        v2_fields['curated_config_json'] = p1_dict.get('curated_config_json', '[]')
        
        t_cursor.execute("PRAGMA table_info(listings_v2)")
        v2_db_cols = {row[1] for row in t_cursor.fetchall()}
        
        v2_valid_fields = {k: v for k, v in v2_fields.items() if k in v2_db_cols}
        cols = list(v2_valid_fields.keys())
        vals = [v2_valid_fields[k] for k in cols]
        placeholders = ", ".join(["?"] * len(cols))
        t_cursor.execute(f"INSERT OR REPLACE INTO listings_v2 ({', '.join([f'`{c}`' for c in cols])}) VALUES ({placeholders})", vals)
        
        custom_fields = {}
        custom_fields['System_ID'] = system_id
        custom_fields['Ma_Khang_Ngo'] = ma_khang_ngo
        custom_fields['Gia_Public'] = p1_dict.get('Gia_Public') or p1_dict.get('Gia_chao') or ''
        custom_fields['Tieu_De_Public'] = p1_dict.get('Tieu_de_Public') or p1_dict.get('Noi_dung_chinh') or ''
        custom_fields['Mo_ta_Public'] = p1_dict.get('Mo_ta_Public') or p1_dict.get('Mo_ta_chi_tiet') or ''
        custom_fields['Note_Noi_Bo'] = ''
        custom_fields['Trang_Thai_Giao_Dich'] = p1_dict.get('Tinh_trang_nha') or p1_dict.get('Trang_thai') or 'Đang bán'
        custom_fields['Ngu_Tret'] = p1_dict.get('Ngu_tret_Admin') or 'N'
        custom_fields['CHDV'] = p1_dict.get('CHDV_Admin') or 'N'
        custom_fields['Trang_Thai_KN'] = p1_dict.get('Danh_gia_Admin') or 'Hàng Ngon'
        custom_fields['Dia_Chi_That'] = f"{p1_dict.get('Ngo_So_nha', '')} {p1_dict.get('Duong', '')}"
        custom_fields['So_Nha'] = p1_dict.get('Ngo_So_nha', '')
        custom_fields['Ten_Duong'] = p1_dict.get('Duong', '')
        custom_fields['Quan'] = p1_dict.get('Quan', '')
        custom_fields['Phuong'] = p1_dict.get('Phuong', '')
        custom_fields['Duong'] = p1_dict.get('Duong', '')
        custom_fields['Ngo_So_nha'] = p1_dict.get('Ngo_So_nha', '')
        custom_fields['bedrooms'] = p1_dict.get('So_phong_ngu', '')
        custom_fields['restrooms'] = p1_dict.get('So_nha_ve_sinh', '')
        custom_fields['minimumRoadWidth'] = p1_dict.get('Duong_truoc_nha_m', '')
        custom_fields['Noi_dung_chinh'] = p1_dict.get('Noi_dung_chinh', '')
        custom_fields['Mo_ta_chi_tiet'] = p1_dict.get('Mo_ta_chi_tiet', '')
        custom_fields['Gia_chao'] = p1_dict.get('Gia_chao', '')
        custom_fields['DT_Thuc_te'] = p1_dict.get('DT_Thuc_te', '')
        custom_fields['DT_Tren_so'] = p1_dict.get('DT_Tren_so', '')
        custom_fields['So_Tang'] = p1_dict.get('So_Tang', '')
        custom_fields['Mat_Tien'] = p1_dict.get('Mat_Tien', '')
        custom_fields['Chieu_dai'] = p1_dict.get('Chieu_dai', '')
        custom_fields['Huong'] = p1_dict.get('Huong', '')
        
        t_cursor.execute("PRAGMA table_info(listings_custom_v2)")
        custom_db_cols = {row[1] for row in t_cursor.fetchall()}
        
        images_to_insert = []
        curated_images = []
        if p1_dict.get('curated_config_json'):
            try:
                curated_data = json.loads(p1_dict['curated_config_json'])
                if isinstance(curated_data, list):
                    for img in curated_data:
                        url = img.get('url') if isinstance(img, dict) else str(img)
                        if url:
                            curated_images.append(url)
                            origin = img.get('origin') if (isinstance(img, dict) and img.get('origin')) else ('self' if ('r2.dev' in url or 'cloudinary.com' in url) else 'crawl')
                            role = img.get('role', 'interior') if isinstance(img, dict) else 'interior'
                            images_to_insert.append({
                                'image_url': url,
                                'r2_url': url if origin == 'self' else '',
                                'role': role,
                                'origin': origin
                            })
            except Exception:
                pass
                
        flat_mappings = [
            ('Hinh_Mat_Tien', 'facade'),
        ]
        for i in range(1, 6):
            flat_mappings.append((f'So_do_thua_dat_{i}', 'diagram'))
        for i in range(1, 11):
            flat_mappings.append((f'Hinh_Hem_{i}', 'alley'))
        for i in range(1, 26):
            flat_mappings.append((f'Anh_{i}', 'interior'))
            
        for col, role in flat_mappings:
            url = p1_dict.get(col)
            if url and url.strip():
                url = url.strip()
                if any(item['image_url'] == url for item in images_to_insert):
                    continue
                origin = 'self' if ('r2.dev' in url or 'cloudinary.com' in url) else 'crawl'
                images_to_insert.append({
                    'image_url': url,
                    'r2_url': url if origin == 'self' else '',
                    'role': role,
                    'origin': origin
                })
                
        custom_images_list = []
        for img in images_to_insert:
            if img['role'] not in ["facade", "cover", "diagram", "deleted", "hidden"]:
                custom_images_list.append({"url": img['image_url'], "role": img['role']})
        custom_fields['images_metadata_json'] = json.dumps(custom_images_list)
        
        custom_valid_fields = {k: v for k, v in custom_fields.items() if k in custom_db_cols}
        c_cols = list(custom_valid_fields.keys())
        c_vals = [clean_sheet_formula_prefix(custom_valid_fields[k]) for k in c_cols]
        c_placeholders = ", ".join(["?"] * len(c_cols))
        t_cursor.execute(f"INSERT OR REPLACE INTO listings_custom_v2 ({', '.join([f'`{c}`' for c in c_cols])}) VALUES ({c_placeholders})", c_vals)
        
        t_cursor.execute("DELETE FROM listings_images WHERE tk_id = ?", (new_tk_id,))
        for i, img in enumerate(images_to_insert):
            t_cursor.execute("""
                INSERT INTO listings_images (tk_id, image_url, r2_url, role, sequence_index, origin)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (new_tk_id, img['image_url'], img['r2_url'], img['role'], i, img['origin']))
            
        t_conn.commit()
    finally:
        if s_conn:
            s_conn.close()
        if t_conn:
            t_conn.close()
        # t_conn.close() handled by finally
    
    add_log_message(f"[✅] Đã đồng bộ ngược thành công căn '{input_so_nha} {input_duong}' sang Pool 2 làm legacy tin.")
    return {"status": "success", "message": f"Đã di trú thành công căn khớp sang Pool 2 với ID {new_tk_id}."}

def recrawl_all_listings(db_file=None, add_log_message=None):
    """
    Cào lại toàn bộ các căn trong Pool 2 (listings_v2), so sánh sự thay đổi và lưu vào pending_diff_json.
    """
    if add_log_message is None:
        def add_log_message(msg):
            print(msg)
            
    add_log_message("[⚡] Bắt đầu tiến trình cào lại định kỳ toàn bộ CSDL (recrawl-all)...")
    
    if db_file is None:
        db_file = get_db_file()
        
    if not os.path.exists(db_file):
        add_log_message(f"[❌ LỖI] Database {db_file} không tồn tại.")
        return {"status": "error", "message": f"Database {db_file} không tồn tại."}
        
    # Check if listings_v2 table exists in the database
    conn_check = None
    try:
        conn_check = sqlite3.connect(db_file, timeout=30.0)
        cursor_check = conn_check.cursor()
        cursor_check.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings_v2'")
        has_v2 = cursor_check.fetchone()
    finally:
        if conn_check:
            conn_check.close()
    
    if not has_v2:
        add_log_message(f"[❌ LỖI] Database {db_file} không phải là hệ thống Pool 2 (không có bảng listings_v2).")
        return {"status": "error", "message": "recrawl-all chỉ hỗ trợ trên hệ thống Pool 2."}
        
    conn = None
    try:
        conn = sqlite3.connect(db_file, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM listings_v2")
        listings = cursor.fetchall()
    finally:
        if conn:
            conn.close()
    
    if not listings:
        add_log_message("[ℹ] Không có căn nào trong listings_v2 để cào lại.")
        return {"status": "success", "message": "Không có căn nào để cào lại."}
        
    add_log_message(f"[ℹ] Phát hiện {len(listings)} căn trong listings_v2 cần cào lại.")
    
    cookie_path = "thienkhoi_cookie.txt"
    if not os.path.exists(cookie_path):
        add_log_message("[❌ LỖI] Không tìm thấy file thienkhoi_cookie.txt.")
        return {"status": "error", "message": "Không tìm thấy file thienkhoi_cookie.txt."}
        
    with open(cookie_path, 'r', encoding='utf-8') as f:
        cookie_str = f.read().strip()
        
    from fetcher import parse_criteria_groups, try_refresh_tokens, extract_tokens
    import requests
    
    access_token, refresh_token, _ = extract_tokens(cookie_str)
    if not access_token:
        add_log_message("[❌ LỖI] Không thể bóc tách access token từ cookie.")
        return {"status": "error", "message": "Không thể bóc tách access token từ cookie."}
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    explicit_criteria_cols = [
        "Criteria_Tiem_nang_Rui_ro", "Criteria_Duong_truoc_nha", "Criteria_Loai_BDS",
        "Criteria_Giay_to_phap_ly", "Criteria_Hinh_dang_dat", "Criteria_Tinh_trang_xay_dung",
        "Criteria_Cau_truc_nha", "Criteria_Noi_that", "Criteria_Thang_may", "Criteria_Loai_ngo",
        "Criteria_Vi_tri_tinh_thue", "Criteria_Mat_thoang", "Criteria_Khoang_cach_bai_do_xe",
        "Criteria_Kinh_doanh_Dong_tien", "Criteria_Tien_ich", "Criteria_Phong_thuy",
        "Criteria_Huong_nha", "Criteria_Vi_tri_trong_ngo", "Criteria_Khoang_cach_duong_oto"
    ]
    
    fields_to_compare = [
        ("Gia_chao", "Giá chào"),
        ("status_nguon", "Trạng thái nguồn"),
        ("Mo_ta_chi_tiet", "Mô tả chi tiết"),
        ("bedrooms", "Số phòng ngủ"),
        ("restrooms", "Số nhà vệ sinh"),
        ("Huong", "Hướng"),
        ("DT_Thuc_te", "Diện tích thực tế"),
        ("DT_Tren_so", "Diện tích trên sổ"),
        ("So_Tang", "Số tầng"),
        ("Mat_Tien", "Mặt tiền"),
        ("Chieu_dai", "Chiều dài")
    ]
    for c in explicit_criteria_cols:
        fields_to_compare.append((c, c.replace("Criteria_", "Tiêu chí ")))
        
    crawled_count = 0
    updated_diffs_count = 0
    
    for idx, old_row in enumerate(listings):
        old_dict = dict(old_row)
        tk_id = old_dict.get('tk_id')
        
        if tk_id.startswith("LEGACY-"):
            add_log_message(f"[{idx+1}/{len(listings)}] Căn {tk_id} là legacy tin, bỏ qua không cào lại.")
            continue
            
        add_log_message(f"[{idx+1}/{len(listings)}] Đang cào lại căn {tk_id}...")
        detail_api_url = f"https://backend.thienkhoi.com/product/v1/property/{tk_id}"
        
        time.sleep(random.uniform(1.0, 2.0))
        
        try:
            r_detail = requests.get(detail_api_url, headers=headers, timeout=20)
            if r_detail.status_code in [401, 403]:
                add_log_message("Token hết hạn, đang cố gắng refresh...")
                refreshed_cookie = try_refresh_tokens()
                if refreshed_cookie:
                    cookie_str = refreshed_cookie
                    access_token, _, _ = extract_tokens(cookie_str)
                    headers["Authorization"] = f"Bearer {access_token}"
                    r_detail = requests.get(detail_api_url, headers=headers, timeout=20)
                else:
                    add_log_message("[❌ LỖI] Refresh token thất bại. Dừng tiến trình cào lại.")
                    return {"status": "error", "message": "Cookie hết hạn và refresh token thất bại."}
                    
            if r_detail.status_code != 200:
                add_log_message(f"[⚠️ WARNING] Lỗi HTTP {r_detail.status_code} khi tải chi tiết căn {tk_id}. Bỏ qua.")
                continue
                
            detail_json = r_detail.json()
            detail_data = detail_json.get("data") or {}
            if not detail_data:
                add_log_message(f"[⚠️ WARNING] Dữ liệu căn {tk_id} trống. Bỏ qua.")
                continue
                
            ma_hang = detail_data.get("code") or tk_id
            tinh = (detail_data.get("district") or {}).get("provinceName", "TP Hồ Chí Minh")
            quan_name = (detail_data.get("district") or {}).get("name", "")
            phuong_name = (detail_data.get("ward") or {}).get("name", "")
            duong_name = (detail_data.get("street") or {}).get("name") if detail_data.get("street") else detail_data.get("streetName", "")
            ngo_so_nha = detail_data.get("address", "")
            
            phan_loai_names = [c.get("name") for c in (detail_data.get("criteria") or []) if c and c.get("name")]
            phan_loai = ", ".join(phan_loai_names)
            
            dt_so = str(detail_data.get("area") or "").strip()
            dt_thuc = str(detail_data.get("actualArea") or "").strip()
            if dt_so and dt_thuc and dt_so != dt_thuc:
                area_str = f"{dt_so}/{dt_thuc}"
            else:
                area_str = dt_so or dt_thuc

            floors_val = str(detail_data.get("floors") or "").strip()
            wide_val = str(detail_data.get("wide") or "").strip()
            depth_val = str(detail_data.get("depth") or "").strip()
            price_val = str(detail_data.get("offeringPrice") or "").strip()

            parts = []
            if ngo_so_nha:
                parts.append(str(ngo_so_nha).strip())
            if duong_name:
                parts.append(str(duong_name).strip())
            if area_str:
                parts.append(str(area_str).strip())
            if floors_val:
                parts.append(str(floors_val).strip())
            if wide_val:
                parts.append(str(wide_val).strip())
            if depth_val:
                parts.append(str(depth_val).strip())
            if price_val:
                parts.append(f"{price_val} tỷ")

            noi_dung_chinh = " ".join([p for p in parts if p])
            mo_ta_chi_tiet = detail_data.get("description", "")
            gia_chao = str(detail_data.get("offeringPrice", ""))
            dt_thuc_te = str(detail_data.get("actualArea", ""))
            dt_tren_so = str(detail_data.get("area", ""))
            so_tang = str(detail_data.get("floors", ""))
            mat_tien = str(detail_data.get("wide", ""))
            chieu_dai = str(detail_data.get("depth", ""))
            so_phong_ngu = str(detail_data.get("bedrooms") or "")
            so_nha_ve_sinh = str(detail_data.get("restrooms") or "")
            # US-110: Trích xuất Hướng trực tiếp từ criteria HOUSE_DIRECTION của JSON thô
            criteria_list = detail_data.get("criteria") or []
            huong = next((c.get("name", "") for c in criteria_list if c and c.get("groupCode") == "HOUSE_DIRECTION"), "")
            duong_truoc_nha = str(detail_data.get("minimumRoadWidth") or "")
            trang_thai = detail_data.get("status", "")
            
            ten_chu_nha = ", ".join([o.get("name") for o in (detail_data.get("homeOwner") or []) if o and o.get("name")])
            dien_thoai_1 = detail_data.get("contactPhoneNumber", "")
            dt_dau_chu = (detail_data.get("ownerSideUser") or {}).get("phone", "")
            ten_dau_chu = (detail_data.get("ownerSideUser") or {}).get("name", "")
            link_fb = (detail_data.get("ownerSideUser") or {}).get("fbLink", "")
            
            media = detail_data.get("media", [])
            property_images = []
            sodo_images = []
            
            for m in media:
                m_type = m.get("type")
                m_url = m.get("url")
                if not m_url:
                    continue
                if m_type in ["parcel_map", "certificate_image"]:
                    sodo_images.append(m_url)
                else:
                    property_images.append(m_url)
                        
            channels_list = detail_data.get("channels") or []
            channels_str = ", ".join([str(c) for c in channels_list if c])
            tags_list = detail_data.get("tags") or []
            tags_str = ", ".join([t.get("name") if isinstance(t, dict) else str(t) for t in tags_list if t])
            
            raw_images_tk_ordered = [m.get("url") for m in media if m.get("url")]
            
            crawled_data = {
                "raw_images_tk_ordered": raw_images_tk_ordered,
                "Mã Hàng": ma_hang,
                "Tỉnh": tinh,
                "Quận": quan_name,
                "Phường": phuong_name,
                "Đường": duong_name,
                "Ngõ/Số nhà": ngo_so_nha,
                "Phân loại": phan_loai,
                "Nội dung chính": noi_dung_chinh,
                "Mô tả chi tiết": mo_ta_chi_tiet,
                "Giá chào": gia_chao,
                "Giá Public": gia_chao,
                "DT Thực tế": dt_thuc_te,
                "DT Trên sổ": dt_tren_so,
                "Số Tầng": so_tang,
                "Mặt Tiền": mat_tien,
                "Chieu_dai": chieu_dai,
                "Số phòng ngủ": so_phong_ngu,
                "Số nhà vệ sinh": so_nha_ve_sinh,
                "Hướng": huong,
                "Đường trước nhà (m)": duong_truoc_nha,
                "Tình trạng nhà": "Bình thường",
                "Trạng thái": trang_thai,
                "Tên Chủ Nhà": ten_chu_nha,
                "Điện thoại 1": dien_thoai_1,
                "Điện thoại Đầu Chủ": dt_dau_chu,
                "Tên Đầu Chủ (Hợp đồng)": ten_dau_chu,
                "Ten_Dau_Chu": ten_dau_chu,
                "Điểm Facebook": link_fb,
                "Link Gốc": f"https://proptech.thienkhoi.com/warehouse/sources/{tk_id}",
                "Last Crawl": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "bedrooms": so_phong_ngu,
                "restrooms": so_nha_ve_sinh,
                "minimumRoadWidth": duong_truoc_nha,
                "isSigned": "1" if detail_data.get("isSigned") else "0",
                "status_nguon": trang_thai,
                "commissionAgent": str(detail_data.get("commissionAgent") or ""),
                "ownerSideUserId": str(detail_data.get("ownerSideUserId") or ""),
                "certificateSeries": str(detail_data.get("certificateSeries") or ""),
                "latitude": str((detail_data.get("coordinate") or {}).get("latitude") or detail_data.get("latitude") or ""),
                "longitude": str((detail_data.get("coordinate") or {}).get("longitude") or detail_data.get("longitude") or ""),
                "placeName": str(detail_data.get("placeName") or ""),
                "streetName": str(detail_data.get("streetName") or ""),
                "balconies": str(detail_data.get("balconies") or ""),
                "sidewalk": str(detail_data.get("sidewalk") or ""),
                "behindOpenSpace": str(detail_data.get("behindOpenSpace") or ""),
                "sideOpenSpace": str(detail_data.get("sideOpenSpace") or ""),
                "createdAt": str(detail_data.get("createdAt") or ""),
                "updatedAt": str(detail_data.get("updatedAt") or ""),
                "commissionType": str(detail_data.get("commissionType") or ""),
                "commissionValue": str(detail_data.get("commissionValue") or ""),
                "isDispute": "1" if detail_data.get("isDispute") else "0",
                "createdAtSigned": str(detail_data.get("createdAtSigned") or ""),
                "CCCD_Dau_Chu": str((detail_data.get("ownerSideUser") or {}).get("numberId") or ""),
                "Kenh_tin_TK": channels_str,
                "The_tags_TK": tags_str
            }
            
            criteria_list = detail_data.get("criteria") or []
            criteria_cols = parse_criteria_groups(criteria_list)
            crawled_data.update(criteria_cols)
            
            for idx, url in enumerate(sodo_images[:5]):
                crawled_data[f"Sơ đồ thửa đất {idx+1}"] = url
                
            # Perform Diff comparison
            diff = {}
            for col_name, label in fields_to_compare:
                old_val = str(old_dict.get(col_name) or "").strip()
                
                new_val_raw = None
                if col_name in crawled_data:
                    new_val_raw = crawled_data[col_name]
                else:
                    for k, v in crawled_data.items():
                        if get_safe_col_name(k) == col_name:
                            new_val_raw = v
                            break
                            
                new_val = str(new_val_raw or "").strip()
                if old_val != new_val:
                    diff[col_name] = {
                        "label": label,
                        "old": old_val,
                        "new": new_val
                    }
                    
            pending_diff_json_val = None
            if diff:
                pending_diff_json_val = json.dumps({"gia_tri_thay_doi": diff}, ensure_ascii=False)
                updated_diffs_count += 1
                add_log_message(f"  [⚠️ KHÁC BIỆT PHÁT HIỆN] Căn {ma_hang} có {len(diff)} trường thay đổi:")
                for col_name, chg in diff.items():
                    add_log_message(f"    - {chg['label']}: '{chg['old']}' -> '{chg['new']}'")
            else:
                add_log_message(f"  [✅ KHỚP] Căn {ma_hang} không có thay đổi dữ liệu.")
                
            save_raw_to_sqlite(tk_id, crawled_data, property_images, db_file=db_file)
            
            conn_u = None
            try:
                conn_u = sqlite3.connect(db_file, timeout=30.0)
                cursor_u = conn_u.cursor()
                cursor_u.execute("UPDATE listings_v2 SET pending_diff_json = ? WHERE tk_id = ?", (pending_diff_json_val, tk_id))
                conn_u.commit()
            finally:
                if conn_u:
                    conn_u.close()
            
            crawled_count += 1
            
        except Exception as e_house:
            add_log_message(f"  [❌ LỖI] Lỗi cào lại căn {tk_id}: {str(e_house)}")
            
    add_log_message(f"[🏁 HOÀN TẤT] Cào lại thành công {crawled_count} căn. Phát hiện {updated_diffs_count} căn có thay đổi.")
    return {"status": "success", "message": f"Cào lại thành công {crawled_count} căn. Có {updated_diffs_count} căn thay đổi."}

def load_custom_columns():
    """
    Đọc các cột tùy biến tự tạo từ settings.json và thêm vào các mảng header toàn cục.
    """
    global LISTINGS_V2_COLS, CUSTOM_HEADERS, PUBLIC_WHITELIST_HEADERS_BASE, RAW_LISTINGS_HEADERS
    try:
        from core.config import read_settings
        cfg = read_settings()
        custom_cols = cfg.get("custom_schema_columns", [])
        for col in custom_cols:
            name = col.get("column_name")
            safe_name = get_safe_col_name(name)
            is_public = col.get("is_public", False)
            
            # Tránh nạp trùng lặp
            if safe_name not in LISTINGS_V2_COLS:
                LISTINGS_V2_COLS.append(safe_name)
            if name not in CUSTOM_HEADERS and safe_name not in CUSTOM_HEADERS:
                CUSTOM_HEADERS.append(name)
            if is_public:
                if "Last updated" in PUBLIC_WHITELIST_HEADERS_BASE:
                    idx = PUBLIC_WHITELIST_HEADERS_BASE.index("Last updated")
                    if name not in PUBLIC_WHITELIST_HEADERS_BASE and safe_name not in PUBLIC_WHITELIST_HEADERS_BASE:
                        PUBLIC_WHITELIST_HEADERS_BASE.insert(idx, name)
                else:
                    if name not in PUBLIC_WHITELIST_HEADERS_BASE and safe_name not in PUBLIC_WHITELIST_HEADERS_BASE:
                        PUBLIC_WHITELIST_HEADERS_BASE.append(name)
            
        # Recompute RAW_LISTINGS_HEADERS
        raw_headers = [
            "tk_id", "status", "raw_images_tk_json", "raw_drive_images_json", "curated_config_json"
        ] + [col for col in LISTINGS_V2_COLS if col not in ["tk_id", "status"]] + EXPLICIT_CRITERIA_COLS
        
        _seen = set()
        _raw_dedup = []
        for _col in raw_headers:
            _name = get_safe_col_name(_col)
            if _name not in _seen:
                _seen.add(_name)
                _raw_dedup.append(_name)
        RAW_LISTINGS_HEADERS = _raw_dedup
    except Exception as e:
        print(f"[⚠️ ERROR load_custom_columns] {str(e)}")

def add_column_to_google_sheets_v2(safe_name, header_name, is_public, get_google_credentials, load_config, add_log_message):
    """
    Chèn thêm cột vào File 1 Raw, File 2 Custom, và File 3 Public (nếu is_public=True) của Pool2.
    """
    creds = get_google_credentials()
    cfg = load_config()
    if os.environ.get("STAGING") == "true":
        raw_sheet_id = cfg.get("staging_pool_sheet_id") or cfg.get("pool2_raw_sheet_id")
        custom_sheet_id = cfg.get("staging_source_sheet_id") or cfg.get("pool2_custom_sheet_id")
        public_sheet_id = cfg.get("staging_public_sheet_id") or cfg.get("pool2_public_sheet_id")
    else:
        raw_sheet_id = cfg.get("pool2_raw_sheet_id")
        custom_sheet_id = cfg.get("pool2_custom_sheet_id")
        public_sheet_id = cfg.get("pool2_public_sheet_id")
    
    if not creds:
        add_log_message("[⚠️ ERROR Sheets] Không thể lấy Google Credentials để cập nhật header Sheets.")
        return False
        
    import gspread
    try:
        client = gspread.authorize(creds)
        client.http_client.session.timeout = 30
        
        # 1. Thêm vào File 1 Raw
        if raw_sheet_id:
            try:
                raw_spreadsheet = client.open_by_key(raw_sheet_id)
                raw_sheet = raw_spreadsheet.worksheet("Listings")
                raw_headers = raw_sheet.row_values(1)
                if safe_name not in raw_headers:
                    raw_sheet.add_cols(1)
                    raw_headers.append(safe_name)
                    col_letter = gspread.utils.rowcol_to_a1(1, len(raw_headers)).replace("1", "")
                    raw_sheet.update(range_name=f"{col_letter}1", values=[[safe_name]], value_input_option='USER_ENTERED')
                    add_log_message(f"[✅ Sheets] Đã chèn cột '{safe_name}' vào File 1 Raw.")
            except Exception as e_raw:
                add_log_message(f"[⚠️ ERROR Raw Sheet] {str(e_raw)}")
                
        # 2. Thêm vào File 2 Custom
        if custom_sheet_id:
            try:
                custom_spreadsheet = client.open_by_key(custom_sheet_id)
                custom_sheet = custom_spreadsheet.worksheet("Custom")
                custom_headers = custom_sheet.row_values(1)
                if header_name not in custom_headers:
                    custom_sheet.add_cols(1)
                    custom_headers.append(header_name)
                    col_letter = gspread.utils.rowcol_to_a1(1, len(custom_headers)).replace("1", "")
                    custom_sheet.update(range_name=f"{col_letter}1", values=[[header_name]], value_input_option='USER_ENTERED')
                    add_log_message(f"[✅ Sheets] Đã chèn cột '{header_name}' vào File 2 Custom.")
            except Exception as e_cust:
                add_log_message(f"[⚠️ ERROR Custom Sheet] {str(e_cust)}")
                
        # 3. Thêm vào File 3 Public (nếu is_public=True)
        if is_public and public_sheet_id:
            try:
                public_spreadsheet = client.open_by_key(public_sheet_id)
                public_sheet = public_spreadsheet.worksheet("Public")
                public_headers = public_sheet.row_values(1)
                if header_name not in public_headers:
                    if "Last updated" in public_headers:
                        last_updated_idx = public_headers.index("Last updated")
                        public_sheet.insert_cols([[header_name]], col=last_updated_idx + 1)
                        add_log_message(f"[✅ Sheets] Đã chèn cột '{header_name}' trước 'Last updated' vào File 3 Public.")
                    else:
                        public_sheet.add_cols(1)
                        public_headers.append(header_name)
                        col_letter = gspread.utils.rowcol_to_a1(1, len(public_headers)).replace("1", "")
                        public_sheet.update(range_name=f"{col_letter}1", values=[[header_name]], value_input_option='USER_ENTERED')
                        add_log_message(f"[✅ Sheets] Đã chèn cột '{header_name}' vào cuối File 3 Public.")
            except Exception as e_pub:
                add_log_message(f"[⚠️ ERROR Public Sheet] {str(e_pub)}")
                
        return True
    except Exception as e:
        add_log_message(f"[❌ ERROR Sheets Sync] Gặp lỗi khi cập nhật header Sheets: {str(e)}")
        return False

def append_column_to_docs(header_name, safe_name, is_public, description):
    """
    Tự động thêm đặc tả cột mới vào cuối bảng markdown của docs/pool_sheet_schema.md và docs/data_dictionary.md.
    """
    # 1. Cập nhật docs/pool_sheet_schema.md
    schema_path = os.path.join("docs", "pool_sheet_schema.md")
    if os.path.exists(schema_path):
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")
            
            # Tìm dòng cuối cùng của bảng cột
            last_idx = -1
            last_stt = 0
            for idx, line in enumerate(lines):
                if line.strip().startswith("|") and "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 2 and parts[1].isdigit():
                        last_idx = idx
                        last_stt = int(parts[1])
            
            if last_idx != -1:
                new_stt = last_stt + 1
                pub_check = "✅" if is_public else "❌"
                new_row = f"| {new_stt} | `{header_name}` | `{safe_name}` | {pub_check} | {description or 'Cột thuộc tính tùy biến động'} |"
                lines.insert(last_idx + 1, new_row)
                with open(schema_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                print(f"[✅ Docs] Đã cập nhật docs/pool_sheet_schema.md cho cột '{header_name}'.")
        except Exception as e_docs:
            print(f"[⚠️ ERROR append_column_to_docs schema] {str(e_docs)}")
            
    # 2. Cập nhật docs/data_dictionary.md
    dict_path = os.path.join("docs", "data_dictionary.md")
    if os.path.exists(dict_path):
        try:
            with open(dict_path, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.split("\n")
            
            # Tìm dòng cuối cùng của bảng Từ điển
            last_idx = -1
            last_stt = 0
            for idx, line in enumerate(lines):
                if line.strip().startswith("|") and "|" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 2 and parts[1].isdigit():
                        last_idx = idx
                        last_stt = int(parts[1])
            
            if last_idx != -1:
                new_stt = last_stt + 1
                new_row = f"| {new_stt} | `{header_name}` | `{safe_name}` | {description or 'Đặc tả cột tùy biến'} | Cột thuộc tính tùy biến tự tạo (Dynamic Schema). |"
                lines.insert(last_idx + 1, new_row)
                with open(dict_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                print(f"[✅ Docs] Đã cập nhật docs/data_dictionary.md cho cột '{header_name}'.")
        except Exception as e_docs:
            print(f"[⚠️ ERROR append_column_to_docs dict] {str(e_docs)}")


def ensure_pool_images_sheet_exists(spreadsheet):
    """
    Kiểm tra và tự động tạo tab Pool_Images nếu chưa tồn tại.
    """
    try:
        sheet = spreadsheet.worksheet("Pool_Images")
    except Exception:
        # Tạo mới tab
        sheet = spreadsheet.add_worksheet(title="Pool_Images", rows=1000, cols=60)
        # Khởi tạo header cơ bản
        headers = ["Mã", "Địa chỉ", "Loại", "Số lượng", "Ảnh 1", "Ảnh 2", "Ảnh 3"]
        sheet.update(range_name='A1:G1', values=[headers])
    return sheet


def ensure_pool_images_headers(sheet, target_images_count):
    """
    Mở rộng số cột tiêu đề ảnh trên sheet Pool_Images động nếu số lượng ảnh mới vượt quá số cột hiện tại.
    """
    try:
        # Đọc hàng 1
        headers = sheet.row_values(1)
    except Exception:
        headers = ["Mã", "Địa chỉ", "Loại", "Số lượng"]
        
    current_len = len(headers)
    required_len = 4 + target_images_count  # A, B, C, D + K ảnh
    
    if current_len < required_len:
        # Thêm các cột Ảnh mới
        for i in range(current_len - 3, target_images_count + 1):
            headers.append(f"Ảnh {i}")
        # Ghi đè lại hàng 1
        import gspread
        col_letter = gspread.utils.rowcol_to_a1(1, len(headers)).replace("1", "")
        try:
            sheet.update(range_name=f"A1:{col_letter}1", values=[headers])
        except Exception as e:
            print(f"[⚠️ WARNING] Không thể mở rộng header cho Pool_Images: {str(e)}")


def init_pool_images_rows(spreadsheet, tk_id, address, raw_images_list):
    """
    Khởi tạo 2 dòng crawl/self kề nhau trên tab Pool_Images cho mã căn tk_id nếu chưa tồn tại.
    Dòng crawl chứa danh sách ảnh thô. Dòng self để trống hoàn toàn các cột ảnh.
    """
    sheet = ensure_pool_images_sheet_exists(spreadsheet)
    
    # Đọc cột A (Mã) và C (Loại) để kiểm tra xem đã có dòng nào chưa
    try:
        col_a = sheet.col_values(1)
        col_c = sheet.col_values(3)
    except Exception as e:
        print(f"[⚠️ WARNING] Không thể đọc dữ liệu Pool_Images để kiểm tra: {str(e)}")
        return
        
    # Tìm xem tk_id đã có dòng crawl chưa
    has_crawl = False
    for idx, (m, l) in enumerate(zip(col_a, col_c)):
        if m.strip() == tk_id.strip() and l.strip() == "crawl":
            has_crawl = True
            break
            
    if not has_crawl:
        # Chưa có, tiến hành chèn cặp dòng mới kề sát nhau vào cuối bảng
        # Mở rộng số cột của sheet nếu số lượng ảnh cào lớn hơn số cột hiện tại
        ensure_pool_images_headers(sheet, len(raw_images_list))
        
        # Dòng crawl
        crawl_row = [tk_id, address, "crawl", len(raw_images_list)] + raw_images_list
        # Dòng self (trống các cột ảnh)
        self_row = [tk_id, address, "self", 0]
        
        try:
            # Ghi cả 2 dòng kề nhau vào cuối
            next_idx = len(col_a) + 1
            if next_idx < 2:
                next_idx = 2
            
            # Tự động mở rộng số dòng nếu vượt quá giới hạn hiện tại của sheet
            current_row_count = sheet.row_count
            required_rows = next_idx + 1
            if required_rows > current_row_count:
                rows_to_add = max(100, required_rows - current_row_count)
                sheet.add_rows(rows_to_add)
            
            import gspread
            col_letter = gspread.utils.rowcol_to_a1(1, max(len(crawl_row), len(self_row))).replace("1", "")
            sheet.update(range_name=f"A{next_idx}:{col_letter}{next_idx+1}", values=[crawl_row, self_row], value_input_option='USER_ENTERED')
            print(f"[✅ Backup] Khởi tạo thành công 2 dòng crawl/self kề nhau cho căn {tk_id} trên Pool_Images.")
        except Exception as e:
            print(f"[❌ LỖI] Lỗi chèn dòng mới vào Pool_Images: {str(e)}")


def update_pool_images_crawl_row(spreadsheet, tk_id, address, raw_images_list):
    """
    Cập nhật danh sách ảnh thô mới cào về vào dòng crawl trên sheet Pool_Images.
    Bảo toàn dòng self nguyên vẹn.
    """
    sheet = ensure_pool_images_sheet_exists(spreadsheet)
    
    try:
        col_a = sheet.col_values(1)
        col_c = sheet.col_values(3)
    except Exception as e:
        print(f"[⚠️ WARNING] Không thể đọc dữ liệu Pool_Images để cập nhật: {str(e)}")
        return
        
    # Tìm dòng crawl của tk_id
    crawl_row_idx = -1
    for idx, (m, l) in enumerate(zip(col_a, col_c)):
        if m.strip() == tk_id.strip() and l.strip() == "crawl":
            crawl_row_idx = idx + 1 # 1-based index
            break
            
    if crawl_row_idx != -1:
        # Đã tìm thấy, tiến hành cập nhật
        # Mở rộng số cột của sheet nếu số lượng ảnh mới lớn hơn số cột hiện tại
        ensure_pool_images_headers(sheet, len(raw_images_list))
        
        # Xóa sạch các cột ảnh cũ (chèn mảng trống rộng)
        try:
            # Ghi đè 100 cột trống bắt đầu từ cột E (ảnh 1) để xóa ảnh cũ
            empty_row = [""] * 100
            sheet.update(range_name=f"E{crawl_row_idx}:DD{crawl_row_idx}", values=[empty_row])
        except Exception as e_clear:
            print(f"[⚠️ WARNING] Không thể xóa ảnh cũ trên Pool_Images: {str(e_clear)}")
            
        # Ghi đè dòng mới
        crawl_row = [tk_id, address, "crawl", len(raw_images_list)] + raw_images_list
        import gspread
        col_letter = gspread.utils.rowcol_to_a1(1, len(crawl_row)).replace("1", "")
        try:
            sheet.update(range_name=f"A{crawl_row_idx}:{col_letter}{crawl_row_idx}", values=[crawl_row], value_input_option='USER_ENTERED')
            print(f"[✅ Backup] Cập nhật thành công dòng crawl cho căn {tk_id} trên Pool_Images.")
        except Exception as e:
            print(f"[❌ LỖI] Lỗi cập nhật dòng crawl trên Pool_Images: {str(e)}")


def update_pool_images_self_row(spreadsheet, tk_id, address, curated_images_list):
    """
    Cập nhật danh sách ảnh đã biên tập (curated) vào dòng self trên sheet Pool_Images.
    """
    sheet = ensure_pool_images_sheet_exists(spreadsheet)
    
    try:
        col_a = sheet.col_values(1)
        col_c = sheet.col_values(3)
    except Exception as e:
        print(f"[⚠️ WARNING] Không thể đọc dữ liệu Pool_Images để cập nhật self: {str(e)}")
        return
        
    # Tìm dòng self của tk_id
    self_row_idx = -1
    for idx, (m, l) in enumerate(zip(col_a, col_c)):
        if m.strip() == tk_id.strip() and l.strip() == "self":
            self_row_idx = idx + 1 # 1-based index
            break
            
    if self_row_idx != -1:
        # Đã tìm thấy, tiến hành cập nhật
        # Mở rộng số cột của sheet nếu số lượng ảnh mới lớn hơn số cột hiện tại
        ensure_pool_images_headers(sheet, len(curated_images_list))
        
        # Xóa sạch các cột ảnh cũ (chèn mảng trống rộng)
        try:
            empty_row = [""] * 100
            sheet.update(range_name=f"E{self_row_idx}:DD{self_row_idx}", values=[empty_row])
        except Exception as e_clear:
            print(f"[⚠️ WARNING] Không thể xóa ảnh cũ trên Pool_Images: {str(e_clear)}")
            
        # Ghi đè dòng mới
        self_row = [tk_id, address, "self", len(curated_images_list)] + curated_images_list
        import gspread
        col_letter = gspread.utils.rowcol_to_a1(1, len(self_row)).replace("1", "")
        try:
            sheet.update(range_name=f"A{self_row_idx}:{col_letter}{self_row_idx}", values=[self_row], value_input_option='USER_ENTERED')
            print(f"[✅ Backup] Cập nhật thành công dòng self cho căn {tk_id} trên Pool_Images.")
        except Exception as e:
            print(f"[❌ LỖI] Lỗi cập nhật dòng self trên Pool_Images: {str(e)}")


# Tự động nạp các cột tùy biến khi import module
load_custom_columns()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="KHANG NGO NHÀ PHỐ - POOL LEGO CLI ENGINE")
    parser.add_argument('--action', required=True, choices=['sync-pool2-to-pool1', 'sync-pool1-to-pool2', 'recrawl-all'],
                        help="Hành động đồng bộ hoặc cào lại")
    parser.add_argument('--so_nha', help="Số nhà (dành cho sync-pool1-to-pool2)")
    parser.add_argument('--duong', help="Tên đường (dành cho sync-pool1-to-pool2)")
    parser.add_argument('--tk_id', help="Mã căn (tùy chọn cho sync-pool2-to-pool1)")
    
    args = parser.parse_args()
    
    if args.action == 'sync-pool2-to-pool1':
        res = sync_between_databases("Pool2", "Pool1", tk_id=args.tk_id)
        print(res.get("message"))
    elif args.action == 'sync-pool1-to-pool2':
        if not args.so_nha or not args.duong:
            print("[❌] Thiếu tham số --so_nha hoặc --duong cho đồng bộ ngược.")
            sys.exit(1)
        res = sync_between_databases("Pool1", "Pool2", so_nha=args.so_nha, duong=args.duong)
        print(res.get("message"))
    elif args.action == 'recrawl-all':
        res = recrawl_all_listings()
        print(res.get("message"))
