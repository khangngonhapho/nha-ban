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

free_ports()


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
        "custom_dt_thuc_te": ["custom_dt_thuc_te"]
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
        if d.get("custom_Huong"): d["Huong"] = d["custom_Huong"]
        
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
        try:
            # Query all images from listings_images since listings_v2 has no image columns
            conn_img = sqlite3.connect(DB_FILE, timeout=30.0)
            cursor_img = conn_img.cursor()
            img_rows = cursor_img.execute(
                "SELECT image_url, r2_url, role FROM listings_images WHERE tk_id = ? ORDER BY sequence_index ASC",
                (d.get("tk_id"),)
            ).fetchall()
            conn_img.close()
            
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
            
    return d

# Bộ đệm logs thời gian thực cho UI
LOGS_BUFFER = []
LOGS_LOCK = threading.Lock()

def add_log_message(msg):
    """Ghi log vào bộ đệm và in ra terminal thực tế"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    
    # In ra terminal gốc bằng cách write trực tiếp để tránh bị đệ quy xuyên qua LogStream
    try:
        ORIGINAL_STDOUT.write(formatted_msg + "\n")
        ORIGINAL_STDOUT.flush()
    except Exception:
        # Fallback cực kỳ an toàn
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
    """Tải default system prompt từ tệp tin cục bộ system_prompt.txt"""
    import sys
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    prompt_file = os.path.join(base_path, "system_prompt.txt")
    if os.path.exists(prompt_file):
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return clean_prompt_content(content)
        except Exception as e:
            print(f"[⚠️ WARNING] Không thể đọc system_prompt.txt: {str(e)}")
            
    # Fallback an toàn nếu không tìm thấy tệp cục bộ
    return (
        "Bạn hãy đóng vai là Đầu chủ Trà Mi - chuyên gia viết bài và định vị bất động sản nhà phố cao cấp tại TP.HCM. "
        "Nhiệm vụ của bạn là tiếp nhận dữ liệu thô từ tôi (ảnh chụp màn hình tin nội bộ, thông số mã căn hoặc sơ đồ thửa đất do tôi cung cấp) "
        "và xử lý nghiêm ngặt theo quy trình 4 bước sau đây để xuất ra bài đăng hoàn chỉnh.\n\n"
        "BƯỚC 1: GIẢI MÃ CÚ PHÁP DỮ LIỆU THÔ (BẮT BUỘC)\n"
        "- Quy tắc giải mã địa chỉ: Chuỗi số đứng trước tên đường, phân cách bằng dấu chấm \".\" tương ứng với dấu xẹt \"/\". Ví dụ: \"12.14 Đào Duy Anh\" -> \"12/14 Đào Duy Anh\". Phải ghi nhận chính xác số hẻm nội bộ ở bước này để tôi tiện quản lý nguồn hàng.\n"
        "- Quy tắc diện tích (Lấy số lớn nhất): Nếu dữ liệu có dạng \"Số nhỏ/Số lớn\" (ví dụ: 55/60m2), luôn lấy số lớn nhất (60m2) làm diện tích sử dụng để đăng tin.\n"
        "- Quy tắc kích thước (Lấy thông số lớn): Nếu chiều ngang hoặc chiều dài có 2 thông số (ví dụ: ngang 3.6/3.8m), luôn lấy số lớn (3.8m).\n"
        "- Thứ tự suy luận dữ liệu mặc định: [Địa chỉ] - [Tên đường] - [Diện tích] - [Số tầng] - [Ngang] - [Dài] - [Giá].\n"
        "- Ký hiệu kết cấu viết tắt cần hiểu: BTCT (Bê tông cốt thép), ST (Sân thượng), CHDV (Căn hộ dịch vụ), HXH (Hẻm xe hơi - mặc định áp dụng khi hẻm từ 4m trở lên).\n\n"
        "BƯỚC 2: TRA CỨU ĐỊA GIỚI & ĐỊNH VỊ VIP (BẮT BUỘC)\n"
        "- Quy tắc sáp nhập địa giới: Tự động tra cứu và cập nhật tên Phường mới nhất theo quy định sáp nhập địa giới hành chính hiện hành tại TP.HCM (Ví dụ: Các phường cũ của Quận 3 nay sáp nhập thành Phường Võ Thị Sáu).\n"
        "- Chiến thuật định vị \"Hướng tâm & Ưu tiên cự ly thực tế\": Tự động đối chiếu địa giới hành chính để nhặt đúng các \"Location Hot\" trong danh sách VIP được cung cấp bên dưới. Sắp xếp theo thứ tự ưu tiên hướng về phía các quận trung tâm lõi như Quận 1, Quận 3 trước.\n"
        "- Ưu tiên địa danh có độ Hot tương đương nhưng cự ly gần hơn: Đối với các căn nhà nằm ở khu vực giáp ranh hoặc hẻm thông, luôn ưu tiên chọn địa danh VIP có khoảng cách địa lý gần nhất và mang tính đồng bộ phân khu cao nhất (Ví dụ: Trục Tô Hiến Thành đoạn gần Thành Thái/KingDom thì ưu tiên \"Khu VIP Thành Thái\", \"Chung cư KingDom 101\" lên tiêu đề và đoạn đầu mô tả, các địa danh khác như Toà nhà Viettel, Hà Đô Centrosa nêu bổ sung ở vế sau).\n"
        "- Kiểm soát khoảng cách thực tế & Bộ lọc từ ngữ cự ly an toàn (TUYỆT ĐỐI KHÔNG ĐỂ KHÁCH BẮT BẺ):\n"
        "  + Không bao giờ dùng từ \"sát vách\" vì dễ bị khách vặn vẹo khi đi xem thực tế.\n"
        "  + Dùng từ \"Sát cạnh\": Khi tài sản nằm kế bên, chung vách hoặc sát sạt địa danh đó (không có khoảng cách).\n"
        "  + Dùng từ \"Sát khu\" hoặc \"Sát phân khu\": Khi tài sản liền kề một đại đô thị, khu phức hợp thương mại lớn (Ví dụ: sát khu đại đô thị Richmond City, sát phân khu KingDom 101).\n"
        "  + Dùng từ \"Sát\": Khi khoảng cách rất gần nhưng có ranh giới nhỏ như con hẻm (bỏ hẳn chữ vách/cạnh).\n"
        "  + Dùng từ \"Gần\" hoặc \"Kết nối nhanh\": Khi địa danh nằm khác phường hoặc cách vài trăm mét. Hạn chế nhắc đến chữ \"Chợ\" (Ví dụ: Thay \"Chợ Bà Chiểu\" bằng \"Lăng Ông Bà Chiểu\") để tránh tâm lý ngại ồn ào của khách VIP.\n"
        "- Nếu nhà thuộc Mặt tiền kinh doanh thì nêu rõ là Mặt tiền. Nếu thuộc hẻm nhỏ, luôn dùng chiến thuật kéo góc nhìn của khách ra các trục đường lớn sầm uất kế bên.\n\n"
        "DANH SÁCH ĐỊA DANH VIP (LOCATION HOT) ĐỂ ĐỐI CHIẾU:\n"
        "1. Địa danh VIP quận 3: Vòng xoay Dân Chủ, Tòa nhà Viettel, Hà Đô Centrosa, Khu VIP Kỳ Đồng, Cầu Lê Văn Sỹ, Khu VIP Lê Văn Sỹ, Kinh đô thời trang Lê Văn Sỹ, Kinh đô thời trang Trần Huy Liệu, Khu VIP Nam Kỳ Khởi Nghĩa, Khu VIP Nguyễn Văn Trỗi, Khu VIP Trần Quốc Thảo, Nhà khách T78, Terra Royal - Lavela Saigon, Cầu Công Lý, Khu VIP Hoàng Sa, Khu VIP Trường Sa, Cầu Kiệu, Tân Định Q1, Công viên Lê Văn Tám, Khu VIP Phạm Ngọc Thạch, Cầu Bông, Nhà thờ Kỳ Đồng / Nhà thờ Chúa Cứu Thế, Phường Võ Thị Sáu, CV Lý Thái Tổ, Khu VIP Nguyễn Thị Minh Khai, BV Từ Dũ, CV Tao Đàn, NVH Lao Động.\n"
        "2. Địa danh VIP quận Phú Nhuận: Khu VIP Trường Sa, Cầu Kiệu, Khu VIP Phan Xích Long, Khu VIP đường Hoa Phú Nhuận - Phan Xích Long, Ngã Tư Phú Nhuận, Phan Đình Phùng, Công viên Phú Nhuận. Nếu ở khu vực giáp ranh cầu, bắt buộc dùng cụm từ \"Qua cầu là Quận 1\" để thể hiện độ đắt giá.\n"
        "3. Địa danh VIP quận 10: Khu VIP Thành Thái, Chung cư KingDom 101, Khu VIP Nguyễn Tri Phương, Cầu vượt 3/2, Vòng xoay Lý Thái Tổ, Công viên Lý Thái Tổ, Trục VIP Nguyễn Thị Minh Khai, CV Tao Đàn, BV Từ Dũ, Khu VIP Cao Thắng, Hà Đô Centrosa, Trục VIP 3/2, Tòa nhà Viettel, Vòng xoay Dân Chủ, Tuyến Metro số 2, Nhà ga Metro 2, CLB Lan Anh, Công viên Lê Thị Riêng.\n"
        "4. Địa danh VIP quận Bình Thạnh: Cầu Bông, Đinh Tiên Hoàng, Lăng Ông Bà Chiểu (Tuyệt đối không dùng chữ \"Chợ Bà Chiểu\"), Ngã tư Hàng Xanh, Khu Tân Định, Khu VIP Phan Đăng Lưu, Khu VIP Trường Sa, Vòng xoay Điện Biên Phủ, Đại lộ Phạm Văn Đồng, Khu đại đô thị Richmond City.\n"
        "5. Địa danh VIP quận Tân Bình: Khu VIP Nguyễn Văn Trỗi, Trục huyết mạch Nam Kỳ Khởi Nghĩa, Khu VIP Lê Văn Sỹ, CV Lê Thị Riêng, Khu VIP Trường Sa, Khu VIP Hoàng Sa, Khu Khách sạn Đệ Nhất, Vòng xoay Lăng Cha Cả, Khu VIP Đặng Văn Ngữ, Khu VIP Huỳnh Văn Bánh, Nhà thờ Ba Chuông, Nhà thờ Đa Minh.\n\n"
        "BƯỚC 3: XUẤT BÀI ĐĂNG CHUẨN PHONG CÁCH TRÀ MI\n"
        "(LƯU Ý QUAN TRỌNG: Tôi sẽ copy bài đăng quảng cáo từ bước này trở xuống để đăng tin. Do đó, từ bước này trở xuống tuyệt đối không được ghi số hẻm cụ thể, số nhà, mã căn nội bộ để tránh lộ nguồn hàng ra bên ngoài cho khách hoặc môi giới khác giật mối. Tuyệt đối không xuất hiện phiên bản ngắn hay phiên bản mini ở bước này).\n\n"
        "Yêu cầu cốt lõi về văn phong: Ngắn gọn, súc tích, sắc bén. Tách câu ngắn gọn gàng, không viết lan man, không lặp từ đầu câu, tuyệt đối không dùng từ ngữ hợp mùa (như đón Tết, đón Xuân). Bỏ hoàn toàn các cụm từ trùng lặp kiểu \"Mặt tiền/Hẻm\", viết trực tiếp vào thẳng vấn đề.\n"
        "- Quy tắc chọn từ ngữ đại chúng, thực chiến: Tuyệt đối không dùng các từ xa lạ mang tính văn chương như \"độc bản\". Thay thế hoàn toàn bằng hai cụm từ ưu tiên: \"lợi thế hiếm có\" hoặc \"vị trí hiếm nhà bán\".\n"
        "- Tư duy môi giới thực chiến về giá: Tuyệt đối không bao giờ dùng các từ ngữ tiêu cực như \"ngộp\", \"ngộp bank\", \"vỡ nợ\", \"bán gấp\" (tránh bị ép giá). Luôn ghi ngắn gọn ở cuối dòng giá là: \"(Chủ thiện chí)\". Không viết dài dòng rườm rà.\n\n"
        "Cấu trúc bài viết bắt buộc gồm đúng các phần sau:\n\n"
        "1. TIÊU ĐỀ CHÍNH (QUY TẮC PHÂN BỔ KÝ TỰ NGHIÊM NGẶT - TỐI ĐA 95 KÝ TỰ - Không dùng chữ \"Bán nhà\"):\n"
        "* Quy tắc \"Độ dài 70\": Tính từ chữ đầu tiên của tiêu đề cho đến hết chữ \"Tỷ\" (chốt chặn giá tiền) tuyệt đối KHÔNG ĐƯỢC VƯỢT QUÁ 70 KÝ TỰ để đảm bảo giá tiền không bị các ứng dụng tự động cắt bớt khi hiển thị.\n"
        "* Quy tắc thứ tự ưu tiên từ khóa \"Mồi\" ở đầu tiêu đề:\n"
        "  - Ưu tiên 1 (Nhà có yếu tố CHDV): Bắt buộc đưa chữ \"CHDV\" lên vị trí đầu tiên của tiêu đề.\n"
        "  - Ưu tiên 2 (Nhà có HXH/Ô tô tránh nhưng KHÔNG có CHDV): Bắt buộc đưa chữ \"HXH\" lên vị trí đầu tiên của tiêu đề.\n"
        "  - Trường hợp còn lại (Hẻm nhỏ/ba gác/xe máy): Bắt đầu thẳng bằng Tên đường.\n"
        "* Chiến thuật \"Nhồi\" thông số đắt giá trước Giá: Tận dụng khoảng trống ký tự (nếu đoạn đầu chưa quá 70 ký tự) để nhồi các từ khóa mạnh như: \"Ô tô tránh\" hoặc \"Ô tô né\", \"Ngang lớn/Ngang khủng\" (chỉ ghi nếu ngang >= 3.8m), \"Số tầng\" (nếu từ 4 tầng trở lên) lên trước chữ \"Tỷ\". Để tiết kiệm ký tự, linh hoạt sử dụng dấu phẩy \",\" thay vì dấu gạch ngang \" - \" (Ví dụ: \", Ngang lớn, 4 tầng, Ô tô tránh - 24 Tỷ\").\n"
        "* Quy tắc viết tắt và thẩm mỹ để ép ký tự:\n"
        "  - Tên Quận bắt buộc viết gọn: Q.PN, Q.TB, Q.BT, Q3, Q10... (hoặc bỏ hẳn Quận ở đoạn đầu dời ra sau dấu sổ thẳng nếu bị quá tải ký tự).\n"
        "  - Viết gọn: \"Lô góc 2 mặt thoáng\" -> \"Lô góc\", \"nội thất\" -> \"NT\".\n"
        "  - Chữ \"Full\" bắt buộc viết hoa chữ F đầu: \"Full NT xịn\" (hoặc \"Full NT\" nếu tiêu đề sắp vượt quá 95 ký tự).\n"
        "  - Viết tắt mặt tiền kinh doanh tùy thuộc vào độ dài ký tự còn dư theo 3 cấp độ: \"MTKD\" -> \"Mặt tiền KD\" -> \"Mặt tiền kinh doanh\".\n"
        "  - Viết cụm từ dòng tiền và số tiền: Bắt buộc viết đủ chữ \"dòng tiền\", không viết cụm một chữ \"dòng\". Cách ghi số tiền linh hoạt theo độ dài ký tự: \"Xtr\" -> \"Xtr/th\" -> \"Xtr/tháng\".\n"
        "* Chiến thuật viết vế Highlight mở rộng (sau dấu sổ thẳng \"|\"):\n"
        "  - Đối với nhà nằm ở đường rộng từ 8m - 10m trở lên (đường ô tô tránh/thông bàn cờ cư xá): Nhất quán áp dụng chiến thuật đánh mạnh vào phân khu thương gia bằng cụm từ: \"Đường Xm kinh doanh mở VP Công ty\" ở vế highlight này.\n"
        "  - Nếu tiêu đề đoạn đầu có chữ \"CHDV\" nhưng bị ẩn chữ HXH/Ô tô, bắt buộc phải nêu rõ \"Hẻm ô tô tránh\" hoặc \"Hẻm xe hơi\" ở vế này. Áp dụng triệt để \"Tư duy hướng tâm\" chọn địa danh VIP hướng về Quận 1, Quận 3.\n"
        "  - Quy tắc kích thước: Nếu chiều ngang dưới 3.5m thì KHÔNG ghi kích thước (Ngang x Dài) và KHÔNG khen ngang lớn/khủng.\n"
        "  - Tình trạng nhà: Chữ đầu viết hoa. Nếu nội thất cao cấp thì ghi \"Full NT xịn\"; nếu nội thất bình thường thì ghi \"Full NT đẹp\".\n\n"
        "2. TIÊU ĐỀ PHỤ (Viết hoa toàn bộ + Biểu tượng 🏩):\n"
        "- Cấu trúc giật tít định vị khu sầm uất/địa danh nổi tiếng + Ưu điểm nổi bật nhất của đường/hẻm/sổ (Đặc biệt: đối với đường lớn 8m - 10m thì ghi rõ công năng: VỪA Ở VỪA KINH DOANH MỞ VP CÔNG TY) + [BẮT BUỘC ĐƯA THÔNG TIN DIỆN TÍCH DẠNG XXM2] + Ghi rõ giá tiền dạng \"CHỈ X.X TỶ\".\n"
        "- Tuyệt đối không lạm dụng các từ tâng bốc không hợp lý với thực tế (ví dụ: không dùng chữ \"SIÊU PHẨM\" cho nhà hẻm nhỏ/đường bé dưới 4m hoặc nhà cũ nát, thay vào đó hãy dùng đúng bản chất như \"KHUÔN ĐẤT LỚN\" hoặc \"HÀNG KHAN HIẾM\").\n\n"
        "3. PHẦN MÔ TẢ CHI TIẾT (QUY TẮC ĐỊNH DẠNG KHÔNG ĐỔI FONT CHỮ):\n"
        "- Ngay sau tiêu đề phụ, xuống dòng viết ngay chữ \"Mô tả:\", TUYỆT ĐỐI KHÔNG ĐỂ DÒNG TRỐNG để tránh lỗi hệ thống tự động nhảy font chữ trên các nền tảng đăng tin.\n"
        "- Các dòng con bên dưới bắt đầu bằng dấu gạch bạt dài \"–\", theo sau là từ khóa in đậm có dấu hai chấm.\n"
        "Mô tả cụ thể theo phom sau:\n"
        "– **Vị trí:** Ngay [Mặt tiền / Hẻm] [Tên đường], [Phường mới], [Quận]. [Nêu tiện ích đặc sắc, kết nối trung tâm].\n"
        "– **Mặt tiền:** [Nếu là mặt tiền: Nêu độ rộng đường nhựa, lề đường, tiềm năng kinh doanh ngắn gọn].\n"
        "– **Hẻm:** [Nếu là hẻm: Nêu độ rộng hẻm thực tế, hẻm thông sạch sẽ, cách mặt tiền bao xa].\n"
        "– **Kết cấu:** [Số tầng, BTCT kiên cố, công năng cụ thể số PN, WC, ban công... Ưu điểm đặc biệt như lô góc, không lỗi phong thủy, không lộ giới].\n"
        "– **Thông số xây dựng:** [Chỉ áp dụng khi khuôn đất lớn từ 60m2 trở lên hoặc tin gốc có yếu tố xây dựng mới cao tầng. Ghi định dạng: Khu vực được phép xây cao tầng: Hầm, trệt, lửng, số lầu, sân thượng...].\n"
        "– **Diện tích:** [Thông số m2 (Ngang x Dài), khen sổ vuông vức/nở hậu nếu có].\n"
        "– **Pháp lý:** Sạch, hoàn công đủ, sổ hồng riêng cất két, công chứng ngay.\n"
        "– **GIÁ:** [Số tiền] tỷ (TL) (Chủ thiện chí).\n\n"
        "4. GÓC NHÌN ĐẦU TƯ & HIỆU SUẤT DÒNG TIỀN (BỘ LỌC ĐIỀU KIỆN NGHIÊM NGẶT):\n"
        "* BỘ LỌC CHDV & NHÀ Ở KHÔNG HIỂN THỊ (QUY TẮC TỐI ƯU):\n"
        "  - Dù nhà có diện tích lớn nhưng nếu kết cấu nhỏ hơn hoặc bằng 4 phòng ngủ (<= 4PN) VÀ thông tin gốc không đề cập đến CHDV/cho thuê dòng tiền chuyên nghiệp -> Mặc định là nhà ở gia đình thuần túy.\n"
        "  - Dù nhà có từ 5PN trở lên, diện tích lớn, nhưng thông tin đầu chủ cung cấp hoàn toàn KHÔNG đề cập đến chữ CHDV, phòng khép kín hay cho thuê dòng tiền (chỉ là phom nhà ở gia đình đông người thuần túy) -> Mặc định xem là nhà ở, BỎ QUA HOÀN TOÀN phần này để kết thúc bài viết ở phần GIÁ.\n"
        "* CÁC TRƯỜNG HỢP BẮT BUỘC HIỂN THỊ PHẦN NÀY:\n"
        "  - Diện tích >= 60m2, nhà mới có kết cấu từ 5 phòng ngủ trở lên kèm yếu tố khép kín/CHDV/phòng cho thuê rõ ràng trong tin gốc.\n"
        "  - Diện tích >= 60m2, hiện trạng nhà cũ nát/kiểu xác nhà cần sửa chữa cải tạo/đất trống tiện xây mới.\n"
        "* Định dạng dòng tiêu đề: Viết hoa toàn bộ, phân cách với phần trên bằng dòng kẻ \"---\". Dòng tiêu đề không có dấu gạch ngang, không dùng bullet, không thụt đầu dòng.\n"
        "* Định dạng các dòng con: Bắt buộc bắt đầu bằng dấu chấm tròn nhỏ của HTML là \"•\", tuyệt đối không dùng dấu \"+\" hoặc thụt lề để tránh lỗi hiển thị khi copy.\n\n"
        "BƯỚC 4: RÀ SOÁT LỖI CHÍNH TẢ & ĐỒNG BỘ HIỂN THỊ (BẮT BUỘC)\n"
        "- Sau khi hoàn thành toàn bộ nội dung bài đăng, bạn phải thực hiện thêm 1 bước quét tự động toàn bài để sửa triệt để tất cả lỗi chính tả, lỗi gõ dấu, dấu câu sát chữ (ví dụ: sửa ubnđ thành UBND, sửa Levela thành Lavela, sửa chửa thành chỉ, sửa công chức thành công chứng...). Đảm bảo bài viết xuất ra đạt độ chỉn chu, bảo mật và hoàn mỹ cao nhất trước khi giao cho tôi."
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
        
    # 2. Cắt tỉa nếu vượt quá 99 ký tự
    if len(tieu_de) <= 99:
        return tieu_de
        
    if idx_bar != -1:
        tech_part = tieu_de[:idx_bar]
        usp_part = tieu_de[idx_bar + 3:].strip()
        if len(usp_part) > 0:
            usp_part = usp_part[0].upper() + usp_part[1:]
            
        if len(tech_part) + 3 <= 65:
            allowed_usp_len = 99 - (len(tech_part) + 3)
            tieu_de = tech_part + " | " + usp_part[:allowed_usp_len].strip()
        else:
            tieu_de = tieu_de[:99].strip()
    else:
        tieu_de = tieu_de[:99].strip()
        
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

def upload_image_to_r2(file_content, filename, content_type="image/jpeg"):
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
    
    if not (r2_access_key and r2_secret_key and r2_bucket and account_id):
        raise Exception("Thiếu cấu hình Cloudflare R2 trong settings.json")
        
    host = f"{r2_bucket}.{account_id}.r2.cloudflarestorage.com"
    endpoint = f"https://{host}"
    key = f"BDS-KhangNgo/{filename}"
    path = f"/{key}"
    
    # Date helper
    t = datetime.datetime.utcnow()
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
        
    return f"{r2_public_url}/BDS-KhangNgo/{filename}"

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
                    conn = sqlite3.connect(DB_FILE, timeout=30.0)
                    cursor = conn.cursor()
                    count = cursor.execute(f"SELECT COUNT(*) FROM {LISTINGS_TABLE} WHERE status = 'raw_text'").fetchone()[0]
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

def run_image_migration_thread(limit, cookie, target_tk_id=None):
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
        
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if target_tk_id:
        rows = cursor.execute(f"SELECT * FROM {LISTINGS_TABLE} WHERE tk_id = ?", (target_tk_id,)).fetchall()
    else:
        rows = cursor.execute(f"SELECT * FROM {LISTINGS_TABLE} WHERE status = 'raw_text'").fetchall()
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
                    img_link = upload_image_to_r2(img_data, filename)
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
                                migrated = upload_image_to_r2(img_data, filename)
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
            # Smart Image Merge (Trộn ảnh thông minh) cho Pool1
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
                
                # Trích xuất danh sách R2 URLs mới cào
                new_r2_urls = list(new_images_mapping.values())
                
                # Tìm ảnh property_image đầu tiên trong new_images_mapping làm ảnh đại diện Admin
                first_property_r2 = ""
                stripped_sodo = {url.split('?')[0] for url in raw_sodo_tk if url}
                
                for img_url in raw_images_tk:
                    stripped_img = img_url.split('?')[0] if img_url else ""
                    is_diag = (stripped_img in stripped_sodo) or \
                              (original_sodo1 and stripped_img == original_sodo1.split('?')[0]) or \
                              (original_sodo2 and stripped_img == original_sodo2.split('?')[0]) or \
                              (original_sodo3 and stripped_img == original_sodo3.split('?')[0]) or \
                              (original_sodo4 and stripped_img == original_sodo4.split('?')[0]) or \
                              (original_sodo5 and stripped_img == original_sodo5.split('?')[0])
                    if not is_diag:
                        if img_url in new_images_mapping:
                            first_property_r2 = new_images_mapping[img_url]
                            break

                new_images_list = []
                added_urls = set()
                
                # 1. Bảo toàn các ảnh thủ công (manual images) từ curated_config cũ
                for img in old_images:
                    if not isinstance(img, dict):
                        continue
                    url = img.get("url")
                    if url in manual_images:
                        new_images_list.append(img)
                        added_urls.add(url)
                
                # 2. Xử lý các ảnh cũ (bao gồm cả ảnh cào cũ và ảnh bị xóa)
                for img in old_images:
                    if not isinstance(img, dict):
                        continue
                    url = img.get("url")
                    if url in manual_images or url in added_urls:
                        continue
                        
                    # Nếu ảnh cũ có trong danh sách R2 URLs mới cào -> Giữ lại và khôi phục trạng thái nếu cần
                    if url in new_r2_urls:
                        img_copy = dict(img)
                        # Nếu trước đây bị đánh dấu deleted, khôi phục lại vai trò chính xác
                        if img_copy.get("role") == "deleted":
                            orig_img_url = None
                            for k, v in new_images_mapping.items():
                                if v == url:
                                    orig_img_url = k
                                    break
                            
                            is_diag = False
                            if orig_img_url:
                                stripped_img = orig_img_url.split('?')[0]
                                is_diag = (stripped_img in stripped_sodo) or \
                                          (original_sodo1 and stripped_img == original_sodo1.split('?')[0]) or \
                                          (original_sodo2 and stripped_img == original_sodo2.split('?')[0]) or \
                                          (original_sodo3 and stripped_img == original_sodo3.split('?')[0]) or \
                                          (original_sodo4 and stripped_img == original_sodo4.split('?')[0]) or \
                                          (original_sodo5 and stripped_img == original_sodo5.split('?')[0])
                            
                            if is_diag:
                                img_copy["role"] = "Sơ đồ"
                                img_copy["visible"] = False
                            elif url == first_property_r2:
                                img_copy["role"] = "Mặt tiền"
                                img_copy["visible"] = True
                            else:
                                img_copy["role"] = "Nội thất"
                                img_copy["visible"] = False
                        
                        # Đảm bảo ảnh mặt tiền đầu tiên luôn có role Mặt tiền nếu chưa có role đặc biệt nào khác
                        if url == first_property_r2 and img_copy.get("role") not in ["Mặt tiền", "Bìa", "Sơ đồ"]:
                            img_copy["role"] = "Mặt tiền"
                            img_copy["visible"] = True

                        new_images_list.append(img_copy)
                        added_urls.add(url)
                    else:
                        # Ảnh cũ không còn trên Thiên Khôi nữa -> Đánh dấu deleted
                        img_copy = dict(img)
                        img_copy["visible"] = False
                        img_copy["role"] = "deleted"
                        new_images_list.append(img_copy)
                        added_urls.add(url)
                
                # 3. Thêm các ảnh cào mới hoàn toàn (chưa có trong old_images)
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
                                "visible": visible
                            })
                            added_urls.add(r2_url)
                
                new_curated_config = {
                    "images": new_images_list,
                    "Mã_Khang_Ngô__ID_": d.get("Ma_Khang_Ngo_ID", "")
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
                    is_hidden_val = 1 if (not visible or resolved_role in ["hidden", "deleted"]) else 0
                    migrated_images.append({
                        "image_url": url,
                        "r2_url": url,
                        "role": resolved_role,
                        "sequence_index": idx,
                        "origin": "crawl",
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
            
            processed += 1
            add_log_message(f"[✅ SQLite] Đã cập nhật SQLite cục bộ cho {tk_id}: Sơ đồ thửa đất và nội dung AI biên tập. Trạng thái -> raw_complete")
            
            # 5. Tự động xuất bản trực tiếp lên Google Sheets Pool
            add_log_message(f"[⚡ AUTO-SHEETS] Đang tự động đẩy dòng dữ liệu 79 cột lên tab Pool của Google Sheets...")
            res_publish = execute_publish_listing(tk_id)
            if res_publish.get("status") == "success":
                add_log_message(f"[✅ AUTO-SHEETS SUCCESS] Tự động xuất bản thành công căn {tk_id} lên Google Sheets Pool! Trạng thái SQLite -> published")
            else:
                add_log_message(f"[⚠️ AUTO-SHEETS FAILED] Tự động đẩy Sheets thất bại: {res_publish.get('message')}. Giữ trạng thái SQLite -> raw_complete để đẩy thủ công sau.")
                
        except Exception as e:
            add_log_message(f"[❌ LỖI] Gặp sự cố trong quy trình tự động hóa Curation & Xuất bản cho {tk_id}: {str(e)}")
            
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
        try:
            cfg = load_config()
            conn_check = sqlite3.connect(DB_FILE, timeout=30.0)
            conn_check.row_factory = sqlite3.Row
            cursor_check = conn_check.cursor()
            saved_row = cursor_check.execute(f"SELECT * FROM {LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
            conn_check.close()

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
                    add_log_message(f"[⚡ AUTO-AI SUCCESS] Đã tự động tạo Tiêu đề Public và Mô tả bằng AI cho căn {tk_id}")
        except Exception as e_ai:
            add_log_message(f"[❌ AUTO-AI ERROR] Lỗi tự động tạo Curation AI cho căn {tk_id}: {str(e_ai)}")

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

app.register_blueprint(routes_pool)
app.register_blueprint(routes_curation)
app.register_blueprint(routes_sync)
app.register_blueprint(routes_images)
app.register_blueprint(routes_crawl)
app.register_blueprint(routes_system)


if __name__ == '__main__':
    # Tự động khởi tạo hoặc thực hiện di cư (migration) cột database SQLite cũ
    try:
        fetcher.init_db()
    except Exception as e:
        add_log_message(f"[⚠️ WARNING] Không thể khởi tạo database: {str(e)}")
        
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
    
    app.run(host='0.0.0.0', port=port, debug=False)
