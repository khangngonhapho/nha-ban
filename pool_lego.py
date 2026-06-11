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
from datetime import datetime

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
    "Ảnh 21", "Ảnh 22", "Ảnh 23", "Ảnh 24", "Ảnh 25"
]

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
    
    Args:
        input_str (str): Chuỗi tiếng Việt cần khử dấu.
        
    Returns:
        str: Chuỗi không dấu tương ứng. Trả về "" nếu rỗng hoặc None.
        
    Storage:
        RAM (Không lưu đĩa).
    """
    if not input_str:
        return ""
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỊịỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
    s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
    res = []
    for c in input_str:
        idx = s1.find(c)
        if idx != -1:
            res.append(s0[idx])
        else:
            res.append(c)
    return "".join(res)

def get_safe_col_name(header):
    """
    Chuyển đổi nhãn cột tiếng Việt có dấu thành tên cột SQLite hợp lệ.
    
    Args:
        header (str): Nhãn tiêu đề tiếng Việt.
        
    Returns:
        str: Tên cột SQLite an toàn (snake_case).
        
    Storage:
        RAM (Không lưu đĩa).
    """
    if not header:
        return ""
    no_accent = remove_accents(header)
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', no_accent)
    cleaned = re.sub(r'_+', '_', cleaned)
    cleaned = cleaned.strip('_')
    return cleaned

def gen_id_khang_ngo_python(so_nha, duong, quan):
    """
    Tự động sinh mã ID Khang Ngô độc nhất dựa trên số nhà, tên đường, tên quận.
    
    Args:
        so_nha (str): Số nhà thô.
        duong (str): Tên đường thô.
        quan (str): Tên quận thô.
        
    Returns:
        str: Mã ID Khang Ngô tự sinh.
        
    Storage:
        RAM (Không lưu đĩa).
    """
    so_nha = str(so_nha or "").strip()
    if '+' in so_nha:
        so_nha = so_nha.split('+')[0].strip()
    duong = str(duong or "").strip()
    quan = str(quan or "").strip()
    
    digit_map = {
        '1': 'M', '2': 'H', '3': 'B', '4': 'A', '5': 'N',
        '6': 'S', '7': 'Z', '8': 'T', '9': 'C', '0': 'O',
        '/': 'I', '.': 'I'
    }
    ma_so_nha = ""
    for char in so_nha:
        if char in digit_map:
            ma_so_nha += digit_map[char]
        elif re.match(r'[a-zA-Z]', char):
            ma_so_nha += char.lower()
            
    normalized_duong = duong
    if re.search(r'cách mạng tháng (tám|8)|cmt8', normalized_duong, re.I):
        normalized_duong = "CMTT"
    elif re.search(r'ba tháng hai|3 tháng 2|3/2|3-2', normalized_duong, re.I):
        normalized_duong = "BTH"
    elif re.search(r'đường số (\d+)', normalized_duong, re.I):
        match = re.search(r'đường số (\d+)', normalized_duong, re.I)
        normalized_duong = "DS" + match.group(1)
        
    abbr_duong = ""
    if normalized_duong in ["CMTT", "BTH"] or normalized_duong.startswith("DS"):
        abbr_duong = normalized_duong
    else:
        no_tones = remove_accents(normalized_duong)
        words = no_tones.split()
        for word in words:
            if len(word) > 0:
                abbr_duong += word[0].upper()
                
    reversed_duong = abbr_duong[::-1]
    combined = ma_so_nha + "I" + reversed_duong
    if len(combined) > 1:
        combined = combined[0] + "W" + combined[1:]
    else:
        combined = combined + "W"
    return combined

def get_db_file():
    """
    Xác định và trả về đường dẫn tệp tin SQLite đang được hệ thống kích hoạt.
    
    Returns:
        str: Đường dẫn tệp tin SQLite.
        
    Storage:
        RAM (Không lưu đĩa).
    """
    try:
        config_file = "settings.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                if cfg.get("active_pool_system") == "Pool2":
                    return "raw_archive_v2.db"
    except Exception:
        pass
    return "raw_archive.db"

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

    # Xác định pool system đang hoạt động
    is_pool2 = False
    try:
        config_file = "settings.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
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
            "Chieu_dai TEXT"
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
            tk_id TEXT,
            image_url TEXT,
            cloudinary_url TEXT,
            role TEXT,
            sequence_index INTEGER,
            edited_by TEXT,
            FOREIGN KEY(tk_id) REFERENCES listings_v2(tk_id) ON DELETE CASCADE
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
            Criteria_Khoang_cach_duong_oto TEXT
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
                "Criteria_Khoang_cach_duong_oto"
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
            "Chieu_dai TEXT"
        ]

        for header in POOL_HEADERS:
            col_name = get_safe_col_name(header)
            columns_def.append(f"`{col_name}` TEXT")
            
        create_table_sql = f"CREATE TABLE IF NOT EXISTS listings ({', '.join(columns_def)})"
        cursor.execute(create_table_sql)
        conn.commit()

        # Di cư tự động (Migration) cho listings Pool1
        try:
            cursor.execute("PRAGMA table_info(listings)")
            existing_cols = [row[1] for row in cursor.fetchall()]
            
            if "Chieu_dai" not in existing_cols:
                cursor.execute("ALTER TABLE listings ADD COLUMN Chieu_dai TEXT")
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
        
    conn = sqlite3.connect(db_file, timeout=30.0)
    cursor = conn.cursor()
    
    # Xác định pool system đang hoạt động
    is_pool2 = False
    try:
        config_file = "settings.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
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
            metadata["System ID"] = f"SYS-{datetime.now().strftime('%Y%m%d').upper()}-{random.randint(100, 999)}"
        if "Mã Hàng" not in metadata and "ma_hang" not in metadata and "Ma_Hang" not in metadata:
            parts = tk_id.split('-')
            suffix = parts[-1].upper() if parts else ""
            metadata["Mã Hàng"] = f"TK-{suffix}"

    for key, val in metadata.items():
        safe_col = key if key in explicit_criteria_cols else get_safe_col_name(key)
        # Chỉ giữ lại những cột thực sự tồn tại trong CSDL mục tiêu
        if safe_col in db_cols and safe_col not in ["tk_id", "status", "raw_images_tk_json", "raw_drive_images_json", "curated_config_json"]:
            cleaned_metadata[safe_col] = str(val) if val is not None else ""

    # Lưu hoặc Cập nhật bảng
    existing = cursor.execute(f"SELECT tk_id FROM {target_table} WHERE tk_id = ?", (tk_id,)).fetchone()
    
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
        
    if existing:
        update_parts = ["status = ?", "raw_images_tk_json = ?"]
        values = ["raw_text", raw_images_tk_json_val]
        
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
        
        for safe_col, val in cleaned_metadata.items():
            columns.append(f"`{safe_col}`")
            placeholders.append("?")
            values.append(val)
            
        insert_sql = f"INSERT INTO {target_table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(insert_sql, values)
        
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

def publish_listing(tk_id, get_google_credentials, load_config, add_log_message, db_file=None):
    """
    Thực hiện đồng bộ xuất bản dữ liệu của một căn nhà từ SQLite local lên Google Sheets trực tuyến.
    Tự động kiểm tra trùng Mã Hàng để chép đè có chọn lọc hoặc chèn dòng mới ở cuối bảng Table.
    Đồng thời đồng bộ mã ID Khang Ngô mới sang sheet Source và cập nhật trạng thái trong SQLite.
    
    Args:
        tk_id (str): Mã căn cần xuất bản.
        get_google_credentials (func): Hàm callback lấy credentials xác thực Google Cloud.
        load_config (func): Hàm callback nạp cấu hình hệ thống settings.
        add_log_message (func): Hàm callback ghi log.
        db_file (str/None): Tên file database.
        
    Returns:
        dict: Chứa status ('success'/'warning'), published_to_cloud (bool), message và row_data.
        
    Storage:
        Cập nhật Google Sheets trực tuyến và cập nhật status, Last_Sync trong SQLite.
    """
    if not db_file:
        db_file = get_db_file()
        
    if not os.path.exists(db_file):
        return {"status": "error", "message": "Database không tồn tại"}
        
    # Xác định bảng listings động
    is_pool2 = False
    try:
        config_file = "settings.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                if cfg.get("active_pool_system") == "Pool2":
                    is_pool2 = True
    except Exception:
        pass
    listings_table = "listings_v2" if is_pool2 else "listings"

    conn = sqlite3.connect(db_file, timeout=30.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
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
    if is_pool2:
        try:
            # Fetch images from listings_images since listings_v2 has no image columns
            cursor.execute(
                "SELECT image_url, cloudinary_url, role, sequence_index FROM listings_images WHERE tk_id = ? ORDER BY sequence_index ASC", 
                (tk_id,)
            )
            img_rows = cursor.fetchall()
            
            diagrams = []
            facades = []
            alleys = []
            interiors = []
            for img_url, cld_url, role, seq in img_rows:
                url = cld_url if cld_url else img_url
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
        if d.get("custom_Huong"): d["Huong"] = d["custom_Huong"]
    
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
    sheet_id = cfg.get("sheet_id")
    
    next_row = 3
    sheet = None
    existing_row_index = None
    
    if creds and sheet_id:
        try:
            import gspread
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(sheet_id)
            
            try:
                sheet = spreadsheet.worksheet("Pool")
            except Exception:
                try:
                    sheet = spreadsheet.worksheet("Source")
                except Exception:
                    sheet = spreadsheet.get_worksheet(0)
                    
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
                    next_row = table_end_row
                    add_log_message(f"[ℹ] Phát hiện Table chính thức kết thúc ở dòng {table_end_row}. Thực hiện chèn tại dòng {next_row} để tự động mở rộng Table và kế thừa format.")
                else:
                    try:
                        next_row = len(sheet.get_all_values()) + 1
                    except Exception as e:
                        add_log_message(f"[⚠️ WARNING] Không lấy được số dòng hiện tại của Sheet, fallback về mặc định: {str(e)}")
                        next_row = 3
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
            
        IMAGE_HEADERS = [
            "Hình Nhận Diện",
            "Sơ đồ thửa đất 1", "Sơ đồ thửa đất 2", "Sơ đồ thửa đất 3", "Sơ đồ thửa đất 4", "Sơ đồ thửa đất 5",
            "Hình Mặt Tiền",
            "Hình Hẻm 1", "Hình Hẻm 2", "Hình Hẻm 3", "Hình Hẻm 4", "Hình Hẻm 5", 
            "Hình Hẻm 6", "Hình Hẻm 7", "Hình Hẻm 8", "Hình Hẻm 9", "Hình Hẻm 10",
            "Ảnh 1", "Ảnh 2", "Ảnh 3", "Ảnh 4", "Ảnh 5", "Ảnh 6", "Ảnh 7", "Ảnh 8",
            "Ảnh 9", "Ảnh 10", "Ảnh 11", "Ảnh 12", "Ảnh 13", "Ảnh 14", "Ảnh 15",
            "Ảnh 16", "Ảnh 17", "Ảnh 18", "Ảnh 19", "Ảnh 20", 
            "Ảnh 21", "Ảnh 22", "Ảnh 23", "Ảnh 24", "Ảnh 25",
            "Ảnh Public (VD: 1,3,5)", "Ảnh Hẻm Public (VD: 1,2)",
            "Last Crawl",
            "Mã Khang Ngô (ID)"
        ]
        
        for idx, header in enumerate(POOL_HEADERS):
            if header in IMAGE_HEADERS:
                safe_col = get_safe_col_name(header)
                val = d.get(safe_col, "")
                if header == "Hình Nhận Diện":
                    val = f"=IMAGE(AD{existing_row_index})"
                elif header == "Last Crawl":
                    val = d.get("Last_Crawl", "") or datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                
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
                val = f"SYS-{datetime.now().strftime('%Y%M%d').upper()}-{random.randint(100, 999)}"
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
            row_data.append(val_str)
            row_data_escaped.append(escape_tsv_field(val_str))
        
    if sheet:
        try:
            if existing_row_index:
                add_log_message(f"[⚡] Đang chép đè dòng dữ liệu lên Sheet '{sheet.title}' (dòng {existing_row_index})...")
                sheet.update(range_name=f"A{existing_row_index}:DZ{existing_row_index}", values=[row_data], value_input_option='USER_ENTERED')
            else:
                add_log_message(f"[⚡] Đang chèn chốt dòng mới lên Sheet '{sheet.title}' (dòng {next_row} - chèn để thừa hưởng định dạng bảng)...")
                sheet.insert_row(row_data, index=next_row, value_input_option='USER_ENTERED')
            
            source_sheet_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
            try:
                source_spreadsheet = client.open_by_key(source_sheet_id)
                source_sheet = source_spreadsheet.worksheet("Source")
                source_values = source_sheet.get_all_values()
                
                system_id = d.get("System_ID", "")
                if system_id:
                    found_source_row_idx = -1
                    for s_idx, s_row in enumerate(source_values[1:], start=2):
                        if len(s_row) > 37 and s_row[37].strip() == system_id:
                            found_source_row_idx = s_idx
                            break
                    
                    if found_source_row_idx > -1:
                        new_ma_kn = d.get("Ma_Khang_Ngo_ID", "")
                        if new_ma_kn:
                            add_log_message(f"[⚡] Đồng bộ Mã Khang Ngô '{new_ma_kn}' sang cột id của sheet Source (dòng {found_source_row_idx})...")
                            source_sheet.update_cell(found_source_row_idx, 4, new_ma_kn)
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
