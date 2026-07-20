#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==================================================
KHANG NGÔ NHÀ PHỐ - LOCAL CURATOR SERVER (Flask)
Phục vụ Mini-App Biên tập & Quản lý Rổ hàng 2000 Căn
==================================================
"""

import os
import sys
import time
import json
import sqlite3

# Tối ưu hóa SQLite WAL mode và Timeout chống lỗi "database disk image is malformed" / "database is locked"
_orig_sqlite_connect = sqlite3.connect
def robust_sqlite_connect(database, timeout=30.0, *args, **kwargs):
    conn = _orig_sqlite_connect(database, timeout=max(timeout, 30.0), *args, **kwargs)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=30000;")
    except Exception:
        pass
    return conn
sqlite3.connect = robust_sqlite_connect

import re
import random
import subprocess
import threading
from datetime import datetime
import requests
import ssl
from requests.adapters import HTTPAdapter
from urllib3.util import create_urllib3_context

# Khắc phục lỗi SSL: UNEXPECTED_EOF_WHILE_READING với các server đằng sau Cloudflare (OpenSSL 3.0+ / Python 3.10+)
_orig_init_poolmanager = HTTPAdapter.init_poolmanager

def _robust_init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
    try:
        ctx = create_urllib3_context()
        if hasattr(ssl, "OP_IGNORE_UNEXPECTED_EOF"):
            ctx.options |= ssl.OP_IGNORE_UNEXPECTED_EOF
        else:
            ctx.options |= 4
            ctx.options |= 0x80000
        pool_kwargs['ssl_context'] = ctx
    except Exception:
        pass
    return _orig_init_poolmanager(self, connections, maxsize, block, **pool_kwargs)

HTTPAdapter.init_poolmanager = _robust_init_poolmanager

import hashlib
import fetcher
from flask import Flask, jsonify, request, Response

def safe_str(val):
    if val is None:
        return ""
    return str(val).strip()

# Lưu trữ sys.stdout gốc tại thời điểm khởi chạy để tránh vòng lặp đệ quy khi chuyển hướng stdout của thread cào
ORIGINAL_STDOUT = sys.stdout

# Xác định thư mục dự án gốc (PROJECT_ROOT) thông minh để luôn trỏ đúng SQLite có dữ liệu
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    # Tìm kiếm file SQLite theo thứ tự ưu tiên tăng dần các cấp thư mục cha
    c1 = os.path.join(exe_dir, "raw_archive.db")
    c2 = os.path.join(os.path.dirname(exe_dir), "raw_archive.db")
    c3 = os.path.join(os.path.dirname(os.path.dirname(exe_dir)), "raw_archive.db")
    
    if os.path.exists(c1):
        PROJECT_ROOT = exe_dir
    elif os.path.exists(c2):
        PROJECT_ROOT = os.path.dirname(exe_dir)
    elif os.path.exists(c3):
        PROJECT_ROOT = os.path.dirname(os.path.dirname(exe_dir))
    else:
        # Nếu không thấy db ở đâu, tự động lùi về thư mục dự án gốc khi chạy trong dist\KhangNgoCurator\
        if os.path.basename(exe_dir).lower() == 'khangngocurator' and os.path.basename(os.path.dirname(exe_dir)).lower() == 'dist':
            PROJECT_ROOT = os.path.dirname(os.path.dirname(exe_dir))
        else:
            PROJECT_ROOT = exe_dir
else:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Đảm bảo CWD luôn là PROJECT_ROOT để các tiến trình cào tin và lưu file hoạt động chính xác
os.chdir(PROJECT_ROOT)

# Chuẩn hóa thư mục static tuyệt đối động để tránh lỗi 404 khi chạy dưới dạng EXE đóng gói
static_folder = os.path.join(PROJECT_ROOT, 'static')

# Giải phóng port 5000 nếu bị kẹt
def free_ports():
    try:
        import subprocess
        output = subprocess.check_output("netstat -aon", shell=True).decode('utf-8', errors='ignore')
        for line in output.strip().split('\n'):
            if "LISTENING" in line and (":5000" in line or ":5001" in line):
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if int(pid) != os.getpid():
                        subprocess.run(f"taskkill /f /pid {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

# free_ports() đã được chuyển vào khối __main__ để tránh tự sát server khi import module


from curator_html_data import CURATOR_HTML_CONTENT

# Khởi tạo Flask với static folder tuyệt đối
app = Flask(__name__, static_folder=static_folder, static_url_path='/static')

import pool_lego
from pool_lego import POOL_HEADERS, remove_accents, get_safe_col_name, gen_id_khang_ngo_python, get_db_file, init_db

# File cấu hình & cơ sở dữ liệu (Dùng đường dẫn tuyệt đối dựa trên PROJECT_ROOT)
DB_FILE = os.path.abspath(os.path.join(PROJECT_ROOT, get_db_file()))

def backup_database():
    """Tự động sao lưu database SQLite sang thư mục đồng bộ an toàn dạng tĩnh"""
    try:
        if not os.path.exists(DB_FILE):
            return
        import shutil
        # Thư mục backup lưu trong thư mục đồng bộ Drive dưới dạng file tĩnh
        # Giúp tránh việc Drive khóa tệp .db live đang được ghi bởi ứng dụng
        backup_dir = "d:/LHTBrain/BDS_Backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Lấy danh sách các bản backup hiện có
        backups = sorted(
            [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.startswith("raw_archive_backup_")],
            key=os.path.getmtime
        )
        
        # Chỉ sao lưu nếu CSDL có sự thay đổi (mtime mới hơn bản backup gần nhất)
        if backups:
            latest_backup = backups[-1]
            if os.path.getmtime(DB_FILE) <= os.path.getmtime(latest_backup):
                # Không có thay đổi gì từ lần backup trước, bỏ qua để tránh ghi file thừa trùng lặp
                return
                
        db_basename = os.path.splitext(os.path.basename(DB_FILE))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{db_basename}_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_name)
        shutil.copy2(DB_FILE, backup_path)
        add_log_message(f"[💾 BACKUP] Tự động sao lưu database thành công: {backup_name}")
        
        # Thêm bản mới vào danh sách để tính toán xoay vòng
        backups.append(backup_path)
        
        # Giữ lại tối đa 10 bản sao lưu gần nhất (dung lượng nhẹ ~27MB/file)
        while len(backups) > 10:
            try:
                os.remove(backups.pop(0))
            except Exception:
                pass
    except Exception as e:
        add_log_message(f"[⚠️ WARNING] Không thể tự động sao lưu database: {str(e)}")

LISTINGS_TABLE = "listings_v2" if "raw_archive_v2.db" in DB_FILE else "listings"
CONFIG_FILE = os.path.abspath(os.path.join(PROJECT_ROOT, "settings.json"))
COOKIE_FILE = os.path.abspath(os.path.join(PROJECT_ROOT, "thienkhoi_cookie.txt"))
CREDENTIALS_FILE = os.path.abspath(os.path.join(PROJECT_ROOT, "credentials.json"))

# Helper functions (remove_accents, get_safe_col_name, gen_id_khang_ngo_python) are imported from pool_lego

def normalize_listing_for_client(row):
    if not row:
        return {}
    d = dict(row)
    
    # Map linh hoạt và an toàn các key từ SQLite sang Client format (hỗ trợ cả 2 định dạng)
    mapping = {
        "last_crawl": ["Last_Crawl", "last_crawl"],
        "Tieu_de_Public": ["Tieu_de_Public", "Ti_u____Public"],
        "Mo_ta_Public": ["Mo_ta_Public", "M__t__Public"],
        "Noi_dung_chinh": ["Noi_dung_chinh", "N_i_dung_ch_nh"],
        "Mo_ta_chi_tiet": ["Mo_ta_chi_tiet", "M__t__chi_ti_t"],
        "Ngo_So_nha": ["Ngo_So_nha", "Ng__S__nh_"],
        "Duong": ["Duong", "___ng"],
        "Phuong": ["Phuong", "Ph__ng"],
        "Quan": ["Quan", "Qu_n"],
        "Phuong_cu_AI_": ["Phuong_cu_AI", "Phuong_cu_AI_", "Ph__ng_c___AI_"],
        "Ma_Khang_Ngo_ID": ["Ma_Khang_Ngo_ID", "M__Khang_Ng___ID_"],
        "DT_Thuc_te": ["DT_Thuc_te", "DT_Th_c_t_"],
        "DT_Tren_so": ["DT_Tren_so", "DT_Tr_n_s_"],
        "So_Tang": ["So_Tang", "S__T_ng"],
        "Mat_Tien": ["Mat_Tien", "M_t_Ti_n"],
        "Chieu_dai": ["Chieu_dai", "Chi_u_dai"],
        "So_phong_ngu": ["So_phong_ngu", "S__ph_ng_ng_", "bedrooms"],
        "So_nha_ve_sinh": ["So_nha_ve_sinh", "S__nh__v__sinh", "restrooms"],
        "Gia_chao": ["Gia_chao", "Gi__ch_o"],
        "Gia_Public": ["Gia_Public", "Gi__Public"],
        "Phan_lo_i_Hem": ["Phan_loai_Hem", "Phan_lo_i_Hem", "Ph_n_lo_i_H_m"],
        "Duong_truoc_nha_m": ["Duong_truoc_nha_m", "___ng_tr__c_nh___m_", "minimumRoadWidth"],
        "Tinh_trang_nha": ["Tinh_trang_nha", "T_nh_tr_ng_nh_"],
        "Danh_gia_Admin": ["Danh_gia_Admin", "__nh_gi___Admin_"],
        "Ngu_tret_Admin": ["Ngu_tret_Admin", "Ng__tr_t__Admin_"],
        "CHDV_Admin": ["CHDV_Admin", "CHDV__Admin_"],
        "Ten_Dau_Chu_Hop_dong": ["Ten_Dau_Chu_Hop_dong", "T_n___u_Ch___H_p___ng_", "Ten_Dau_Chu"],
        "Dien_thoai_Dau_Chu": ["Dien_thoai_Dau_Chu", "_i_n_tho_i___u_Ch_"],
        "Diem_Facebook": ["Diem_Facebook", "_i_m_Facebook"],
        "Ma_Hang": ["Ma_Hang", "M__H_ng"],
        "Tinh": ["Tinh", "T_nh"],
        "custom_dt_so": ["custom_dt_so"],
        "custom_dt_thuc_te": ["custom_dt_thuc_te"],
        "latitude": ["latitude"],
        "longitude": ["longitude"]
    }
    
    for client_key, db_keys in mapping.items():
        val = ""
        for db_key in db_keys:
            if db_key in d:
                if d[db_key] is not None:
                    val = d[db_key]
                    break
        d[client_key] = val
        
    # Áp dụng các trường custom_* từ listings_custom_v2 nếu có (chỉ ở chế độ Pool2)
    if "custom_Ma_Khang_Ngo" in d:
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
        phuong_val = d.get("custom_phuong") or d.get("custom_Phuong")
        if phuong_val: d["Phuong"] = phuong_val
        quan_val = d.get("custom_quan") or d.get("custom_Quan")
        if quan_val: d["Quan"] = quan_val
        if d.get("custom_latitude"): d["latitude"] = d["custom_latitude"]
        if d.get("custom_longitude"): d["longitude"] = d["custom_longitude"]
        
        # Nhóm Tiêu chí
        if d.get("custom_Criteria_Duong_truoc_nha"): d["Criteria_Duong_truoc_nha"] = d["custom_Criteria_Duong_truoc_nha"]
        if d.get("custom_Criteria_Noi_that"): d["Criteria_Noi_that"] = d["custom_Criteria_Noi_that"]
        if d.get("custom_Criteria_Thang_may"): d["Criteria_Thang_may"] = d["custom_Criteria_Thang_may"]
        if d.get("custom_Criteria_Loai_ngo"): d["Criteria_Loai_ngo"] = d["custom_Criteria_Loai_ngo"]
        if d.get("custom_Criteria_Khoang_cach_bai_do_xe"): d["Criteria_Khoang_cach_bai_do_xe"] = d["custom_Criteria_Khoang_cach_bai_do_xe"]
        if d.get("custom_Criteria_Kinh_doanh_Dong_tien"): d["Criteria_Kinh_doanh_Dong_tien"] = d["custom_Criteria_Kinh_doanh_Dong_tien"]
        if d.get("custom_Criteria_Huong_nha"): d["Criteria_Huong_nha"] = d["custom_Criteria_Huong_nha"]
        if d.get("custom_Criteria_Khoang_cach_duong_oto"): d["Criteria_Khoang_cach_duong_oto"] = d["custom_Criteria_Khoang_cach_duong_oto"]
        
    # Đồng bộ key Phuong_cu_AI không gạch dưới đề phòng client khác đọc
    d["Phuong_cu_AI"] = d["Phuong_cu_AI_"]
            
    # Parse các chuỗi JSON ảnh cho an toàn
    d["raw_images_tk"] = json.loads(d["raw_images_tk_json"]) if d.get("raw_images_tk_json") else []
    d["raw_drive_images"] = json.loads(d["raw_drive_images_json"]) if d.get("raw_drive_images_json") else []
    d["curated_config"] = json.loads(d["curated_config_json"]) if d.get("curated_config_json") else None
    
    if LISTINGS_TABLE == "listings_v2":
        conn_img = None
        try:
            # Query all images from listings_images since listings_v2 has no image columns
            conn_img = sqlite3.connect(DB_FILE, timeout=30.0)
            cursor_img = conn_img.cursor()
            img_rows = cursor_img.execute(
                "SELECT image_url, r2_url, role FROM listings_images WHERE tk_id = ? ORDER BY sequence_index ASC",
                (d.get("tk_id"),)
            ).fetchall()
            
            if img_rows:
                raw_tk_all = []
                raw_drive_all = []
                diagrams_raw = []
                
                for img_url, r2_url, role in img_rows:
                    raw_tk_all.append(img_url)
                    raw_drive_all.append(r2_url or img_url)
                    if role == "diagram":
                        diagrams_raw.append(img_url)
                
                d["raw_images_tk"] = raw_tk_all
                d["raw_drive_images"] = raw_drive_all
                
                # Populate Sơ đồ thửa đất 1 đến 5 for frontend compatibility mapping
                for idx in range(5):
                    col_name = get_safe_col_name(f"Sơ đồ thửa đất {idx+1}")
                    d[col_name] = diagrams_raw[idx] if idx < len(diagrams_raw) else ""
        except Exception as e_img:
            add_log_message(f"[⚠️ WARNING] Lỗi tải ảnh từ listings_images trong normalize: {str(e_img)}")
        finally:
            if conn_img:
                conn_img.close()
            
    return d

# Bộ đệm logs thời gian thực cho UI
LOGS_BUFFER = []
LOGS_LOCK = threading.Lock()

def add_log_message(msg):
    """Ghi log vào bộ đệm, in ra terminal và lưu file app.log"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    
    # In ra terminal gốc bằng cách write trực tiếp để tránh bị đệ quy xuyên qua LogStream
    try:
        ORIGINAL_STDOUT.write(formatted_msg + "\n")
        ORIGINAL_STDOUT.flush()
    except Exception:
        # Fallback cực kỳ an toàn
        pass
        
    # Ghi log bền vững vào file app.log trên đĩa cứng
    try:
        log_file_path = os.path.join(PROJECT_ROOT, "app.log")
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    except Exception:
        pass
        
    with LOGS_LOCK:
        LOGS_BUFFER.append(formatted_msg)
        # Giữ tối đa 1000 dòng log gần nhất
        if len(LOGS_BUFFER) > 1000:
            LOGS_BUFFER.pop(0)

def clean_prompt_content(content):
    """Lọc bỏ phần giới thiệu ở đầu Google Doc và bắt đầu chính xác từ câu lệnh phân vai của AI"""
    if not content:
        return content
    start_keywords = ["bạn hãy đóng vai là", "bạn là", "nhiệm vụ của bạn"]
    content_lower = content.lower()
    for kw in start_keywords:
        idx = content_lower.find(kw)
        if idx != -1:
            return content[idx:].strip()
    return content.strip()

def get_default_system_prompt():
    """Trả về default system prompt tối giản làm placeholder"""
    return (
        "Bạn hãy đóng vai là Đầu chủ Trà Mi - chuyên gia viết bài và định vị bất động sản. "
        "Hệ thống đang chạy chế độ dự phòng. Vui lòng kết nối đồng bộ cấu hình từ Google Sheets/Google Doc để cập nhật đầy đủ chỉ thị nghiệp vụ."
    )


# Cấu hình mặc định
DEFAULT_CONFIG = {
    "sheet_id": "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw",
    "pool2_raw_sheet_id": "",
    "pool2_custom_sheet_id": "",
    "pool2_public_sheet_id": "",
    "drive_folder_id": "10NcfOJ3_YBiPVc4FSK2uGGNs7MPmAFO8",
    "target_district": "",
    "search_url": "https://data.thienkhoi.com/Hang?iID_MaTinh=0&iID_HuongNha=0&iID_LoaiHang=0&iID_MaQuan=0&iID_MaPhuongXa=0&iTrangThai=0&iTuMatTien=0&iDenMatTien=0&iTuDienTich=0&iDenDienTich=0&iGiaChaoHopDong=0&iHeSoThanhTich=0&iGia=0&sGia=0&iTuGia=0&iDenGia=0&iPhanTramHoaHong=0&iDuongVao=0&iTuSoTang=0&iPhanTang=0&iDenSoTang=0&iSoPhongNgu=0&iSoToilet=0&iID_Nguon=0&sTaiKhoan=0908130555&iTaiKhoan=0&Menu=0&Page=1&PageSize=20&bCamKetChuan=False&bSigned=False&bHidden=0&iID_MaNguoiDungTao=0&iID_MaNguoiTuChoi=0&iDuAn=0&iTrangThaiSoDo=0&iBranch=0&blacklist=False&iKhoBank=0&iKhoHang=0&iID_MaNguoiDuyetBank=0&iID_MaNguoiBCDK=0&all=False&inside=False&tester=False",
    "crawler_limit": 5,
    "crawler_start_page": 1,
    "delay_house_min": 3.0,
    "delay_house_max": 6.0,
    "delay_page_min": 5.0,
    "delay_page_max": 10.0,
    "openai_api_base": "https://api.openai.com/v1",
    "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
    "prompt_google_doc_id": "1-VlvYmwY9_22dULAF4Xtlooa8A8VUfiV3OVU01OaoGE",
    "openai_system_prompt": get_default_system_prompt(),
    "json_ui_fields": ["Criteria_Duong_truoc_nha"],
    "json_ui_filters": [
        {
            "field": "Criteria_Duong_truoc_nha",
            "label": "Đường trước nhà",
            "type": "select",
            "options": [
                "",
                "Hẻm xe máy ( <2m)",
                "Ngõ ngách (2 - 2.5m)",
                "Ngõ 1 ô tô ( 2.5 -5m)",
                "Ngõ 2 ô tô tránh (5 - 7m)",
                "Ngõ 3 ô tô tránh (7 - 9m)",
                "Ngõ 4 ô tô tránh (9 - 11m)",
                "Ngõ 4 ô tô trở lên ( >11m)"
            ]
        }
    ]
}

def load_config():
    """Tải cấu hình từ file cục bộ, tự động fallback về mặc định nếu trường cấu hình trống rỗng"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_cfg = json.load(f)
                cfg = DEFAULT_CONFIG.copy()
                for k, v in user_cfg.items():
                    # Chỉ ghi đè nếu giá trị hợp lệ và không phải là chuỗi trống
                    if v is not None:
                        if isinstance(v, str) and not v.strip():
                            # Trọc vào chuỗi trống thì bỏ qua để lấy giá trị mặc định của DEFAULT_CONFIG
                            continue
                        cfg[k] = v
                return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    """Lưu cấu hình xuống file"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        add_log_message(f"[❌ LỖI] Không thể lưu cấu hình: {str(e)}")
        return False

def trim_tieu_de_bds(tieu_de):
    if not tieu_de:
        return ""
    tieu_de = tieu_de.strip()
    
    idx_bar = tieu_de.find(" | ")
    
    # A. BỘ LỌC PROGRAMMATIC SCRUBBER CHỐNG LẶP HẺM/XE HƠI KHI ĐẦU ĐÃ CÓ TIỀN TỐ HXH
    if tieu_de.upper().startswith("HXH ") and idx_bar != -1:
        tech_part = tieu_de[:idx_bar]
        usp_part = tieu_de[idx_bar + 3:].strip()
        
        duplicate_keywords = [
            r'hẻm\s+xe\s+hơi', r'hẻm\s+ô\s+tô', r'hẻm', r'ô\s+tô',
            r'xe\s+hơi', r'oto', r'đỗ\s+cửa', r'đỗ', r'đậu'
        ]
        
        cleaned_usp = usp_part
        for kw in duplicate_keywords:
            cleaned_usp = re.sub(rf'(?i){kw}', '', cleaned_usp)
            
        cleaned_usp = re.sub(r'\s+', ' ', cleaned_usp).strip()
        
        if cleaned_usp.lower().startswith("sat "):
            cleaned_usp = "Sát " + cleaned_usp[4:]
        elif cleaned_usp.lower().startswith("sát "):
            cleaned_usp = "Sát " + cleaned_usp[4:]
            
        if cleaned_usp == "":
            tieu_de = tech_part
            idx_bar = -1
        else:
            cleaned_usp = cleaned_usp[0].upper() + cleaned_usp[1:]
            tieu_de = tech_part + " | " + cleaned_usp
            idx_bar = tieu_de.find(" | ")
            
    # 1. Tự động viết hoa chữ cái đầu tiên sau dấu " | "
    if idx_bar != -1:
        tech_part = tieu_de[:idx_bar]
        usp_part = tieu_de[idx_bar + 3:].strip()
        if len(usp_part) > 0:
            usp_part = usp_part[0].upper() + usp_part[1:]
        tieu_de = tech_part + " | " + usp_part
        
    return tieu_de

# ==================================================
# GOOGLE CLOUD SERVICE ACCOUNT CONNECTIVITY (DRIVE & SHEETS)
# ==================================================
LAST_CREDENTIALS_WARNING_TIME = 0

def get_google_credentials():
    """Tạo credentials từ credentials.json hoặc khangngo-admin-*.json nếu tồn tại (Hỗ trợ tự sửa và phục hồi lỗi JWT Signature)"""
    global LAST_CREDENTIALS_WARNING_TIME
    
    # Định nghĩa cache ở Home Directory (Tránh bị xóa bởi git clean hoặc lỗi drive ảo)
    home_dir = os.path.expanduser("~")
    bds_home_dir = os.path.join(home_dir, ".bds_khangngo")
    home_credentials_path = os.path.abspath(os.path.join(bds_home_dir, "credentials.json"))
    
    workspace_credentials_path = CREDENTIALS_FILE
    
    # 1. Tự phục hồi: Nếu ở Workspace thiếu credentials.json nhưng có cache local tại Home Directory
    if not os.path.exists(workspace_credentials_path) and os.path.exists(home_credentials_path):
        try:
            os.makedirs(os.path.dirname(workspace_credentials_path), exist_ok=True)
            import shutil
            shutil.copy2(home_credentials_path, workspace_credentials_path)
            add_log_message(f"[🛡️ SELF-HEALING] Tự động khôi phục credentials.json từ local cache về Workspace: '{workspace_credentials_path}'")
        except Exception:
            pass

    # --- CƠ CHẾ TỰ PHỤC HỒI (SELF-HEALING) NẾU THIẾU credentials.json (US-073.b) ---
    bak_paths = [
        os.path.join(PROJECT_ROOT, "credentials.json.bak"),
        os.path.abspath(os.path.join(PROJECT_ROOT, "..", "credentials.json.bak")),
        os.path.abspath(os.path.join(PROJECT_ROOT, "..", "..", "credentials.json.bak"))
    ]
    for bak_p in bak_paths:
        if os.path.exists(bak_p):
            dest_p = os.path.join(os.path.dirname(bak_p), "credentials.json")
            if not os.path.exists(dest_p):
                try:
                    import shutil
                    shutil.copy2(bak_p, dest_p)
                    add_log_message(f"[🛡️ SELF-HEALING] Phát hiện thiếu credentials.json nhưng có file backup. Đã tự động khôi phục tại: '{dest_p}'")
                except Exception as e_copy:
                    add_log_message(f"[⚠️ WARNING] Không thể tự động khôi phục credentials.json từ backup: {str(e_copy)}")
            break

    # Thu thập toàn bộ thư mục đích quét qua
    target_dirs = [
        PROJECT_ROOT,
        os.path.dirname(home_credentials_path),
        os.path.abspath(os.path.join(PROJECT_ROOT, "..")),
        os.path.abspath(os.path.join(PROJECT_ROOT, "..", "..")),
        os.path.abspath(os.path.join(PROJECT_ROOT, "..", "admin-nha-ban", "automation")),
        os.getcwd(),
        os.path.abspath(os.path.join(os.getcwd(), ".."))
    ]
    
    # Nếu chạy dưới dạng EXE đóng gói (frozen), kiểm tra thêm các đường dẫn lân cận file thực thi
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        target_dirs.insert(0, exe_dir)
        target_dirs.insert(1, os.path.dirname(exe_dir))
        target_dirs.insert(2, os.path.dirname(os.path.dirname(exe_dir)))
        
    # Tạo danh sách các ứng cử viên credentials (bao gồm credentials.json và khangngo-admin-*.json)
    import glob
    candidates = []
    for d in target_dirs:
        if not os.path.exists(d):
            continue
        p_cred = os.path.abspath(os.path.join(d, "credentials.json"))
        if os.path.exists(p_cred):
            candidates.append(p_cred)
        # Quét thêm các file định danh dịch vụ dạng khangngo-admin-*.json
        for p_wild in glob.glob(os.path.join(d, "khangngo-admin-*.json")):
            candidates.append(os.path.abspath(p_wild))
            
    # Loại bỏ các đường dẫn trùng lặp nhưng giữ nguyên thứ tự ưu tiên
    candidates = list(dict.fromkeys(candidates))
    
    from google.oauth2 import service_account
    import google.auth.transport.requests
    req = google.auth.transport.requests.Request()
    
    resolved_path = None
    creds_obj = None
    
    for path in candidates:
        try:
            scopes = [
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/spreadsheets'
            ]
            temp_creds = service_account.Credentials.from_service_account_file(path, scopes=scopes)
            # Kiểm tra nhanh token để xác thực chữ ký (Signature & Time validation)
            try:
                temp_creds.refresh(req)
                resolved_path = path
                creds_obj = temp_creds
                break
            except Exception as e_refresh:
                err_msg = str(e_refresh)
                # Nếu là lỗi chữ ký, hết hạn hoặc thông tin xác thực sai -> loại bỏ ứng cử viên này
                if "invalid_grant" in err_msg or "invalid_client" in err_msg or "signature" in err_msg.lower():
                    try:
                        ORIGINAL_STDOUT.write(f"[DEBUG OAuth] File '{path}' co chu ky hoac khoa khong hop le (JWT Signature/Grant error). Dang quet file tiep theo...\n")
                    except Exception:
                        pass
                    continue
                else:
                    # Lỗi mạng hoặc lỗi kết nối khác, mặc định file này có thể hợp lệ
                    resolved_path = path
                    creds_obj = temp_creds
                    break
        except Exception:
            continue
            
    if not resolved_path:
        # Chỉ in cảnh báo tối đa 1 lần mỗi 10 phút để tránh spam log liên tục
        current_time = time.time()
        if current_time - LAST_CREDENTIALS_WARNING_TIME > 600:
            paths_str = "\n  - ".join(f"'{p}'" for p in candidates)
            add_log_message(f"[⚠️ API WARNING] Không tìm thấy tệp xác thực credentials.json hợp lệ. Các vị trí đã quét:\n  - {paths_str}")
            LAST_CREDENTIALS_WARNING_TIME = current_time
        return None
        
    # 2. Đồng bộ cache và sửa lỗi: Nếu tìm thấy file credentials hợp lệ nhưng khác với credentials.json mặc định,
    # tự động sửa và copy đè lên credentials.json ở Workspace và Home cache để phục hồi hoạt động cho toàn bộ hệ thống.
    try:
        import shutil
        if resolved_path != workspace_credentials_path:
            shutil.copy2(resolved_path, workspace_credentials_path)
            shutil.copy2(resolved_path, workspace_credentials_path + ".bak")
            add_log_message(f"[🛡️ SELF-HEALING] Đã khôi phục credentials.json bằng key dịch vụ hoạt động tốt từ: '{resolved_path}'")
            
        if resolved_path != home_credentials_path:
            os.makedirs(os.path.dirname(home_credentials_path), exist_ok=True)
            shutil.copy2(resolved_path, home_credentials_path)
            shutil.copy2(resolved_path, home_credentials_path + ".bak")
            add_log_message(f"[🛡️ CACHE] Đã đồng bộ credentials.json hợp lệ vào cache local Home Directory: '{home_credentials_path}'")
    except Exception as e_repair:
        try:
            ORIGINAL_STDOUT.write(f"[DEBUG OAuth] Loi khi copy sua file credentials: {str(e_repair)}\n")
        except Exception:
            pass

    # Reset thời gian cảnh báo nếu tìm thấy file hợp lệ
    LAST_CREDENTIALS_WARNING_TIME = 0
    return creds_obj

def get_google_access_token(creds):
    """Lấy Access Token của Google Service Account phục vụ gọi REST API"""
    if not creds:
        return None
    try:
        import google.auth.transport.requests
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        return creds.token
    except Exception as e:
        add_log_message(f"[❌ LỖI] Không thể tạo access token: {str(e)}")
        return None

def fetch_google_doc_content(doc_id):
    """Tải nội dung text thô từ một Google Doc dựa trên ID hoặc link của Doc, hỗ trợ OAuth và Public fallback"""
    if not doc_id:
        return None
    doc_id = str(doc_id).strip()
    if "/" in doc_id:
        # Trích xuất ID từ URL Google Doc
        match = re.search(r"/document/d/([a-zA-Z0-9-_]+)", doc_id)
        if match:
            doc_id = match.group(1)
            
    content = None
    
    # Cách 1: Thử tải dùng Google API OAuth nếu có Credentials
    creds = get_google_credentials()
    if creds:
        token = get_google_access_token(creds)
        if token:
            url = f"https://www.googleapis.com/drive/v3/files/{doc_id}/export?mimeType=text/plain"
            headers = {
                "Authorization": f"Bearer {token}"
            }
            try:
                add_log_message(f"[🤖 GOOGLE DOC] Đang tải prompt từ Google Doc (OAuth) ID: {doc_id}...")
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    response.encoding = 'utf-8'
                    content = response.text
                    add_log_message("[✅ GOOGLE DOC] Đã tải prompt thành công bằng OAuth.")
                else:
                    add_log_message(f"[⚠️ GOOGLE DOC] Tải prompt OAuth thất bại, HTTP {response.status_code}")
            except Exception as e:
                add_log_message(f"[⚠️ GOOGLE DOC] Lỗi khi tải prompt bằng OAuth: {str(e)}")

    # Cách 2: Tải công khai dự phòng (Public Link) nếu OAuth thất bại hoặc không có Credentials
    if not content:
        url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
        try:
            add_log_message(f"[🤖 GOOGLE DOC] Đang tải prompt từ Google Doc (Public Link) ID: {doc_id}...")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                content = response.text
                add_log_message("[✅ GOOGLE DOC] Đã tải prompt thành công bằng Public Link.")
            else:
                add_log_message(f"[⚠️ GOOGLE DOC] Tải prompt Public Link thất bại, HTTP {response.status_code}")
        except Exception as e:
            add_log_message(f"[❌ GOOGLE DOC ERROR] Gặp lỗi khi tải prompt Public Link: {str(e)}")

    if content:
        if content.startswith('\ufeff'):
            content = content[1:]
        clean_content = clean_prompt_content(content)
        
        # Lưu vào cache cục bộ làm offline cache
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cache_file = os.path.join(script_dir, "system_prompt.txt")
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(clean_content)
            add_log_message("[💾 OFFLINE CACHE] Đã cập nhật bộ nhớ đệm system_prompt.txt thành công.")
        except Exception as cache_err:
            print(f"Lỗi ghi cache prompt cục bộ: {cache_err}")
            
        return clean_content
        
    return None

# ==================================================
# KHỞI CHẠY TIẾN TRÌNH CÀO (BACKGROUND THREAD - PACKAGED READY)
# ==================================================

ACTIVE_CRAWLER_THREAD = None
ACTIVE_CRAWLER_LOCK = threading.Lock()

def run_crawler_thread(url, cookie, district, limit, start_page=None):
    """
    Chạy fetcher.scrape_district trực tiếp trong Thread.
    Ghi đè hàm print() cục bộ bên trong fetcher để hứng logs an toàn,
    tránh hoàn toàn việc monkeypatch sys.stdout/stderr toàn cục gây lỗi đệ quy (RecursionError).
    """
    add_log_message(f"[🚀] KHỞI ĐỘNG TIẾN TRÌNH CÀO TỰ ĐỘNG - Quận: '{district}' | Trang bắt đầu: '{start_page or 'Tự động'}'")
    
    # Định nghĩa hàm print() thay thế cục bộ cho module fetcher
    def custom_print(*args, **kwargs):
        msg = " ".join(str(arg) for arg in args)
        add_log_message(msg)
        
    # Ghi đè cục bộ hàm print trong fetcher
    old_print = getattr(fetcher, 'print', print)
    fetcher.print = custom_print
    
    # Thiết lập bảo vệ ngắt tiến trình (sys.exit -> raise Exception)
    old_exit = sys.exit
    def safe_exit(code=0):
        raise RuntimeError(f"Crawl pipeline yêu cầu dừng với mã code {code}")
    sys.exit = safe_exit
    
    try:
        # Gọi trực tiếp hàm trong fetcher
        fetcher.scrape_district(url, cookie, limit, district, start_page)
        add_log_message("[🏁] Tiến trình cào đã hoàn tất thành công!")
    except RuntimeError as re_err:
        add_log_message(f"[⚠️ DỪNG SỚM] {str(re_err)}")
    except SystemExit:
        add_log_message("[🏁] Tiến trình cào dừng (SystemExit).")
    except Exception as e:
        add_log_message(f"[❌ LỖI] Lỗi tiến trình cào: {str(e)}")
    finally:
        # Khôi phục nguyên trạng
        fetcher.print = old_print
        sys.exit = old_exit
        # Sao lưu cơ sở dữ liệu tĩnh lên thư mục backup sau khi cào xong
        backup_database()

# ==================================================
# TẢI HÌNH ẢNH CỤC BỘ / GOOGLE DRIVE UPLOAD CHẠY NGẦM
# ==================================================
def download_image_with_retry(url, headers, retries=3):
    """Tải ảnh từ Thien Khoi với cơ chế thử lại"""
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                return r.content
            add_log_message(f"[⚠️ Thử lại] Tải ảnh thất bại HTTP {r.status_code}. Thử lại {attempt+1}/{retries}...")
        except Exception as e:
            add_log_message(f"[⚠️ Thử lại] Lỗi tải ảnh: {str(e)}. Thử lại {attempt+1}/{retries}...")
        time.sleep(2)
    return None

from PIL import Image, ImageOps
import io

def compress_image(image_bytes, max_size=(1600, 1600), quality=75):
    """Nén và resize ảnh JPEG để tối ưu dung lượng trước khi upload/lưu trữ"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Tự động xoay ảnh vật lý theo đúng tag EXIF trước khi nén để tránh lỗi quay ngang 90 độ
        try:
            img = ImageOps.exif_transpose(img)
        except Exception as exif_err:
            pass
        
        # Chuyển đổi sang RGB nếu là RGBA (tránh lỗi khi lưu JPEG)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            # Tạo background trắng
            background = Image.new("RGB", img.size, (255, 255, 255))
            mask = img.convert("RGBA").split()[3]
            background.paste(img, mask=mask)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
            
        # Resize giữ nguyên tỷ lệ (giới hạn chiều lớn nhất là 1600px)
        resample_filter = getattr(Image, 'Resampling', None)
        if resample_filter and hasattr(resample_filter, 'LANCZOS'):
            img.thumbnail(max_size, resample_filter.LANCZOS)
        else:
            img.thumbnail(max_size, getattr(Image, 'ANTIALIAS', Image.BICUBIC))
            
        # Lưu ra bytes
        out_bytes = io.BytesIO()
        img.save(out_bytes, format='JPEG', quality=quality, optimize=True)
        compressed_data = out_bytes.getvalue()
        
        # Chỉ lấy ảnh nén nếu dung lượng của nó nhỏ hơn ảnh gốc
        if len(compressed_data) < len(image_bytes):
            return compressed_data
        return image_bytes
    except Exception as e:
        # Fallback an toàn: nếu lỗi thì trả về ảnh gốc
        return image_bytes

def upload_image_to_drive(file_content, filename, folder_id, token):
    """Tải ảnh lên Google Drive thông qua REST API trực tiếp"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Tạo Metadata file
    metadata = {
        "name": filename,
        "parents": [folder_id] if folder_id else []
    }
    
    files = {
        "data": ("metadata", json.dumps(metadata), "application/json"),
        "file": (filename, file_content, "image/jpeg")
    }
    
    # 2. Multipart Upload
    r = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
        headers=headers,
        files=files,
        timeout=30
    )
    
    if r.status_code != 200:
        raise Exception(f"Google Drive API returned status {r.status_code}: {r.text}")
        
    file_id = r.json().get("id")
    
    # 3. Chia sẻ tệp công khai (Anyone can read)
    permission = {
        "role": "reader",
        "type": "anyone"
    }
    requests.post(
        f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
        headers=headers,
        json=permission,
        timeout=10
    )
    
    # Trả về link nhúng trực tiếp direct
    return f"https://lh3.googleusercontent.com/d/{file_id}"

def create_drive_folder(folder_name, parent_id, token):
    """Tạo thư mục con trên Drive phục vụ gom ảnh theo mã căn"""
    headers = {"Authorization": f"Bearer {token}"}
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id] if parent_id else []
    }
    
    r = requests.post(
        "https://www.googleapis.com/drive/v3/files",
        headers=headers,
        json=metadata,
        timeout=20
    )
    if r.status_code != 200:
        raise Exception(f"Không thể tạo thư mục Drive: {r.text}")
        
    return r.json().get("id")

def get_r2_subfolder(tk_id, row_dict):
    """Tính toán tên thư mục con R2: {uuid} - {so_nha} {duong}"""
    if not row_dict:
        return tk_id
        
    so_nha = ""
    so_nha_keys = ["Ngo_So_nha", "Ng__S__nh_", "custom_So_Nha"]
    for k in so_nha_keys:
        val = row_dict.get(k)
        if val is not None:
            so_nha = str(val).strip()
            break
            
    # Áp dụng luật số nhà phức hợp (chỉ lấy phần trước dấu cộng +)
    if "+" in so_nha:
        so_nha = so_nha.split("+")[0].strip()
        
    duong = ""
    duong_keys = ["Duong", "___ng"]
    for k in duong_keys:
        val = row_dict.get(k)
        if val is not None:
            duong = str(val).strip()
            break
            
    # Nếu không có số nhà và đường, fallback về tk_id
    if not so_nha and not duong:
        return tk_id
        
    # Khử dấu tiếng Việt để có tên thư mục ASCII an toàn
    import re
    from core.business_rules import remove_accents
    clean_so_nha = remove_accents(so_nha)
    clean_duong = remove_accents(duong)
    
    folder_name = f"{tk_id} - {clean_so_nha} {clean_duong}".strip()
    folder_name = re.sub(r'\s+', ' ', folder_name)
    return folder_name

def list_r2_objects(prefix):
    """Liệt kê các tệp tin trong R2 với prefix cho trước sử dụng ListObjectsV2 và Signature V4"""
    import hashlib
    import hmac
    import datetime
    import urllib.parse
    import xml.etree.ElementTree as ET
    
    cfg = load_config()
    r2_access_key = cfg.get("r2_access_key_id")
    r2_secret_key = cfg.get("r2_secret_access_key")
    r2_bucket = cfg.get("r2_bucket_name")
    account_id = cfg.get("cloudflare_account_id")
    
    if not (r2_access_key and r2_secret_key and r2_bucket and account_id):
        return []
        
    host = f"{r2_bucket}.{account_id}.r2.cloudflarestorage.com"
    params = {
        "list-type": "2",
        "prefix": prefix
    }
    
    canonical_query_parts = []
    for k in sorted(params.keys()):
        v = params[k]
        canonical_query_parts.append(f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}")
    canonical_query_string = "&".join(canonical_query_parts)
    
    canonical_uri = "/"
    
    t = datetime.datetime.now(datetime.UTC)
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    hashed_payload = hashlib.sha256(b"").hexdigest()
    
    canonical_headers = f"host:{host}\nx-amz-content-sha256:{hashed_payload}\nx-amz-date:{amz_date}\n"
    signed_headers = "host;x-amz-content-sha256;x-amz-date"
    
    canonical_request = f"GET\n{canonical_uri}\n{canonical_query_string}\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    algorithm = "AWS4-HMAC-SHA256"
    region = "auto"
    service = "s3"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"
    
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = hmac.new(("AWS4" + key).encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = sign(k_date, region_name)
        k_service = sign(k_region, service_name)
        k_signing = sign(k_service, "aws4_request")
        return k_signing
        
    signing_key = get_signature_key(r2_secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    authorization_header = f"{algorithm} Credential={r2_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    url = f"https://{host}{canonical_uri}?{canonical_query_string}"
    headers = {
        'Host': host,
        'Authorization': authorization_header,
        'x-amz-date': amz_date,
        'x-amz-content-sha256': hashed_payload
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            return []
            
        root = ET.fromstring(r.content)
        keys = []
        for elem in root.iter():
            if elem.tag.endswith('Key'):
                keys.append(elem.text)
        return keys
    except Exception:
        return []

def rebuild_admin_public_images_json(curated_config, manual_images):
    """Từ curated_config (chứa vai trò tiếng Việt) và manual_images, dựng lại Images_Admin_JSON và images_public_json"""
    import json
    if not curated_config or not isinstance(curated_config, dict):
        return "[]", "[]"
        
    images_list = curated_config.get("images", [])
    role_map_vi_to_en = {
        "Sơ đồ": "diagram", "Mặt tiền": "facade", "Bìa": "cover",
        "Hẻm": "alley", "Nội thất": "interior", "Ẩn": "hidden",
        "deleted": "deleted", "diagram": "diagram", "facade": "facade",
        "cover": "cover", "alley": "alley", "interior": "interior",
        "hidden": "hidden", "sodo": "diagram"
    }
    
    migrated_images = []
    for idx, img in enumerate(images_list):
        if not isinstance(img, dict):
            continue
        url = img.get("url")
        vi_role = img.get("role", "Nội thất")
        resolved_role = role_map_vi_to_en.get(vi_role, "interior")
        visible = img.get("visible", True)
        
        # Phân biệt origin: giữ nguyên nếu đã là self/user, hoặc có SYS-, hoặc nằm trong manual_images
        filename = url.split("/")[-1]
        origin = img.get("origin", "crawl")
        if origin in ["self", "user"] or filename.startswith("SYS-") or url in manual_images:
            origin = "self"
        else:
            origin = "crawl"
            
        is_hidden_val = 1 if (not visible or resolved_role in ["hidden", "deleted"]) else 0
        migrated_images.append({
            "image_url": url,
            "r2_url": url,
            "role": resolved_role,
            "sequence_index": idx,
            "origin": origin,
            "is_hidden": is_hidden_val
        })
        
    images_admin_json_str = json.dumps(migrated_images, ensure_ascii=False)
    
    cover_urls = []
    other_urls = []
    for img in migrated_images:
        if img["is_hidden"] == 0 and img["role"] not in ["facade", "diagram", "deleted", "hidden"]:
            url = img["r2_url"] if img["r2_url"] else img["image_url"]
            if img["role"] == "cover":
                cover_urls.append(url)
            else:
                other_urls.append(url)
    public_urls = cover_urls + other_urls
    images_public_json_str = json.dumps(public_urls, ensure_ascii=False)
    
    return images_admin_json_str, images_public_json_str

def upload_image_to_r2(file_content, filename, content_type="image/jpeg", r2_subfolder=None):
    """Tải ảnh lên Cloudflare R2 sử dụng REST API với AWS Signature v4"""
    import hashlib
    import hmac
    import datetime
    
    cfg = load_config()
    r2_access_key = cfg.get("r2_access_key_id")
    r2_secret_key = cfg.get("r2_secret_access_key")
    r2_bucket = cfg.get("r2_bucket_name")
    account_id = cfg.get("cloudflare_account_id")
    r2_public_url = cfg.get("r2_public_url")
    r2_migration_prefix = cfg.get("r2_migration_prefix", "").strip()
    if not r2_migration_prefix:
        raise Exception("Thiếu cấu hình r2_migration_prefix trong settings.json")
    
    if not (r2_access_key and r2_secret_key and r2_bucket and account_id):
        raise Exception("Thiếu cấu hình Cloudflare R2 trong settings.json")
        
    host = f"{r2_bucket}.{account_id}.r2.cloudflarestorage.com"
    endpoint = f"https://{host}"
    
    import urllib.parse
    if r2_subfolder:
        key = f"{r2_migration_prefix}/{r2_subfolder}/{filename}"
    else:
        key = f"{r2_migration_prefix}/{filename}"
    encoded_key = urllib.parse.quote(key, safe="/")
    path = f"/{encoded_key}"
    
    # Date helper
    t = datetime.datetime.now(datetime.UTC)
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    hashed_payload = hashlib.sha256(file_content).hexdigest()
    
    canonical_headers = f"host:{host}\nx-amz-content-sha256:{hashed_payload}\nx-amz-date:{amz_date}\n"
    signed_headers = "host;x-amz-content-sha256;x-amz-date"
    
    canonical_request = f"PUT\n{path}\n\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    algorithm = "AWS4-HMAC-SHA256"
    region = "auto"
    service = "s3"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"
    
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = hmac.new(("AWS4" + key).encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = sign(k_date, region_name)
        k_service = sign(k_region, service_name)
        k_signing = sign(k_service, "aws4_request")
        return k_signing
        
    signing_key = get_signature_key(r2_secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    authorization_header = f"{algorithm} Credential={r2_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    url = f"{endpoint}{path}"
    headers = {
        'Host': host,
        'Authorization': authorization_header,
        'x-amz-date': amz_date,
        'x-amz-content-sha256': hashed_payload,
        'Content-Type': content_type
    }
    
    r = requests.put(url, data=file_content, headers=headers, timeout=30)
    if r.status_code != 200:
        raise Exception(f"R2 API error {r.status_code}: {r.text}")
        
    return f"{r2_public_url}/{key}"

def copy_r2_object(src_key, dest_key):
    """Sao chép đối tượng nội bộ R2 bằng REST API CopyObject và Signature V4"""
    import urllib.parse
    import datetime
    import hashlib
    import hmac
    
    cfg = load_config()
    r2_access_key = cfg.get("r2_access_key_id")
    r2_secret_key = cfg.get("r2_secret_access_key")
    r2_bucket = cfg.get("r2_bucket_name")
    account_id = cfg.get("cloudflare_account_id")
    
    if not (r2_access_key and r2_secret_key and r2_bucket and account_id):
        return False
        
    host = f"{r2_bucket}.{account_id}.r2.cloudflarestorage.com"
    endpoint = f"https://{host}"
    
    src_source_val = f"/{r2_bucket}/{urllib.parse.quote(src_key)}"
    
    encoded_dest_key = urllib.parse.quote(dest_key, safe="/")
    path = f"/{encoded_dest_key}"
    
    t = datetime.datetime.now(datetime.UTC)
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    hashed_payload = hashlib.sha256(b"").hexdigest()
    
    canonical_headers = (
        f"host:{host}\n"
        f"x-amz-content-sha256:{hashed_payload}\n"
        f"x-amz-copy-source:{src_source_val}\n"
        f"x-amz-date:{amz_date}\n"
    )
    signed_headers = "host;x-amz-content-sha256;x-amz-copy-source;x-amz-date"
    
    canonical_request = f"PUT\n{path}\n\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    algorithm = "AWS4-HMAC-SHA256"
    region = "auto"
    service = "s3"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"
    
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = hmac.new(("AWS4" + key).encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = sign(k_date, region_name)
        k_service = sign(k_region, service_name)
        k_signing = sign(k_service, "aws4_request")
        return k_signing
        
    signing_key = get_signature_key(r2_secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    authorization_header = f"{algorithm} Credential={r2_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    url = f"{endpoint}{path}"
    headers = {
        'Host': host,
        'Authorization': authorization_header,
        'x-amz-date': amz_date,
        'x-amz-content-sha256': hashed_payload,
        'x-amz-copy-source': src_source_val
    }
    
    try:
        r = requests.put(url, headers=headers, timeout=20)
        return r.status_code == 200
    except Exception:
        return False

def delete_r2_object(key):
    """Xóa đối tượng trên R2 bằng REST API DELETE và Signature V4"""
    import urllib.parse
    import datetime
    import hashlib
    import hmac
    
    cfg = load_config()
    r2_access_key = cfg.get("r2_access_key_id")
    r2_secret_key = cfg.get("r2_secret_access_key")
    r2_bucket = cfg.get("r2_bucket_name")
    account_id = cfg.get("cloudflare_account_id")
    
    if not (r2_access_key and r2_secret_key and r2_bucket and account_id):
        return False
        
    host = f"{r2_bucket}.{account_id}.r2.cloudflarestorage.com"
    endpoint = f"https://{host}"
    
    encoded_key = urllib.parse.quote(key, safe="/")
    path = f"/{encoded_key}"
    
    t = datetime.datetime.now(datetime.UTC)
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    hashed_payload = hashlib.sha256(b"").hexdigest()
    
    canonical_headers = f"host:{host}\nx-amz-content-sha256:{hashed_payload}\nx-amz-date:{amz_date}\n"
    signed_headers = "host;x-amz-content-sha256;x-amz-date"
    
    canonical_request = f"DELETE\n{path}\n\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    algorithm = "AWS4-HMAC-SHA256"
    region = "auto"
    service = "s3"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"
    
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = hmac.new(("AWS4" + key).encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = sign(k_date, region_name)
        k_service = sign(k_region, service_name)
        k_signing = sign(k_service, "aws4_request")
        return k_signing
        
    signing_key = get_signature_key(r2_secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    authorization_header = f"{algorithm} Credential={r2_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    url = f"{endpoint}{path}"
    headers = {
        'Host': host,
        'Authorization': authorization_header,
        'x-amz-date': amz_date,
        'x-amz-content-sha256': hashed_payload
    }
    
    try:
        r = requests.delete(url, headers=headers, timeout=20)
        return r.status_code in [200, 204]
    except Exception:
        return False

def create_drive_folder(folder_name, parent_id, token):
    """Tạo thư mục con trên Drive phục vụ gom ảnh theo mã căn"""
    headers = {"Authorization": f"Bearer {token}"}
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id] if parent_id else []
    }
    
    r = requests.post(
        "https://www.googleapis.com/drive/v3/files",
        headers=headers,
        json=metadata,
        timeout=20
    )
    if r.status_code != 200:
        raise Exception(f"Không thể tạo thư mục Drive: {r.text}")
        
    return r.json().get("id")

# ==================================================
# TIẾN TRÌNH TỰ ĐỘNG DI CƯ HÌNH ẢNH CHẠY NGẦM (BACKGROUND AUTO-MIGRATION)
# ==================================================
IS_MIGRATION_ACTIVE = False
SHOULD_STOP_MIGRATION = False
MIGRATION_LOCK = threading.Lock()

def run_auto_migration_wrapper(cookie):
    global IS_MIGRATION_ACTIVE, SHOULD_STOP_MIGRATION
    try:
        SHOULD_STOP_MIGRATION = False
        run_image_migration_thread(limit=None, cookie=cookie)
    except Exception as e:
        add_log_message(f"[❌ AUTO-MIGRATION ERROR] Lỗi trong tiến trình di cư tự động: {str(e)}")
    finally:
        with MIGRATION_LOCK:
            IS_MIGRATION_ACTIVE = False
        backup_database()

def run_auto_migration_wrapper_with_limit(limit, cookie):
    global IS_MIGRATION_ACTIVE, SHOULD_STOP_MIGRATION
    try:
        SHOULD_STOP_MIGRATION = False
        run_image_migration_thread(limit=limit, cookie=cookie)
    except Exception as e:
        add_log_message(f"[❌ MIGRATION ERROR] Lỗi trong tiến trình di cư thủ công: {str(e)}")
    finally:
        with MIGRATION_LOCK:
            IS_MIGRATION_ACTIVE = False
        backup_database()

def start_auto_migration_scheduler():
    """Bắt đầu vòng lặp quét tự động di cư hình ảnh chạy ngầm"""
    def scheduler_loop():
        global IS_MIGRATION_ACTIVE
        # Nghỉ 10 giây trước khi bắt đầu quét lần đầu tiên để server khởi động hoàn tất
        time.sleep(10)
        
        while True:
            try:
                # 1. Kiểm tra xem có đang chạy di cư không
                with MIGRATION_LOCK:
                    if IS_MIGRATION_ACTIVE:
                        time.sleep(15)
                        continue
                
                # 2. Kiểm tra xem có database và có căn nào status = 'raw_text' không
                if os.path.exists(DB_FILE):
                    conn = None
                    try:
                        conn = sqlite3.connect(DB_FILE, timeout=30.0)
                        cursor = conn.cursor()
                        count = cursor.execute(f"SELECT COUNT(*) FROM {LISTINGS_TABLE} WHERE status = 'raw_text'").fetchone()[0]
                    finally:
                        if conn:
                            conn.close()
                    
                    if count > 0:
                        add_log_message(f"[⚡ AUTO-MIGRATION] Phát hiện {count} căn đang chờ di cư ảnh. Tự động kích hoạt luồng di cư...")
                        
                        cookie = ""
                        if os.path.exists(COOKIE_FILE):
                            try:
                                with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                                    cookie = f.read().strip()
                            except Exception:
                                pass
                        
                        with MIGRATION_LOCK:
                            IS_MIGRATION_ACTIVE = True
                            
                        # Khởi chạy luồng di cư
                        t = threading.Thread(target=run_auto_migration_wrapper, args=(cookie,))
                        t.daemon = True
                        t.start()
            except Exception as e:
                # Thử lại thầm lặng
                pass
            
            # Nghỉ 15 giây trước khi quét lần tiếp theo
            time.sleep(15)

    t = threading.Thread(target=scheduler_loop)
    t.daemon = True
    t.start()

def start_periodic_backup_scheduler():
    """Khởi động bộ lập lịch tự động sao lưu CSDL định kỳ chạy ngầm (quét mỗi 15 phút)"""
    def scheduler_loop():
        # Đợi 15 giây cho server khởi chạy hoàn tất trước khi quét lượt đầu
        time.sleep(15)
        while True:
            try:
                backup_database()
            except Exception:
                pass
            time.sleep(900)  # Lặp lại sau mỗi 15 phút
    t = threading.Thread(target=scheduler_loop)
    t.daemon = True
    t.start()

def run_image_migration_thread(limit, cookie, target_tk_id=None, skip_sheets_publish=False):
    """Tải và di cư hình ảnh chạy ngầm hoặc đồng bộ căn cụ thể (Throttled Mode)"""
    global SHOULD_STOP_MIGRATION
    SHOULD_STOP_MIGRATION = False
    
    if target_tk_id:
        add_log_message(f"[🚀] KHỞI ĐỘNG TIẾN TRÌNH DI CƯ HÌNH ẢNH CHO CĂN: {target_tk_id}...")
    else:
        add_log_message("[🚀] KHỞI ĐỘNG TIẾN TRÌNH DI CƯ HÌNH ẢNH CHẠY NGẦM...")
    
    # 1. Truy vấn các căn chưa được xử lý ảnh
    if not os.path.exists(DB_FILE):
        add_log_message("[❌] Chưa có file Database SQLite raw_archive.db. Vui lòng cào tin trước.")
        return
        
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if target_tk_id:
            rows = cursor.execute(f"SELECT * FROM {LISTINGS_TABLE} WHERE tk_id = ?", (target_tk_id,)).fetchall()
        else:
            rows = cursor.execute(f"SELECT * FROM {LISTINGS_TABLE} WHERE status = 'raw_text'").fetchall()
    finally:
        if conn:
            conn.close()
    
    if not rows:
        if target_tk_id:
            add_log_message(f"[⚠️] Không tìm thấy thông tin căn {target_tk_id} để di cư ảnh.")
        else:
            add_log_message("[✅] Tuyệt vời! Không có căn nào ở trạng thái chờ di cư ảnh (status='raw_text').")
        return
        
    if target_tk_id:
        add_log_message(f"[i] Bắt đầu di cư hình ảnh cho căn mục tiêu: {target_tk_id}")
    else:
        add_log_message(f"[i] Phát hiện {len(rows)} căn thô cần di cư hình ảnh.")
    
    # 2. Kiểm tra cấu hình Cloud (Cloudflare R2 hoặc Google Drive)
    cfg = load_config()
    
    r2_access_key = cfg.get("r2_access_key_id")
    r2_secret_key = cfg.get("r2_secret_access_key")
    r2_bucket = cfg.get("r2_bucket_name")
    account_id = cfg.get("cloudflare_account_id")
    r2_public_url = cfg.get("r2_public_url", "")
    use_r2 = bool(r2_access_key and r2_secret_key and r2_bucket and account_id)
    
    creds = None
    token = None
    drive_parent_folder = None
    
    if use_r2:
        add_log_message(f"[🔒] Phát hiện cấu hình Cloudflare R2 (Bucket: {r2_bucket}). Ảnh sẽ được upload trực tiếp lên Cloudflare R2 siêu tốc!")
    else:
        creds = get_google_credentials()
        token = get_google_access_token(creds)
        drive_parent_folder = cfg.get("drive_folder_id")
        if creds and token:
            add_log_message("[🔒] Google Service Account được phát hiện. Ảnh sẽ được upload lên Google Drive 5TB!")
        else:
            add_log_message("[⚠️] KHÔNG phát hiện file 'credentials.json' hoặc cấu hình Cloudflare R2. Hệ thống tự động kích hoạt chế độ tải ảnh CỤC BỘ (Local Storage) để lưu trữ tại static/images/[tk_id]/")
        
    headers_tk = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie or ""
    }
    
    processed = 0
    for row in rows:
        if SHOULD_STOP_MIGRATION:
            add_log_message("[🛑] ĐÃ YÊU CẦU DỪNG TIẾN TRÌNH DI CƯ HÌNH ẢNH!")
            break
            
        if limit and processed >= limit:
            break
            
        row_db_id = row["tk_id"] if LISTINGS_TABLE == "listings_v2" else row["id"]
        tk_id = row["tk_id"]
        d = normalize_listing_for_client(row)
        raw_images_tk = d["raw_images_tk"]
        
        add_log_message(f"[+] Bắt đầu xử lý hình ảnh cho căn: {tk_id} ({len(raw_images_tk)} ảnh gốc)...")
        
        drive_links = []
        house_folder_id = None
        
        # Nếu dùng Drive, tạo thư mục riêng cho căn nhà
        if not use_r2 and token:
            try:
                house_folder_id = create_drive_folder(f"TK_{tk_id}", drive_parent_folder, token)
            except Exception as e:
                add_log_message(f"  [⚠️] Không tạo được folder Drive riêng cho {tk_id}: {str(e)}. Sẽ dùng folder cha.")
                house_folder_id = drive_parent_folder
                
        # ==================================================
        # TIẾN TRÌNH DI CƯ ẢNH SONG SONG ĐA LUỒNG (PARALLEL WORKER POOL - SPEEDUP 700% - 1000%)
        # ==================================================
        import concurrent.futures
        
        drive_links = ["" for _ in raw_images_tk]
        new_images_mapping = {}
        
        # 1. Đọc dữ liệu ảnh cũ và cấu hình thủ công để đối chiếu/trộn
        images_mapping_json_val = row["images_mapping_json"] if "images_mapping_json" in row.keys() else None
        manual_images_json_val = row["manual_images_json"] if "manual_images_json" in row.keys() else None
        raw_sodo_tk_json_val = row["raw_sodo_tk_json"] if "raw_sodo_tk_json" in row.keys() else None
        curated_config_json_val = row["curated_config_json"] if "curated_config_json" in row.keys() else None
        
        try:
            images_mapping = json.loads(images_mapping_json_val) if images_mapping_json_val else {}
        except Exception:
            images_mapping = {}
            
        try:
            manual_images = json.loads(manual_images_json_val) if manual_images_json_val else []
        except Exception:
            manual_images = []
            
        try:
            raw_sodo_tk = json.loads(raw_sodo_tk_json_val) if raw_sodo_tk_json_val else []
        except Exception:
            raw_sodo_tk = []

        # R2 Subfolder và Precheck Logic (US-141)
        r2_subfolder = None
        if use_r2:
            r2_migration_prefix = cfg.get("r2_migration_prefix", "").strip()
            if not r2_migration_prefix:
                add_log_message("[❌ ERROR] Thiếu cấu hình r2_migration_prefix trong settings.json. Tiến trình di cư ảnh bị hủy.")
                return
            r2_subfolder = get_r2_subfolder(tk_id, dict(row))
            prefix = f"{r2_migration_prefix}/{r2_subfolder}/"
            
            # Liệt kê danh sách file đã tồn tại trên R2 trong thư mục con này
            r2_keys = list_r2_objects(prefix)
            
            # [US-152] Chỉ bảo toàn ảnh tự up tay (SYS-), tắt auto-move ảnh thô cũ để tải mới 100%
            if not r2_keys:
                # Quét tìm các ảnh tự up tay (SYS-) từ các prefix lịch sử
                historical_prefixes = ["BDS-KhangNgo", "BDS-KhangNgo-v2"]
                if r2_migration_prefix in historical_prefixes:
                    historical_prefixes.remove(r2_migration_prefix)
                
                sys_prefixes = []
                for pref in historical_prefixes:
                    sys_prefixes.extend([
                        f"{pref}/{r2_subfolder}",
                        f"{pref}/SYS-{tk_id.upper()}",
                        f"{pref}/SYS-{tk_id.lower()}",
                        f"{pref}/SYS-{tk_id.replace('-', '').upper()}",
                        f"{pref}/SYS-{tk_id.replace('-', '').lower()}"
                    ])
                sys_keys = []
                for op in sys_prefixes:
                    res_keys = list_r2_objects(op)
                    if res_keys:
                        for k in res_keys:
                            filename = k.split("/")[-1].upper()
                            # Chỉ lấy ảnh Admin up tay (tiền tố SYS-)
                            if filename.startswith(f"SYS-{tk_id.upper()}_") or filename.startswith(f"SYS-{tk_id.replace('-', '').upper()}_"):
                                sys_keys.append(k)
                sys_keys = list(set(sys_keys))
                
                if sys_keys:
                    add_log_message(f"  [🔄 Bảo toàn] Phát hiện {len(sys_keys)} ảnh tự up tay (SYS-). Đang copy sang thư mục mới v3 '{r2_subfolder}'...")
                    for sys_key in sys_keys:
                        filename = sys_key.split("/")[-1]
                        new_key = f"{r2_migration_prefix}/{r2_subfolder}/{filename}"
                        if copy_r2_object(sys_key, new_key):
                            # Không gọi delete_r2_object để bảo toàn file v1/v2 của Production cũ
                            r2_keys.append(new_key)
            
            if r2_keys:
                add_log_message(f"  [⚡ Precheck] Phát hiện {len(r2_keys)} ảnh đã tồn tại trên R2 cho căn '{r2_subfolder}'. Đang khôi phục mapping...")
                
                col_sodo1_key = get_safe_col_name("Sơ đồ thửa đất 1")
                col_sodo2_key = get_safe_col_name("Sơ đồ thửa đất 2")
                col_sodo3_key = get_safe_col_name("Sơ đồ thửa đất 3")
                col_sodo4_key = get_safe_col_name("Sơ đồ thửa đất 4")
                col_sodo5_key = get_safe_col_name("Sơ đồ thửa đất 5")
                original_sodo1 = d.get(col_sodo1_key)
                original_sodo2 = d.get(col_sodo2_key)
                original_sodo3 = d.get(col_sodo3_key)
                original_sodo4 = d.get(col_sodo4_key)
                original_sodo5 = d.get(col_sodo5_key)
                
                for key in r2_keys:
                    filename = key.split("/")[-1]
                    r2_url = f"{r2_public_url}/{key}"
                    
                    # 1. Ảnh thường: img_{tk_id}_{idx}.jpg
                    if filename.startswith(f"img_{tk_id}_") and filename.endswith(".jpg"):
                        try:
                            idx_str = filename[len(f"img_{tk_id}_"):-4]
                            idx = int(idx_str)
                            if 1 <= idx <= len(raw_images_tk):
                                img_url = raw_images_tk[idx - 1]
                                images_mapping[img_url] = r2_url
                                new_images_mapping[img_url] = r2_url
                        except Exception:
                            pass
                    
                    # 2. Sơ đồ: sodo{sodo_num}_{tk_id}.jpg
                    elif filename.startswith("sodo") and filename.endswith(f"_{tk_id}.jpg"):
                        try:
                            sodo_num = filename[4:filename.find(f"_{tk_id}")]
                            if sodo_num == "1" and original_sodo1:
                                images_mapping[original_sodo1] = r2_url
                                new_images_mapping[original_sodo1] = r2_url
                            elif sodo_num == "2" and original_sodo2:
                                images_mapping[original_sodo2] = r2_url
                                new_images_mapping[original_sodo2] = r2_url
                            elif sodo_num == "3" and original_sodo3:
                                images_mapping[original_sodo3] = r2_url
                                new_images_mapping[original_sodo3] = r2_url
                            elif sodo_num == "4" and original_sodo4:
                                images_mapping[original_sodo4] = r2_url
                                new_images_mapping[original_sodo4] = r2_url
                            elif sodo_num == "5" and original_sodo5:
                                images_mapping[original_sodo5] = r2_url
                                new_images_mapping[original_sodo5] = r2_url
                        except Exception:
                            pass
                            
                    # 3. Ảnh upload thủ công: SYS-{tk_id.upper()}_{role}_{timestamp}{ext}
                    elif (filename.upper().startswith(f"SYS-{tk_id.upper()}_") or 
                          filename.upper().startswith(f"SYS-{tk_id.replace('-', '').upper()}_")):
                        if r2_url not in manual_images:
                            manual_images.append(r2_url)

        # Tái sử dụng ảnh R2 cũ từ file backup (US-116)
        r2_by_tk_id_file = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/r2_images_by_tk_id.json"
        r2_by_tk_id = {}
        if os.path.exists(r2_by_tk_id_file):
            try:
                with open(r2_by_tk_id_file, "r", encoding="utf-8") as r2_f:
                    r2_by_tk_id = json.load(r2_f)
            except Exception:
                pass
        
        tk_r2_data = r2_by_tk_id.get(tk_id)
        if tk_r2_data:
            # Xác định các ảnh sơ đồ thửa đất để đối chiếu
            col_sodo1_key = get_safe_col_name("Sơ đồ thửa đất 1")
            col_sodo2_key = get_safe_col_name("Sơ đồ thửa đất 2")
            col_sodo3_key = get_safe_col_name("Sơ đồ thửa đất 3")
            col_sodo4_key = get_safe_col_name("Sơ đồ thửa đất 4")
            col_sodo5_key = get_safe_col_name("Sơ đồ thửa đất 5")
            original_sodo1 = d.get(col_sodo1_key)
            original_sodo2 = d.get(col_sodo2_key)
            original_sodo3 = d.get(col_sodo3_key)
            original_sodo4 = d.get(col_sodo4_key)
            original_sodo5 = d.get(col_sodo5_key)
            stripped_sodo = {url.split('?')[0] for url in raw_sodo_tk if url}

            for idx, img_url in enumerate(raw_images_tk):
                stripped_url = img_url.split('?')[0] if img_url else ""
                if stripped_url in images_mapping:
                    continue
                orig_filename = stripped_url.split('/')[-1]
                base_name = orig_filename.split('.')[0]
                r2_url = None
                
                # 1. Khớp theo tên file gốc trong filenames
                if orig_filename in tk_r2_data.get("filenames", {}):
                    r2_url = tk_r2_data["filenames"][orig_filename]
                elif base_name in tk_r2_data.get("filenames", {}):
                    r2_url = tk_r2_data["filenames"][base_name]
                else:
                    is_diag = (stripped_url in stripped_sodo) or \
                              (original_sodo1 and stripped_url == original_sodo1.split('?')[0]) or \
                              (original_sodo2 and stripped_url == original_sodo2.split('?')[0]) or \
                              (original_sodo3 and stripped_url == original_sodo3.split('?')[0]) or \
                              (original_sodo4 and stripped_url == original_sodo4.split('?')[0]) or \
                              (original_sodo5 and stripped_url == original_sodo5.split('?')[0])
                    
                    if is_diag:
                        # Thử lấy số từ tên file sơ đồ (vd sodo2 -> 2)
                        digits = "".join(filter(str.isdigit, base_name))
                        if digits and digits in tk_r2_data.get("sodo", {}):
                            r2_url = tk_r2_data["sodo"][digits]
                        else:
                            sodo_num = None
                            if original_sodo1 and stripped_url == original_sodo1.split('?')[0]: sodo_num = "1"
                            elif original_sodo2 and stripped_url == original_sodo2.split('?')[0]: sodo_num = "2"
                            elif original_sodo3 and stripped_url == original_sodo3.split('?')[0]: sodo_num = "3"
                            elif original_sodo4 and stripped_url == original_sodo4.split('?')[0]: sodo_num = "4"
                            elif original_sodo5 and stripped_url == original_sodo5.split('?')[0]: sodo_num = "5"
                            else:
                                try:
                                    sodo_idx = raw_sodo_tk.index(img_url)
                                    sodo_num = str(sodo_idx + 1)
                                except ValueError:
                                    pass
                            if sodo_num and sodo_num in tk_r2_data.get("sodo", {}):
                                r2_url = tk_r2_data["sodo"][sodo_num]
                    else:
                        # Nếu tên file là số đại diện cho stt gốc (vd: 22.jpg -> 22)
                        if base_name.isdigit() and base_name in tk_r2_data.get("images", {}):
                            r2_url = tk_r2_data["images"][base_name]
                        # Khớp theo stt của danh sách cào mới
                        elif str(idx + 1) in tk_r2_data.get("images", {}):
                            r2_url = tk_r2_data["images"][str(idx + 1)]
                        
                if r2_url:
                    images_mapping[img_url] = r2_url

        # Xác định URL ảnh sơ đồ thửa đất của căn này để bỏ qua nén
        col_sodo1_key = get_safe_col_name("Sơ đồ thửa đất 1")
        col_sodo2_key = get_safe_col_name("Sơ đồ thửa đất 2")
        col_sodo3_key = get_safe_col_name("Sơ đồ thửa đất 3")
        col_sodo4_key = get_safe_col_name("Sơ đồ thửa đất 4")
        col_sodo5_key = get_safe_col_name("Sơ đồ thửa đất 5")
        original_sodo1 = d.get(col_sodo1_key)
        original_sodo2 = d.get(col_sodo2_key)
        original_sodo3 = d.get(col_sodo3_key)
        original_sodo4 = d.get(col_sodo4_key)
        original_sodo5 = d.get(col_sodo5_key)

        images_to_process = []
        # Build lookup dictionaries with query-strings removed to support dynamic Cloudfront signed URLs
        stripped_mapping = {}
        for k, v in images_mapping.items():
            if k:
                stripped_mapping[k.split('?')[0]] = v
                
        stripped_sodo = {url.split('?')[0] for url in raw_sodo_tk if url}

        images_to_process = []
        for idx, img_url in enumerate(raw_images_tk):
            stripped_url = img_url.split('?')[0] if img_url else ""
            # Nếu ảnh đã được di cư thành công trong mapping, bỏ qua tải/nén/up
            if stripped_url in stripped_mapping and stripped_mapping[stripped_url]:
                drive_links[idx] = stripped_mapping[stripped_url]
                new_images_mapping[img_url] = stripped_mapping[stripped_url]
                add_log_message(f"  [⚡ Skip] Ảnh #{idx+1} của {tk_id} đã di cư trước đó. Sử dụng lại: {stripped_mapping[stripped_url]}")
            else:
                is_diag = (stripped_url in stripped_sodo) or \
                          (original_sodo1 and stripped_url == original_sodo1.split('?')[0]) or \
                          (original_sodo2 and stripped_url == original_sodo2.split('?')[0]) or \
                          (original_sodo3 and stripped_url == original_sodo3.split('?')[0]) or \
                          (original_sodo4 and stripped_url == original_sodo4.split('?')[0]) or \
                          (original_sodo5 and stripped_url == original_sodo5.split('?')[0])
                images_to_process.append((idx, img_url, is_diag))
        
        def process_single_image(args_tuple):
            idx, img_url, is_diagram = args_tuple
            try:
                img_data = download_image_with_retry(img_url, headers_tk)
                if not img_data:
                    add_log_message(f"  [❌] Bỏ qua ảnh #{idx+1} của {tk_id} do lỗi tải file.")
                    return idx, "", img_url
                    
                # BỎ QUA NÉN CHO ẢNH SƠ ĐỒ ĐỂ BẢO TOÀN CHI TIẾT
                if is_diagram:
                    orig_kb = int(len(img_data) / 1024)
                    add_log_message(f"  [🛡️ Sơ đồ] Ảnh #{idx+1} của {tk_id} là ảnh Sơ đồ thửa đất ({orig_kb}KB). BỎ QUA NÉN để bảo toàn chi tiết.")
                else:
                    img_data_original_len = len(img_data)
                    img_data = compress_image(img_data)
                    img_data_compressed_len = len(img_data)
                    
                    saved_percent = 0
                    if img_data_original_len > 0:
                        saved_percent = int((img_data_original_len - img_data_compressed_len) / img_data_original_len * 100)
                    
                    orig_kb = int(img_data_original_len / 1024)
                    comp_kb = int(img_data_compressed_len / 1024)
                    add_log_message(f"  [⚡ Tối ưu] Ảnh #{idx+1} của {tk_id}: {orig_kb}KB -> {comp_kb}KB (Giảm {saved_percent}%)")
                
                filename = f"img_{tk_id}_{idx+1}.jpg"
                
                if use_r2:
                    img_link = upload_image_to_r2(img_data, filename, r2_subfolder=r2_subfolder)
                    return idx, img_link, img_url
                elif token:
                    drive_link = upload_image_to_drive(img_data, filename, house_folder_id, token)
                    return idx, drive_link, img_url
                else:
                    local_dir = os.path.join("static", "images", tk_id)
                    os.makedirs(local_dir, exist_ok=True)
                    local_path = os.path.join(local_dir, filename)
                    with open(local_path, "wb") as f:
                        f.write(img_data)
                    local_url = f"/static/images/{tk_id}/{filename}"
                    return idx, local_url, img_url
            except Exception as e:
                add_log_message(f"  [❌ LỖI] Xử lý ảnh #{idx+1} thất bại cho {tk_id}: {str(e)}")
                return idx, "", img_url

        if images_to_process:
            max_workers = min(3, len(images_to_process))
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = executor.map(process_single_image, images_to_process)
                for idx, img_link, img_url in results:
                    if img_link:
                        drive_links[idx] = img_link
                        new_images_mapping[img_url] = img_link

        # Cập nhật SQLite, phân loại sơ đồ/ảnh thô và tự động đẩy Sheets Pool (US-040)
        conn = None
        try:
            clean_sodo1 = ""
            clean_sodo2 = ""
            clean_sodo3 = ""
            clean_sodo4 = ""
            clean_sodo5 = ""
            house_links = []
            
            for idx, img_url in enumerate(raw_images_tk):
                if idx >= len(drive_links):
                    continue
                migrated_url = drive_links[idx]
                if not migrated_url:
                    continue
                
                stripped_img_url = img_url.split('?')[0] if img_url else ""
                if original_sodo1 and stripped_img_url == original_sodo1.split('?')[0]:
                    clean_sodo1 = migrated_url
                elif original_sodo2 and stripped_img_url == original_sodo2.split('?')[0]:
                    clean_sodo2 = migrated_url
                elif original_sodo3 and stripped_img_url == original_sodo3.split('?')[0]:
                    clean_sodo3 = migrated_url
                elif original_sodo4 and stripped_img_url == original_sodo4.split('?')[0]:
                    clean_sodo4 = migrated_url
                elif original_sodo5 and stripped_img_url == original_sodo5.split('?')[0]:
                    clean_sodo5 = migrated_url
                else:
                    house_links.append(migrated_url)
            
            # Tự động di cư Sơ đồ thửa đất 1 đến 5 lên Cloud (bỏ qua nén)
            headers_tk_sodo = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Cookie": cookie or ""
            }
            
            for sodo_num, (orig_sodo, clean_sodo) in enumerate([
                (original_sodo1, clean_sodo1),
                (original_sodo2, clean_sodo2),
                (original_sodo3, clean_sodo3),
                (original_sodo4, clean_sodo4),
                (original_sodo5, clean_sodo5)
            ], start=1):
                if orig_sodo and orig_sodo.startswith("http") and not ("google" in clean_sodo or "r2.dev" in clean_sodo or (r2_public_url and r2_public_url in clean_sodo)):
                    try:
                        add_log_message(f"  [🛡️ Sơ đồ {sodo_num}] Đang di cư Ảnh Sơ đồ thửa đất {sodo_num} của {tk_id} lên Cloud (BỎ QUA NÉN)...")
                        img_data = download_image_with_retry(orig_sodo, headers_tk_sodo)
                        if img_data:
                            filename = f"sodo{sodo_num}_{tk_id}.jpg"
                            migrated = ""
                            if use_r2:
                                migrated = upload_image_to_r2(img_data, filename, r2_subfolder=r2_subfolder)
                            elif token:
                                migrated = upload_image_to_drive(img_data, filename, house_folder_id, token)
                            
                            if migrated:
                                if sodo_num == 1: clean_sodo1 = migrated
                                elif sodo_num == 2: clean_sodo2 = migrated
                                elif sodo_num == 3: clean_sodo3 = migrated
                                elif sodo_num == 4: clean_sodo4 = migrated
                                elif sodo_num == 5: clean_sodo5 = migrated
                                add_log_message(f"  [🛡️ Sơ đồ {sodo_num}] Di cư Sơ đồ {sodo_num} thành công: {migrated}")
                                new_images_mapping[orig_sodo] = migrated
                    except Exception as e:
                        add_log_message(f"  [❌ LỖI] Di cư Sơ đồ {sodo_num} thất bại: {str(e)}")

            first_property_r2 = ""
            first_property_r2 = ""
            # [US-152]: Vô hiệu hóa Smart Image Merge chắp vá cũ. Dựng mảng ảnh mới sạch 100% từ cào.
            if LISTINGS_TABLE == "listings":
                try:
                    curated_data = json.loads(curated_config_json_val) if curated_config_json_val else None
                except Exception:
                    curated_data = None
                    
                old_images = []
                if isinstance(curated_data, dict):
                    old_images = curated_data.get("images", [])
                elif isinstance(curated_data, list):
                    old_images = curated_data
                
                new_images_list = []
                added_urls = set()
                new_r2_urls = set(new_images_mapping.values())
                stripped_sodo = {url.split('?')[0] for url in raw_sodo_tk if url}
                
                # Tìm ảnh property_image đầu tiên (Mặt tiền) mới cào
                for img_url in raw_images_tk:
                    if img_url in new_images_mapping:
                        r2_url = new_images_mapping[img_url]
                        stripped_img = img_url.split('?')[0] if img_url else ""
                        is_diag = (stripped_img in stripped_sodo) or \
                                  (original_sodo1 and stripped_img == original_sodo1.split('?')[0]) or \
                                  (original_sodo2 and stripped_img == original_sodo2.split('?')[0]) or \
                                  (original_sodo3 and stripped_img == original_sodo3.split('?')[0]) or \
                                  (original_sodo4 and stripped_img == original_sodo4.split('?')[0]) or \
                                  (original_sodo5 and stripped_img == original_sodo5.split('?')[0])
                        if not is_diag:
                            first_property_r2 = r2_url
                            break

                # 1. DUYỆT QUA OLD IMAGES THEO THỨ TỰ VẬT LÝ GỐC ĐỂ BẢO TOÀN THỨ TỰ TƯƠNG ĐỐI
                for img in old_images:
                    if not isinstance(img, dict):
                        continue
                    url = img.get("url", "")
                    origin = img.get("origin", "")
                    
                    # A. Ảnh tự upload: Bảo toàn nguyên vẹn
                    if url.upper().startswith("SYS-") or "SYS-" in url.upper() or origin in ["local", "self", "user"]:
                        new_images_list.append(img)
                        added_urls.add(url)
                    # B. Ảnh cào cũ: Chỉ giữ lại nếu vẫn còn tồn tại trên nguồn Thiên Khôi (có trong new_r2_urls)
                    elif url in new_r2_urls:
                        img_copy = dict(img)
                        # Tìm URL gốc đối tác để kiểm tra xem có phải ảnh sơ đồ không
                        orig_url = None
                        for k, v in new_images_mapping.items():
                            if v == url:
                                orig_url = k
                                break
                        
                        is_diag = False
                        if orig_url:
                            stripped_img = orig_url.split('?')[0]
                            is_diag = (stripped_img in stripped_sodo) or \
                                      (original_sodo1 and stripped_img == original_sodo1.split('?')[0]) or \
                                      (original_sodo2 and stripped_img == original_sodo2.split('?')[0]) or \
                                      (original_sodo3 and stripped_img == original_sodo3.split('?')[0]) or \
                                      (original_sodo4 and stripped_img == original_sodo4.split('?')[0]) or \
                                      (original_sodo5 and stripped_img == original_sodo5.split('?')[0])
                        
                        # Khôi phục vai trò/ẩn hiện chuẩn xác nếu trước đây bị đánh dấu deleted
                        if img_copy.get("role") == "deleted":
                            if is_diag:
                                img_copy["role"] = "Sơ đồ"
                                img_copy["visible"] = False
                            elif url == first_property_r2:
                                img_copy["role"] = "Mặt tiền"
                                img_copy["visible"] = True
                            else:
                                img_copy["role"] = "Nội thất"
                                img_copy["visible"] = False
                        elif url == first_property_r2 and img_copy.get("role") not in ["Mặt tiền", "Bìa", "Sơ đồ"]:
                            img_copy["role"] = "Mặt tiền"
                            img_copy["visible"] = True
                            
                        img_copy["origin"] = "crawl"
                        new_images_list.append(img_copy)
                        added_urls.add(url)
                
                # 2. NẠP MỚI 100% ẢNH CÀO TỪ THIÊN KHÔI CHƯA TỒN TẠI TRONG OLD IMAGES (APPEND VÀO CUỐI)
                for img_url in raw_images_tk:
                    if img_url in new_images_mapping:
                        r2_url = new_images_mapping[img_url]
                        if r2_url not in added_urls:
                            stripped_img = img_url.split('?')[0] if img_url else ""
                            is_diag = (stripped_img in stripped_sodo) or \
                                      (original_sodo1 and stripped_img == original_sodo1.split('?')[0]) or \
                                      (original_sodo2 and stripped_img == original_sodo2.split('?')[0]) or \
                                      (original_sodo3 and stripped_img == original_sodo3.split('?')[0]) or \
                                      (original_sodo4 and stripped_img == original_sodo4.split('?')[0]) or \
                                      (original_sodo5 and stripped_img == original_sodo5.split('?')[0])
                            
                            if is_diag:
                                role = "Sơ đồ"
                                visible = False
                            elif r2_url == first_property_r2:
                                role = "Mặt tiền"
                                visible = True
                            else:
                                role = "Nội thất"
                                visible = False
                            
                            new_images_list.append({
                                "url": r2_url,
                                "role": role,
                                "visible": visible,
                                "origin": "crawl"
                            })
                            added_urls.add(r2_url)

                # 3. XÓA VẬT LÝ CÁC FILE RẢC CỦA TIN CÀO TRÊN CLOUDFLARE R2
                if use_r2 and r2_keys:
                    active_r2_urls = {img.get("url") for img in new_images_list if img.get("url")}
                    deleted_count = 0
                    for key in r2_keys:
                        r2_url = f"{r2_public_url}/{key}"
                        filename = key.split("/")[-1]
                        
                        # 🛡️ CƠ CHẾ PHÒNG VỆ TUYỆT ĐỐI (Chống xóa nhầm ảnh tự upload)
                        # Chỉ xóa ảnh nếu không nằm trong active_r2_urls và không có tiền tố SYS-
                        if r2_url not in active_r2_urls:
                            if not (filename.upper().startswith("SYS-") or "SYS-" in filename.upper()):
                                add_log_message(f"  [🗑️ Cloud R2] Phát hiện file rác cào bị loại bỏ: {key}. Đang xóa vĩnh viễn trên R2...")
                                if delete_r2_object(key):
                                    add_log_message(f"  [🗑️ Cloud R2 SUCCESS] Đã xóa thành công: {key}")
                                    deleted_count += 1
                                else:
                                    add_log_message(f"  [⚠️ Cloud R2 FAILED] Không thể xóa: {key}")
                    if deleted_count > 0:
                        add_log_message(f"[✅ Cloud R2 COMPLETE] Đã dọn dẹp xong {deleted_count} ảnh cào cũ bị xóa khỏi R2.")
                
                # [US-152] Refactor: Dùng System ID làm khóa định danh thay vì Mã Khang Ngô
                new_curated_config = {
                    "images": new_images_list,
                    "system_id": d.get("System_ID") or ""
                }
                
                # Đóng gói dữ liệu Images_Admin_JSON và images_public_json cho bảng listings
                role_map_vi_to_en = {
                    "Sơ đồ": "diagram",
                    "Mặt tiền": "facade",
                    "Bìa": "cover",
                    "Hẻm": "alley",
                    "Nội thất": "interior",
                    "Ẩn": "hidden",
                    "deleted": "deleted",
                    "diagram": "diagram",
                    "facade": "facade",
                    "cover": "cover",
                    "alley": "alley",
                    "interior": "interior",
                    "hidden": "hidden"
                }
                migrated_images = []
                for idx, img in enumerate(new_images_list):
                    url = img.get("url")
                    vi_role = img.get("role", "Nội thất")
                    resolved_role = role_map_vi_to_en.get(vi_role, "interior")
                    visible = img.get("visible", True)
                    origin = img.get("origin", "crawl")
                    if origin in ["self", "user"]:
                        origin = "self"
                    else:
                        origin = "crawl"
                    is_hidden_val = 1 if (not visible or resolved_role in ["hidden", "deleted"]) else 0
                    migrated_images.append({
                        "image_url": url,
                        "r2_url": url,
                        "role": resolved_role,
                        "sequence_index": idx,
                        "origin": origin,
                        "is_hidden": is_hidden_val
                    })
                images_admin_json_str = json.dumps(migrated_images, ensure_ascii=False)
                
                # Phân tách và sắp xếp mảng public: ảnh có role cover (Bìa) lên đầu, loại bỏ facade (Mặt tiền)
                cover_urls = []
                other_urls = []
                for img in migrated_images:
                    if img["is_hidden"] == 0 and img["role"] not in ["facade", "diagram", "deleted", "hidden"]:
                        url = img["r2_url"] if img["r2_url"] else img["image_url"]
                        if img["role"] == "cover":
                            cover_urls.append(url)
                        else:
                            other_urls.append(url)
                public_urls = cover_urls + other_urls
                images_public_json_str = json.dumps(public_urls, ensure_ascii=False)

                flat_sodo = []
                flat_hem = []
                flat_anh = []
                for img in migrated_images:
                    url = img.get("r2_url") or img.get("image_url") or ""
                    if not url:
                        continue
                    role = img.get("role")
                    if role in ["diagram", "Sơ đồ"]:
                        flat_sodo.append(url)
                    elif role in ["alley", "Hẻm"]:
                        flat_hem.append(url)
                    else:
                        flat_anh.append(url)

                clean_sodo1 = flat_sodo[0] if len(flat_sodo) > 0 else ""
                clean_sodo2 = flat_sodo[1] if len(flat_sodo) > 1 else ""
                clean_sodo3 = flat_sodo[2] if len(flat_sodo) > 2 else ""
                clean_sodo4 = flat_sodo[3] if len(flat_sodo) > 3 else ""
                clean_sodo5 = flat_sodo[4] if len(flat_sodo) > 4 else ""

                house_links = flat_anh
            
            # 2. Truy vấn dữ liệu cũ để tránh ghi đè làm mất thông tin đã biên tập
            col_ma_kn = get_safe_col_name("Mã Khang Ngô (ID)")
            col_tieu_de = get_safe_col_name("Tiêu đề Public")
            col_mo_ta = get_safe_col_name("Mô tả Public")
            col_phuong_cu = get_safe_col_name("Phường cũ (AI)")
            col_mat_tien = get_safe_col_name("Hình Mặt Tiền")
            col_anh_pub = get_safe_col_name("Ảnh Public (VD: 1,3,5)")
            col_anh_hem_pub = get_safe_col_name("Ảnh Hẻm Public (VD: 1,2)")
            
            ma_khang_ngo = row[col_ma_kn] if col_ma_kn in row.keys() else ""
            tieu_de_public = row[col_tieu_de] if col_tieu_de in row.keys() else ""
            mo_ta_public = row[col_mo_ta] if col_mo_ta in row.keys() else ""
            phuong_cu_ai = row[col_phuong_cu] if col_phuong_cu in row.keys() else ""
            hinh_mat_tien = row[col_mat_tien] if col_mat_tien in row.keys() else ""
            if not hinh_mat_tien and first_property_r2:
                hinh_mat_tien = first_property_r2
            anh_pub = row[col_anh_pub] if col_anh_pub in row.keys() else ""
            anh_hem_pub = row[col_anh_hem_pub] if col_anh_hem_pub in row.keys() else ""
            
            # 3. Ghi thông tin vào SQLite ở trạng thái 'raw_complete' trước
            conn = sqlite3.connect(DB_FILE, timeout=30.0)
            cursor = conn.cursor()
            
            cursor.execute(f"PRAGMA table_info({LISTINGS_TABLE})")
            db_cols = {r[1] for r in cursor.fetchall()}
            
            update_fields = {}
            # Public/curated fields
            update_fields[col_ma_kn] = ma_khang_ngo or ""
            update_fields[col_tieu_de] = tieu_de_public or ""
            update_fields[col_mo_ta] = mo_ta_public or ""
            update_fields[col_phuong_cu] = phuong_cu_ai or ""
            update_fields[col_mat_tien] = hinh_mat_tien or ""
            
            # Diagram images
            update_fields[col_sodo1_key] = clean_sodo1
            update_fields[col_sodo2_key] = clean_sodo2
            update_fields[col_sodo3_key] = clean_sodo3
            update_fields[col_sodo4_key] = clean_sodo4
            update_fields[col_sodo5_key] = clean_sodo5
            
            # Hẻm images
            for i in range(10):
                col_name = get_safe_col_name(f"Hình Hẻm {i+1}")
                if LISTINGS_TABLE == "listings":
                    val = flat_hem[i] if i < len(flat_hem) else ""
                else:
                    val = row[col_name] if col_name in row.keys() else None
                update_fields[col_name] = val or ""
            
            # Ảnh 1 to Ảnh 25 (Chứa tất cả 25 ảnh nội thất/ngoại thất thô)
            for i in range(25):
                col_name = get_safe_col_name(f"Ảnh {i+1}")
                val = house_links[i] if i < len(house_links) else ""
                update_fields[col_name] = val
                
            # Bảo toàn ảnh được chọn
            update_fields[col_anh_pub] = anh_pub or ""
            update_fields[col_anh_hem_pub] = anh_hem_pub or ""
                
            # Lọc các trường thực sự tồn tại trong DB để tránh lỗi no such column
            if LISTINGS_TABLE == "listings":
                update_fields["curated_config_json"] = json.dumps(new_curated_config, ensure_ascii=False)
                update_fields["images_mapping_json"] = json.dumps(new_images_mapping, ensure_ascii=False)
                update_fields["Images_Admin_JSON"] = images_admin_json_str
                update_fields["images_public_json"] = images_public_json_str
                
                image_fields_to_skip = {
                    get_safe_col_name("Hình Nhận Diện"),
                    get_safe_col_name("Ảnh Public (VD: 1,3,5)"),
                    get_safe_col_name("Ảnh Hẻm Public (VD: 1,2)")
                }
                old_hinh_mat_tien = row[col_mat_tien] if col_mat_tien in row.keys() else ""
                if old_hinh_mat_tien:
                    image_fields_to_skip.add(col_mat_tien)
                
                valid_update_fields = {k: v for k, v in update_fields.items() if k in db_cols and k not in image_fields_to_skip}
            else:
                valid_update_fields = {k: v for k, v in update_fields.items() if k in db_cols}
                
            cols_sql = [f"`{k}` = ?" for k in valid_update_fields.keys()]
            
            primary_key_col = "tk_id" if LISTINGS_TABLE == "listings_v2" else "id"
            drive_links_clean = [link for link in drive_links if link]
            if cols_sql:
                vals = list(valid_update_fields.values())
                vals.extend([json.dumps(drive_links_clean), row_db_id])
                cursor.execute(
                    f"UPDATE {LISTINGS_TABLE} SET {', '.join(cols_sql)}, raw_drive_images_json = ?, status = 'raw_complete' WHERE {primary_key_col} = ?",
                    vals
                )
            else:
                cursor.execute(
                    f"UPDATE {LISTINGS_TABLE} SET raw_drive_images_json = ?, status = 'raw_complete' WHERE {primary_key_col} = ?",
                    [json.dumps(drive_links_clean), row_db_id]
                )
            
            # If in Pool2 mode, update individual migrated images in listings_images table
            if LISTINGS_TABLE == "listings_v2":
                # Lấy bản đồ URL cũ để so khớp cập nhật cho listings_custom_v2
                old_rows = cursor.execute(
                    "SELECT image_url, r2_url FROM listings_images WHERE tk_id = ?",
                    (tk_id,)
                ).fetchall()
                old_url_map = {r[0]: r[1] for r in old_rows if r[0]}

                # Update diagram images
                for s_num, clean_s in enumerate([clean_sodo1, clean_sodo2, clean_sodo3, clean_sodo4, clean_sodo5], start=1):
                    orig_s = [original_sodo1, original_sodo2, original_sodo3, original_sodo4, original_sodo5][s_num-1]
                    if orig_s and clean_s:
                        cursor.execute(
                            "UPDATE listings_images SET r2_url = ? WHERE tk_id = ? AND image_url = ?",
                            (clean_s, tk_id, orig_s)
                        )
                # Update interior/house images
                for idx, orig_img_url in enumerate(raw_images_tk):
                    if idx < len(drive_links):
                        mig_img_url = drive_links[idx]
                        if mig_img_url:
                            cursor.execute(
                                "UPDATE listings_images SET r2_url = ? WHERE tk_id = ? AND image_url = ?",
                                (mig_img_url, tk_id, orig_img_url)
                            )

                # Đồng bộ cập nhật các link mới (R2 mới) vào listings_custom_v2.images_metadata_json nếu đã tồn tại
                system_id = row["System_ID"] if "System_ID" in row.keys() else d.get("System_ID")
                if system_id:
                    custom_row = cursor.execute(
                        "SELECT images_metadata_json FROM listings_custom_v2 WHERE System_ID = ?",
                        (system_id,)
                    ).fetchone()
                    if custom_row and custom_row[0]:
                        try:
                            images_meta = json.loads(custom_row[0])
                            updated_meta = []
                            has_meta_updates = False
                            for img_obj in images_meta:
                                if not isinstance(img_obj, dict):
                                    updated_meta.append(img_obj)
                                    continue
                                url = img_obj.get("url")
                                if not url:
                                    updated_meta.append(img_obj)
                                    continue

                                new_url = url
                                # So khớp với ảnh thô
                                for orig_idx, orig_url in enumerate(raw_images_tk):
                                    if orig_url and (orig_url == url or old_url_map.get(orig_url) == url):
                                        if orig_idx < len(drive_links) and drive_links[orig_idx]:
                                            new_url = drive_links[orig_idx]
                                            break

                                # So khớp với sơ đồ
                                for orig_s, clean_s in [
                                    (original_sodo1, clean_sodo1),
                                    (original_sodo2, clean_sodo2),
                                    (original_sodo3, clean_sodo3),
                                    (original_sodo4, clean_sodo4),
                                    (original_sodo5, clean_sodo5)
                                ]:
                                    if orig_s and (orig_s == url or old_url_map.get(orig_s) == url):
                                        if clean_s:
                                            new_url = clean_s
                                            break

                                if new_url != url:
                                    img_obj["url"] = new_url
                                    has_meta_updates = True
                                updated_meta.append(img_obj)

                            if has_meta_updates:
                                cursor.execute(
                                    "UPDATE listings_custom_v2 SET images_metadata_json = ? WHERE System_ID = ?",
                                    (json.dumps(updated_meta), system_id)
                                )
                                add_log_message(f"  [🔄 Cập nhật Custom] Đã đồng bộ link ảnh mới vào images_metadata_json của căn {tk_id}")
                        except Exception as e_meta:
                            add_log_message(f"  [⚠️ WARNING] Không thể đồng bộ images_metadata_json cho {tk_id}: {str(e_meta)}")
            
            conn.commit()
            conn.close()
            conn = None
            
            processed += 1
            add_log_message(f"[✅ SQLite] Đã cập nhật SQLite cục bộ cho {tk_id}: Sơ đồ thửa đất và hình ảnh R2. Trạng thái -> raw_complete")
            
            # 5. Tự động xuất bản trực tiếp lên Google Sheets Pool (nếu không yêu cầu skip)
            if not skip_sheets_publish:
                add_log_message(f"[⚡ AUTO-SHEETS] Đang tự động đẩy dòng dữ liệu 79 cột lên tab Pool của Google Sheets...")
                res_publish = execute_publish_listing(tk_id)
                if res_publish.get("status") == "success":
                    add_log_message(f"[✅ AUTO-SHEETS SUCCESS] Tự động xuất bản thành công căn {tk_id} lên Google Sheets Pool! Trạng thái SQLite -> published")
                else:
                    add_log_message(f"[⚠️ AUTO-SHEETS FAILED] Tự động đẩy Sheets thất bại: {res_publish.get('message')}. Giữ trạng thái SQLite -> raw_complete để đẩy thủ công sau.")
            else:
                add_log_message(f"[ℹ] Đã bỏ qua xuất bản Sheets tự động cho căn {tk_id} để chuẩn bị ghi Batch.")
                
        except Exception as e:
            add_log_message(f"[❌ LỖI] Gặp sự cố trong quy trình tự động hóa Curation & Xuất bản cho {tk_id}: {str(e)}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            
        # Throttling tối ưu bảo vệ IP: Cloudflare R2 cực nhanh (0.5 - 1.5s), Google Drive API (1.5 - 3.0s)
        if use_r2:
            sleep_time = random.uniform(0.5, 1.5)
        else:
            sleep_time = random.uniform(1.5, 3.0)
        time.sleep(sleep_time)
        
    add_log_message(f"[🏁] HOÀN TẤT LUỒNG DI CƯ: Đã xử lý {processed} căn.")


def generate_fallback_content_python(d):
    so_nha = safe_str(d.get("Ngo_So_nha") or d.get("Ngo_So_nha_") or "")
    duong = safe_str(d.get("Duong") or d.get("Duong_") or "")
    dt = safe_str(d.get("DT_Thuc_te") or d.get("DT_Thuc_te_") or d.get("Dien_tich") or "")
    tang = safe_str(d.get("So_Tang") or d.get("So_Tang_") or "")
    mat = safe_str(d.get("Mat_Tien") or d.get("Mat_Tien_") or "")
    dai = safe_str(d.get("Chieu_dai") or d.get("Chieu_dai_") or "")
    gia = safe_str(d.get("Gia_chao") or d.get("Gia_chao_") or "")

    kich_thuoc = f"{mat}x{dai}" if mat and dai else ""
    try:
        gia_ty = float(gia)
        if gia_ty > 100:
            gia_ty = gia_ty / 1000
        gia_format = f"{gia_ty}T" if gia_ty > 0 else ""
    except ValueError:
        gia_format = gia

    title_parts = []
    if duong:
        title_parts.append(duong)
    if dt:
        title_parts.append(f"{dt}m2")
    if kich_thuoc:
        title_parts.append(kich_thuoc)
    if tang:
        title_parts.append(f"{tang} tầng")
    if gia_format:
        title_parts.append(gia_format)

    title = " - ".join(title_parts)
    desc = d.get("Mo_ta_chi_tiet") or d.get("Noi_dung_chinh") or ""
    return {
        "tieu_de_public": title,
        "mo_ta_public": desc,
        "phuong_cu": ""
    }

def generate_ai_curation_for_listing_backend(d, cfg):
    import requests
    import json
    api_key = cfg.get("openai_api_key", "").strip()
    if not api_key:
        add_log_message("[🤖 AUTO-AI] Chưa cấu hình OpenAI API Key. Bỏ qua gọi AI và dùng fallback format.")
        return generate_fallback_content_python(d)

    api_base = cfg.get("openai_api_base", "https://api.openai.com/v1").strip().rstrip('/')
    system_prompt = cfg.get("openai_system_prompt", DEFAULT_CONFIG["openai_system_prompt"])

    so_nha = safe_str(d.get("Ngo_So_nha") or d.get("Ngo_So_nha_") or "")
    duong_truoc_nha = safe_str(d.get("Duong_truoc_nha_m") or d.get("Duong_truoc_nha_m_") or "")
    phan_loai_hem = safe_str(d.get("Phan_loai_Hem") or d.get("Phan_loai_Hem_") or "").lower()

    is_mat_tien = False
    if so_nha:
        if "." not in so_nha:
            is_mat_tien = True
    elif "mặt tiền" in phan_loai_hem or "mặt phố" in phan_loai_hem:
        is_mat_tien = True

    try:
        width_val = float(duong_truoc_nha) if duong_truoc_nha else 0.0
    except ValueError:
        width_val = 0.0

    tien_to = ""
    if is_mat_tien:
        tien_to = "Mặt tiền "
    elif width_val >= 4.0:
        tien_to = "HXH "

    gia_chao = d.get("Gia_chao") or d.get("Gia_chao_") or ""
    try:
        gia_ty = float(gia_chao)
        if gia_ty > 100:
            gia_ty = gia_ty / 1000
        gia_format = f"{gia_ty} tỷ" if gia_ty > 0 else ""
    except ValueError:
        gia_format = gia_chao

    user_prompt = (
        "THÔNG TIN CĂN NHÀ:\n"
        f"- Địa chỉ: {d.get('Ngo_So_nha', '')} {d.get('Duong', '')}, Phường {d.get('Phuong', '')}, Quận {d.get('Quan', '')}\n"
        f"- Nội dung chính gốc (chứa kích thước ở đầu): {d.get('Noi_dung_chinh', '')}\n"
        f"- DT Thực tế: {d.get('DT_Thuc_te', '')}m2 | DT Trên sổ: {d.get('DT_Tren_so', '')}m2\n"
        f"- Chiều ngang (mặt tiền): {d.get('Mat_Tien', '')}m\n"
        f"- Hướng: {d.get('Huong', '')}\n"
        f"- Kết cấu: {d.get('So_Tang', '')} tầng, {d.get('So_phong_ngu', '')} PN, {d.get('So_nha_ve_sinh', '')} WC\n"
        f"- Hẻm: {d.get('Phan_loai_Hem', '')} (Rộng: {d.get('Duong_truoc_nha_m', '')}m)\n"
        f"- Giá: {gia_format}\n"
        f"- Phân loại / Tag USP: {d.get('Phan_loai', '')}\n"
        f"- Điểm nổi bật của căn nhà (nguồn USP chính): {d.get('Mo_ta_chi_tiet', '')}\n\n"
        "LƯU Ý QUAN TRỌNG: Đọc kỹ 'Nội dung chính gốc', 'Phân loại / Tag USP' và 'Điểm nổi bật' — bắt buộc phản ánh các thông số kỹ thuật và ưu điểm vào Tiêu đề và Mô tả. BẮT BUỘC bắt đầu phần tiêu đề trực tiếp bằng tiền tố '" + tien_to + "' kết hợp liền mạch với Tên đường (TUYỆT ĐỐI không chèn thêm bất kỳ dấu gạch ngang, dấu chấm hay ký tự đặc biệt nào giữa tiền tố này và tên đường, Ví dụ: " + (f"'{tien_to}Trần Quang Diệu - ...'" if tien_to else "'Trần Quang Diệu - ...'") + ").\n"
        "🚨 YÊU CẦU ĐỊNH DẠNG: Bắt buộc phải trả về kết quả dưới định dạng JSON sạch (respond in json format) theo đúng cấu trúc yêu cầu trong System Prompt."
    )

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"}
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{api_base}/chat/completions", json=payload, headers=headers, timeout=30)
        res_json = response.json()

        if response.status_code == 200:
            ai_message = res_json["choices"][0]["message"]["content"]
            add_log_message(f"[🤖 AI] Nhận kết quả từ OpenAI: {ai_message}")
            ai_data = json.loads(ai_message)

            tieu_de_raw = ""
            for k in ["tieuDe", "tieu_de", "tieuDePublic", "tieu_de_public", "tieu de", "Tiêu đề", "tiêu đề"]:
                if k in ai_data and ai_data[k]:
                    tieu_de_raw = ai_data[k]
                    break
            if not tieu_de_raw:
                tieu_de_raw = next((v for k, v in ai_data.items() if "tieu" in k.lower()), "")

            mo_ta_raw = ""
            for k in ["moTa", "mo_ta", "moTaPublic", "mo_ta_public", "mo ta", "Mô tả", "mô tả"]:
                if k in ai_data and ai_data[k]:
                    mo_ta_raw = ai_data[k]
                    break
            if not mo_ta_raw:
                mo_ta_raw = next((v for k, v in ai_data.items() if "mo" in k.lower() and "phuong" not in k.lower()), "")

            phuong_cu_raw = ""
            for k in ["phuongCu", "phuong_cu", "phuong cu", "Phường cũ", "phường cũ"]:
                if k in ai_data and ai_data[k]:
                    phuong_cu_raw = ai_data[k]
                    break
            if not phuong_cu_raw:
                phuong_cu_raw = next((v for k, v in ai_data.items() if "phuong" in k.lower() or "old" in k.lower()), "")

            tieu_de_clean = trim_tieu_de_bds(tieu_de_raw)
            return {
                "tieu_de_public": tieu_de_clean,
                "mo_ta_public": mo_ta_raw,
                "phuong_cu": phuong_cu_raw
            }
        else:
            err_msg = res_json.get("error", {}).get("message", "Lỗi không xác định từ OpenAI.")
            add_log_message(f"[🤖 AUTO-AI ERROR] OpenAI API Error: {err_msg}. Dùng fallback format.")
            return generate_fallback_content_python(d)
    except Exception as e:
        add_log_message(f"[🤖 AUTO-AI ERROR] Lỗi khi gửi OpenAI API: {str(e)}. Dùng fallback format.")
        return generate_fallback_content_python(d)

def run_ai_curation_for_crawled_listing(tk_id, data):
    import sqlite3
    import json
    import pool_lego
    run_ai = data.get("run_ai", False)
    if run_ai:
        conn_check = None
        conn_update = None
        try:
            cfg = load_config()
            conn_check = sqlite3.connect(DB_FILE, timeout=30.0)
            conn_check.row_factory = sqlite3.Row
            cursor_check = conn_check.cursor()
            saved_row = cursor_check.execute(f"SELECT * FROM {LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
            conn_check.close()
            conn_check = None

            if saved_row:
                d_norm = normalize_listing_for_client(saved_row)
                ai_result = generate_ai_curation_for_listing_backend(d_norm, cfg)
                if ai_result:
                    conn_update = sqlite3.connect(DB_FILE, timeout=30.0)
                    cursor_update = conn_update.cursor()
                    col_tieu_de = pool_lego.get_safe_col_name("Tiêu đề Public")
                    col_mo_ta = pool_lego.get_safe_col_name("Mô tả Public")
                    col_phuong_cu = pool_lego.get_safe_col_name("Phường cũ (AI)")

                    cursor_update.execute(
                        f"UPDATE {LISTINGS_TABLE} SET `{col_tieu_de}` = ?, `{col_mo_ta}` = ?, `{col_phuong_cu}` = ? WHERE tk_id = ?",
                        (ai_result.get("tieu_de_public", ""), ai_result.get("mo_ta_public", ""), ai_result.get("phuong_cu", ""), tk_id)
                    )
                    conn_update.commit()
                    conn_update.close()
                    conn_update = None
                    add_log_message(f"[⚡ AUTO-AI SUCCESS] Đã tự động tạo Tiêu đề Public và Mô tả bằng AI cho căn {tk_id}")
        except Exception as e_ai:
            add_log_message(f"[❌ AUTO-AI ERROR] Lỗi tự động tạo Curation AI cho căn {tk_id}: {str(e_ai)}")
        finally:
            if conn_check:
                try:
                    conn_check.close()
                except Exception:
                    pass
            if conn_update:
                try:
                    conn_update.close()
                except Exception:
                    pass

def execute_publish_listing(tk_id):
    """
    Wrapper chuyển tiếp cuộc gọi xuất bản tin lên Google Sheets bằng cách gọi pool_lego.publish_listing.
    """
    import pool_lego
    return pool_lego.publish_listing(
        tk_id=tk_id,
        get_google_credentials=get_google_credentials,
        load_config=load_config,
        add_log_message=add_log_message,
        db_file=DB_FILE
    )


# ==================================================
# API ENDPOINTS (BLUEPRINTS REGISTRATION)
# ==================================================
from api.routes_pool import routes_pool
from api.routes_curation import routes_curation
from api.routes_sync import routes_sync
from api.routes_images import routes_images
from api.routes_crawl import routes_crawl
from api.routes_system import routes_system
from api.routes_links import routes_links

app.register_blueprint(routes_pool)
app.register_blueprint(routes_curation)
app.register_blueprint(routes_sync)
app.register_blueprint(routes_images)
app.register_blueprint(routes_crawl)
app.register_blueprint(routes_system)
app.register_blueprint(routes_links)


if __name__ == '__main__':
    # Tự động khởi tạo hoặc thực hiện di cư (migration) cột database SQLite cũ
    try:
        fetcher.init_db()
    except Exception as e:
        add_log_message(f"[⚠️ WARNING] Không thể khởi tạo database: {str(e)}")
    
    # [ANTI-MALFORMED] Kiểm tra toàn vẹn CSDL 1 lần khi khởi động (Phương án C)
    try:
        from core.db import startup_integrity_check
        db_healthy = startup_integrity_check(DB_FILE)
        if db_healthy:
            add_log_message(f"[🛡️ Integrity Guard] CSDL '{DB_FILE}' đã qua kiểm tra toàn vẹn ✅")
        else:
            from core.db import get_integrity_status
            status = get_integrity_status()
            add_log_message(f"[🚨🚨🚨 CẢNH BÁO NGHIÊM TRỌNG] CSDL '{DB_FILE}' BỊ HỎNG! Chi tiết: {status['details']}")
            add_log_message(f"[🚨] Vui lòng khôi phục từ bản sao lưu gần nhất trước khi tiếp tục sử dụng!")
    except Exception as e:
        add_log_message(f"[⚠️ WARNING] Không thể kiểm tra toàn vẹn CSDL: {str(e)}")
        
    # Tự động khởi chạy tiến trình quét và di cư hình ảnh chạy ngầm nếu có căn chờ xử lý
    try:
        # Tắt tính năng tự động di cư hình ảnh chạy ngầm theo yêu cầu để tránh nghẽn IP khi cào tin
        # start_auto_migration_scheduler()
        add_log_message("[🚀] Tính năng tự động di cư hình ảnh chạy ngầm đang được TẮT (Bạn vẫn có thể bấm nút Di cư thủ công trên UI)...")
    except Exception as e:
        add_log_message(f"[⚠️ WARNING] Không thể cấu hình bộ quét di cư: {str(e)}")

    # Tự động kích hoạt bộ sao lưu CSDL định kỳ ngầm
    try:
        start_periodic_backup_scheduler()
        add_log_message("[🚀] Bật tính năng tự động SAO LƯU định kỳ (quét mỗi 15 phút - tối đa 5 bản)...")
    except Exception as e:
        add_log_message(f"[⚠️ WARNING] Không thể khởi chạy bộ sao lưu định kỳ: {str(e)}")
        
    cfg = load_config()
    port = int(os.environ.get("FLASK_PORT", 5001))
    add_log_message(f"[*] Khởi chạy local server tại: http://localhost:{port}")
    
    # Tự động kích hoạt mở trình duyệt tab mới sau 1.5 giây
    import webbrowser
    def auto_open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception as e:
            add_log_message(f"[⚠️] Không thể tự động mở trình duyệt: {str(e)}")
            
    threading.Thread(target=auto_open_browser, daemon=True).start()
    
    # Giải phóng port 5000/5001 nếu bị kẹt bởi phiên cũ (chỉ chạy trong __main__, không chạy khi import)
    free_ports()
    
    # Bảo vệ Flask server: auto-restart khi crash + ghi traceback vào app.log
    MAX_RESTART_ATTEMPTS = 3
    for _restart_attempt in range(MAX_RESTART_ATTEMPTS):
        try:
            app.run(host='0.0.0.0', port=port, debug=False)
            break  # Thoát bình thường (Ctrl+C)
        except KeyboardInterrupt:
            add_log_message("[🛑] Server dừng bởi người dùng (Ctrl+C).")
            break
        except SystemExit as e_exit:
            add_log_message(f"[🔴 CRASH] Flask server bị SystemExit (code={e_exit.code}). Lần thử {_restart_attempt+1}/{MAX_RESTART_ATTEMPTS}...")
            try:
                import traceback
                with open("app.log", "a", encoding="utf-8") as _crash_f:
                    _crash_f.write(f"\n--- SERVER CRASH #{_restart_attempt+1} (SystemExit code={e_exit.code}) ---\n")
                    _crash_f.write(traceback.format_exc())
                    _crash_f.write("\n")
            except Exception:
                pass
            if _restart_attempt < MAX_RESTART_ATTEMPTS - 1:
                add_log_message(f"[🔄] Đang tự động khởi động lại server sau 2 giây...")
                time.sleep(2)
            else:
                add_log_message(f"[🔴] Đã thử khởi động lại {MAX_RESTART_ATTEMPTS} lần mà vẫn thất bại. Server dừng hẳn.")
        except Exception as e_crash:
            add_log_message(f"[🔴 CRASH] Flask server crash: {str(e_crash)}. Lần thử {_restart_attempt+1}/{MAX_RESTART_ATTEMPTS}...")
            try:
                import traceback
                with open("app.log", "a", encoding="utf-8") as _crash_f:
                    _crash_f.write(f"\n--- SERVER CRASH #{_restart_attempt+1} ({type(e_crash).__name__}: {e_crash}) ---\n")
                    _crash_f.write(traceback.format_exc())
                    _crash_f.write("\n")
            except Exception:
                pass
            if _restart_attempt < MAX_RESTART_ATTEMPTS - 1:
                add_log_message(f"[🔄] Đang tự động khởi động lại server sau 2 giây...")
                time.sleep(2)
            else:
                add_log_message(f"[🔴] Đã thử khởi động lại {MAX_RESTART_ATTEMPTS} lần mà vẫn thất bại. Server dừng hẳn.")
