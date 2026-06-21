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
def free_port_5000():
    try:
        import subprocess
        output = subprocess.check_output("netstat -aon", shell=True).decode('utf-8', errors='ignore')
        for line in output.strip().split('\n'):
            if "LISTENING" in line and ":5000" in line:
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    subprocess.run(f"taskkill /f /pid {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

free_port_5000()

from curator_html_data import CURATOR_HTML_CONTENT

# Khởi tạo Flask với static folder tuyệt đối
app = Flask(__name__, static_folder=static_folder, static_url_path='/static')

import pool_lego
from pool_lego import POOL_HEADERS, remove_accents, get_safe_col_name, gen_id_khang_ngo_python, get_db_file, init_db

# File cấu hình & cơ sở dữ liệu (Dùng đường dẫn tuyệt đối dựa trên PROJECT_ROOT)
DB_FILE = os.path.abspath(os.path.join(PROJECT_ROOT, get_db_file()))
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
        "Tinh": ["Tinh", "T_nh"]
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
    "prompt_google_doc_id": "12LaUJ-34eolQ9ElgQhpe5k9Mh_bn4B7p31DQAZ1Ncto",
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
MIGRATION_LOCK = threading.Lock()

def run_auto_migration_wrapper(cookie):
    global IS_MIGRATION_ACTIVE
    try:
        run_image_migration_thread(limit=None, cookie=cookie)
    except Exception as e:
        add_log_message(f"[❌ AUTO-MIGRATION ERROR] Lỗi trong tiến trình di cư tự động: {str(e)}")
    finally:
        with MIGRATION_LOCK:
            IS_MIGRATION_ACTIVE = False

def run_auto_migration_wrapper_with_limit(limit, cookie):
    global IS_MIGRATION_ACTIVE
    try:
        run_image_migration_thread(limit=limit, cookie=cookie)
    except Exception as e:
        add_log_message(f"[❌ MIGRATION ERROR] Lỗi trong tiến trình di cư thủ công: {str(e)}")
    finally:
        with MIGRATION_LOCK:
            IS_MIGRATION_ACTIVE = False

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

def run_image_migration_thread(limit, cookie, target_tk_id=None):
    """Tải và di cư hình ảnh chạy ngầm hoặc đồng bộ căn cụ thể (Throttled Mode)"""
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
                
                # 2. Bảo toàn và cập nhật các ảnh di cư cũ
                stripped_new_mapping = {}
                for k, v in new_images_mapping.items():
                    if k:
                        stripped_new_mapping[k.split('?')[0]] = v
                        
                for img in old_images:
                    if not isinstance(img, dict):
                        continue
                    url = img.get("url")
                    if url in manual_images:
                        continue
                    
                    orig_tk_url = None
                    for k, v in images_mapping.items():
                        if v == url:
                            orig_tk_url = k
                            break
                    
                    if orig_tk_url:
                        stripped_orig_tk = orig_tk_url.split('?')[0]
                        if stripped_orig_tk in stripped_new_mapping:
                            new_r2_url = stripped_new_mapping[stripped_orig_tk]
                            if new_r2_url not in added_urls:
                                img_copy = dict(img)
                                img_copy["url"] = new_r2_url
                                new_images_list.append(img_copy)
                                added_urls.add(new_r2_url)
                
                # 3. Thêm các ảnh di cư mới cào vào cuối danh sách
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
                            role = "Sơ đồ" if is_diag else "Nội thất"
                            visible = False if role in ["Sơ đồ", "Mặt tiền"] else True
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
            
            # Hẻm images (Bảo toàn dữ liệu cũ)
            for i in range(10):
                col_name = get_safe_col_name(f"Hình Hẻm {i+1}")
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
                
                # Loại bỏ các cột phẳng hình ảnh ở Pool1
                image_fields_to_skip = {
                    get_safe_col_name("Hình Nhận Diện"),
                    get_safe_col_name("Hình Mặt Tiền"),
                    get_safe_col_name("Ảnh Public (VD: 1,3,5)"),
                    get_safe_col_name("Ảnh Hẻm Public (VD: 1,2)")
                }
                for i in range(1, 6):
                    image_fields_to_skip.add(get_safe_col_name(f"Sơ đồ thửa đất {i}"))
                for i in range(1, 11):
                    image_fields_to_skip.add(get_safe_col_name(f"Hình Hẻm {i}"))
                for i in range(1, 26):
                    image_fields_to_skip.add(get_safe_col_name(f"Ảnh {i}"))
                
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

# ==================================================
# API ENDPOINTS
# ==================================================

@app.route('/')
def index():
    """Trả về giao diện web biên tập viên kèm headers chống cache trình duyệt cứng"""
    if os.path.exists("curator.html"):
        with open("curator.html", "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = CURATOR_HTML_CONTENT
    resp = Response(content, mimetype='text/html')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/index.html')
def index_html():
    """Trả về giao diện web client index.html"""
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
    else:
        return "index.html not found", 404
    resp = Response(content, mimetype='text/html')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/api/schema/add-column', methods=['POST'])
def add_schema_column():
    """
    API thêm thuộc tính mới động (Dynamic Schema) cho Pool2.
    Đồng bộ: settings.json, SQLite listings_v2 & listings_custom_v2, Google Sheets và tài liệu markdown.
    """
    data = request.json or {}
    column_name = data.get("column_name", "").strip()
    data_type = data.get("data_type", "TEXT").strip().upper()
    is_public = bool(data.get("is_public", False))
    description = data.get("description", "").strip()
    
    if not column_name:
        return jsonify({"status": "error", "message": "Tên cột không được để trống"}), 400
        
    safe_name = pool_lego.get_safe_col_name(column_name)
    
    # 1. Ghi thông tin mới vào settings.json
    cfg = load_config()
    if "custom_schema_columns" not in cfg:
        cfg["custom_schema_columns"] = []
        
    # Check if exists
    for col in cfg["custom_schema_columns"]:
        if pool_lego.get_safe_col_name(col.get("column_name")) == safe_name:
            return jsonify({"status": "error", "message": f"Cột '{column_name}' đã tồn tại trong cấu hình"}), 400
            
    cfg["custom_schema_columns"].append({
        "column_name": column_name,
        "data_type": data_type,
        "is_public": is_public,
        "description": description
    })
    save_config(cfg)
    
    # Nạp lại cấu hình động trong pool_lego memory
    pool_lego.load_custom_columns()
    
    # 2. ALTER TABLE SQLite listings_v2 & listings_custom_v2
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    cursor = conn.cursor()
    try:
        # listings_v2
        cursor.execute("PRAGMA table_info(listings_v2)")
        v2_cols = [r[1] for r in cursor.fetchall()]
        if safe_name not in v2_cols:
            cursor.execute(f"ALTER TABLE listings_v2 ADD COLUMN `{safe_name}` {data_type}")
            
        # listings_custom_v2 (tất cả là TEXT phục vụ đè)
        cursor.execute("PRAGMA table_info(listings_custom_v2)")
        custom_cols = [r[1] for r in cursor.fetchall()]
        if safe_name not in custom_cols:
            cursor.execute(f"ALTER TABLE listings_custom_v2 ADD COLUMN `{safe_name}` TEXT")
            
        conn.commit()
    except Exception as e_db:
        conn.close()
        return jsonify({"status": "error", "message": f"Lỗi nâng cấp SQLite: {str(e_db)}"}), 500
    conn.close()
    
    # 3. Chèn cột vào 3 Google Sheets
    logs = []
    def log_msg(msg):
        logs.append(msg)
        add_log_message(msg)
        
    pool_lego.add_column_to_google_sheets_v2(
        safe_name=safe_name,
        header_name=column_name,
        is_public=is_public,
        get_google_credentials=get_google_credentials,
        load_config=load_config,
        add_log_message=log_msg
    )
    
    # 4. Ghi nhận mô tả cột vào file tài liệu markdown docs
    pool_lego.append_column_to_docs(
        header_name=column_name,
        safe_name=safe_name,
        is_public=is_public,
        description=description
    )
    
    return jsonify({
        "status": "success", 
        "message": f"Đã thêm thuộc tính '{column_name}' thành công!",
        "logs": logs
    })

@app.route('/api/listings/<tk_id>/upload-image', methods=['POST'])
def upload_manual_image(tk_id):
    """
    API đăng tải hình ảnh thủ công cho căn nhà (Pool2).
    Lưu vào Cloudflare R2 (hoặc Local), cập nhật SQLite listings_images, listings_v2,
    và đồng bộ an toàn lên Google Sheets (cách ly ảnh nhạy cảm).
    """
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Không tìm thấy file ảnh"}), 400
        
    file = request.files['file']
    role = request.form.get("role", "interior").strip()
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "Chưa chọn file ảnh"}), 400
        
    img_bytes = file.read()
    if not img_bytes:
        return jsonify({"status": "error", "message": "File ảnh rỗng"}), 400
        
    cfg = load_config()
    r2_access_key = cfg.get("r2_access_key_id")
    r2_secret_key = cfg.get("r2_secret_access_key")
    r2_bucket = cfg.get("r2_bucket_name")
    account_id = cfg.get("cloudflare_account_id")
    use_r2 = bool(r2_access_key and r2_secret_key and r2_bucket and account_id)
    
    is_diagram = (role in ["diagram", "sodo"])
    if not is_diagram:
        try:
            img_bytes = compress_image(img_bytes)
        except Exception as e_comp:
            add_log_message(f"[⚠️ Warning] Nén ảnh thủ công thất bại: {str(e_comp)}")
            
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    timestamp = int(time.time())
    filename = f"SYS-{tk_id.upper()}_{role}_{timestamp}{ext}"
    
    img_link = ""
    try:
        if use_r2:
            img_link = upload_image_to_r2(img_bytes, filename)
        else:
            local_dir = os.path.join("static", "images", tk_id)
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, filename)
            with open(local_path, "wb") as f:
                f.write(img_bytes)
            img_link = f"/static/images/{tk_id}/{filename}"
    except Exception as e_upload:
        return jsonify({"status": "error", "message": f"Tải ảnh lên cloud thất bại: {str(e_upload)}"}), 500
        
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    cursor = conn.cursor()
    try:
        if LISTINGS_TABLE == "listings":
            role_map = {
                "sodo": "Sơ đồ",
                "diagram": "Sơ đồ",
                "facade": "Mặt tiền",
                "interior": "Nội thất",
                "alley": "Hẻm",
                "cover": "Bìa"
            }
            vi_role = role_map.get(role.lower(), "Nội thất")
            visible = False if vi_role in ["Sơ đồ", "Mặt tiền"] else True
            
            cursor.execute("SELECT curated_config_json, manual_images_json FROM listings WHERE tk_id = ?", (tk_id,))
            row_db = cursor.fetchone()
            curated_json = row_db[0] if row_db else None
            manual_json = row_db[1] if row_db else None
            
            try:
                manual_list = json.loads(manual_json) if manual_json else []
            except Exception:
                manual_list = []
            if not isinstance(manual_list, list):
                manual_list = []
            manual_list.append(img_link)
            
            new_img_obj = {
                "url": img_link,
                "role": vi_role,
                "visible": visible
            }
            
            if not curated_json:
                updated_curated = {"images": [new_img_obj]}
            else:
                try:
                    data_curated = json.loads(curated_json)
                except Exception:
                    data_curated = {"images": []}
                
                if isinstance(data_curated, dict):
                    if "images" not in data_curated or not isinstance(data_curated["images"], list):
                        data_curated["images"] = []
                    data_curated["images"].append(new_img_obj)
                    updated_curated = data_curated
                elif isinstance(data_curated, list):
                    data_curated.append(new_img_obj)
                    updated_curated = data_curated
                else:
                    updated_curated = {"images": [new_img_obj]}
            
            cursor.execute(
                "UPDATE listings SET curated_config_json = ?, manual_images_json = ? WHERE tk_id = ?",
                (json.dumps(updated_curated, ensure_ascii=False), json.dumps(manual_list, ensure_ascii=False), tk_id)
            )
        else:
            max_seq = cursor.execute(
                "SELECT MAX(sequence_index) FROM listings_images WHERE tk_id = ?", 
                (tk_id,)
            ).fetchone()[0]
            next_seq = (max_seq + 1) if (max_seq is not None) else 0
            
            cursor.execute("""
                INSERT INTO listings_images (tk_id, image_url, r2_url, role, sequence_index, edited_by, origin)
                VALUES (?, ?, ?, ?, ?, 'Admin', 'self')
            """, (tk_id, img_link, img_link, role, next_seq))
            
            all_imgs = cursor.execute(
                "SELECT image_url, r2_url, role FROM listings_images WHERE tk_id = ? ORDER BY sequence_index ASC",
                (tk_id,)
            ).fetchall()
            
            curated_list = []
            for img_url, r2_url_val, r_role in all_imgs:
                url_to_use = r2_url_val if r2_url_val else img_url
                curated_list.append({"url": url_to_use, "role": r_role or "interior"})
                
            curated_config_json = json.dumps(curated_list, ensure_ascii=False)
            cursor.execute(
                "UPDATE listings_v2 SET curated_config_json = ? WHERE tk_id = ?",
                (curated_config_json, tk_id)
            )
            
            sys_row = cursor.execute("SELECT System_ID FROM listings_v2 WHERE tk_id = ?", (tk_id,)).fetchone()
            system_id = sys_row[0] if sys_row else None
            
            if role in ["interior", "alley", "cover"] and system_id:
                safe_imgs = []
                for img_url, r2_url_val, r_role in all_imgs:
                    if r_role not in ["facade", "diagram", "deleted", "hidden"]:
                        url_to_use = r2_url_val if r2_url_val else img_url
                        safe_imgs.append({"url": url_to_use, "role": r_role or "interior"})
                
                safe_json = json.dumps(safe_imgs, ensure_ascii=False)
                cursor.execute(
                    "UPDATE listings_custom_v2 SET images_metadata_json = ? WHERE System_ID = ?",
                    (safe_json, system_id)
                )
        conn.commit()
    except Exception as e_db:
        conn.close()
        return jsonify({"status": "error", "message": f"Lỗi ghi nhận CSDL: {str(e_db)}"}), 500
    conn.close()
    
    try:
        execute_publish_listing(tk_id)
    except Exception as e_sheet:
        add_log_message(f"[⚠️ Warning] Đồng bộ Sheets thất bại sau khi upload ảnh: {str(e_sheet)}")
        
    return jsonify({
        "status": "success",
        "message": f"Tải lên hình ảnh vai trò '{role}' thành công!",
        "url": img_link
    })

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """API lấy và cập nhật cấu hình"""
    if request.method == 'POST':
        data = request.json
        cfg = load_config()
        for k in DEFAULT_CONFIG.keys():
            if k in data:
                # Bảo vệ chống ghi đè OpenAI API Key bằng chuỗi trống hoặc placeholder từ UI
                if k == "openai_api_key":
                    new_key = data[k].strip() if isinstance(data[k], str) else ""
                    if new_key and not new_key.startswith("sk-proj-xxxx") and "xxxxxxxx" not in new_key:
                        cfg[k] = new_key
                else:
                    cfg[k] = data[k]
        # Tự động trích xuất json_ui_fields từ json_ui_filters
        if "json_ui_filters" in data:
            filters = data["json_ui_filters"] or []
            fields = []
            for f in filters:
                if isinstance(f, dict) and f.get("field"):
                    fields.append(f["field"])
            cfg["json_ui_fields"] = fields
        save_config(cfg)
        return jsonify({"status": "success", "config": cfg})
    else:
        cfg = load_config()
        client_cfg = dict(cfg)
        if "openai_api_key" in client_cfg and client_cfg["openai_api_key"]:
            key = client_cfg["openai_api_key"]
            if len(key) > 12:
                client_cfg["openai_api_key"] = f"{key[:8]}...xxxx...{key[-4:]}"
        return jsonify({"status": "success", "config": client_cfg})

# ==================================================
# BACKEND AUTO-CURATION & FALLBACK GENERATOR (US-040)
# ==================================================
def generate_fallback_content_python(d):
    so_nha = safe_str(d.get("Ngo_So_nha"))
    duong = safe_str(d.get("Duong"))
    dt = safe_str(d.get("DT_Thuc_te"))
    tang = safe_str(d.get("So_Tang"))
    mat = safe_str(d.get("Mat_Tien"))
    dai = safe_str(d.get("Chieu_dai"))
    gia = safe_str(d.get("Gia_chao"))
    
    # Kích thước
    kich_thuoc = f"{mat}x{dai}" if mat and dai else ""
    
    # Định dạng giá
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
    desc = d.get("Mo_ta_chi_tiet", "") or d.get("Noi_dung_chinh", "")
    return {
        "tieu_de_public": title,
        "mo_ta_public": desc,
        "phuong_cu": ""
    }

def generate_ai_curation_for_listing_backend(d, cfg):
    """Gọi OpenAI gpt-4o-mini để tự động sinh Tiêu đề, Mô tả và tìm Phường cũ cho 1 căn"""
    api_key = cfg.get("openai_api_key", "").strip()
    if not api_key:
        add_log_message("[⚠️ AUTO-AI] Chưa cấu hình OpenAI API Key. Bỏ qua gọi AI và dùng fallback format.")
        return generate_fallback_content_python(d)
        
    api_base = cfg.get("openai_api_base", "https://api.openai.com/v1").strip().rstrip('/')
    
    # Tải prompt động từ Google Doc nếu cấu hình
    doc_id = cfg.get("prompt_google_doc_id", "")
    doc_prompt = None
    if doc_id:
        doc_prompt = fetch_google_doc_content(doc_id)
        
    if doc_prompt:
        system_prompt = doc_prompt
    else:
        system_prompt = cfg.get("openai_system_prompt", DEFAULT_CONFIG["openai_system_prompt"])
        
    # Nối chỉ thị JSON để đảm bảo AI trả về cấu trúc chính xác
    json_suffix = (
        "\n\n🚨 BẮT BUỘC ĐỊNH DẠNG ĐẦU RA (OUTPUT FORMAT):\n"
        "Bạn PHẢI trả về kết quả dưới dạng JSON object duy nhất có cấu trúc chính xác sau, không chứa ký tự markdown (như ```json) hay văn bản nào bên ngoài:\n"
        "{\n"
        "  \"tieuDe\": \"Tiêu đề public viết theo hướng dẫn của Bước 3\",\n"
        "  \"moTa\": \"Mô tả chi tiết viết theo hướng dẫn của Bước 3\",\n"
        "  \"phuongCu\": \"Tên phường cũ (nếu có sáp nhập phường, hoặc để trống)\"\n"
        "}"
    )
    if "tieuDe" not in system_prompt or "moTa" not in system_prompt:
        system_prompt += json_suffix
    
    # 1. Tính toán Tiền tố địa chỉ (Mặt tiền / HXH)
    so_nha = safe_str(d.get("Ngo_So_nha"))
    duong_truoc_nha = safe_str(d.get("Duong_truoc_nha_m"))
    phan_loai_hem = safe_str(d.get("Phan_loai_Hem")).lower()
    
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
        
    # 2. Xử lý định dạng Giá (tương thích Thiên Khôi)
    gia_chao = d.get("Gia_chao", "")
    try:
        gia_ty = float(gia_chao)
        if gia_ty > 100:
            gia_ty = gia_ty / 1000
        gia_format = f"{gia_ty} tỷ" if gia_ty > 0 else ""
    except ValueError:
        gia_format = gia_chao
        
    # 3. Tạo User Prompt
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
            add_log_message(f"[🤖 AUTO-AI] Nhận kết quả từ OpenAI: {ai_message}")
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
            add_log_message(f"[❌ AUTO-AI ERROR] OpenAI API Error: {err_msg}. Dùng fallback format.")
            return generate_fallback_content_python(d)
    except Exception as e:
        add_log_message(f"[❌ AUTO-AI ERROR] Lỗi khi gọi OpenAI API: {str(e)}. Dùng fallback format.")
        return generate_fallback_content_python(d)

@app.route('/api/ai/generate', methods=['POST'])
def ai_generate():
    """Gọi OpenAI gpt-4o-mini để sinh Tiêu đề, Mô tả và tìm Phường cũ"""
    try:
        data = request.json or {}
        cfg = load_config()
        
        api_key = cfg.get("openai_api_key", "").strip()
        if not api_key:
            return jsonify({
                "status": "error",
                "message": "Chưa cấu hình OpenAI API Key. Vui lòng vào mục 'Cấu hình Hệ thống & API' để thiết lập."
            }), 400
            
        # Tải prompt động từ Google Doc nếu cấu hình
        doc_id = cfg.get("prompt_google_doc_id", "")
        doc_prompt = None
        if doc_id:
            doc_prompt = fetch_google_doc_content(doc_id)
            
        if doc_prompt:
            system_prompt = doc_prompt
        else:
            system_prompt = cfg.get("openai_system_prompt", DEFAULT_CONFIG["openai_system_prompt"])
            
        # Nối chỉ thị JSON để đảm bảo AI trả về cấu trúc chính xác
        json_suffix = (
            "\n\n🚨 BẮT BUỘC ĐỊNH DẠNG ĐẦU RA (OUTPUT FORMAT):\n"
            "Bạn PHẢI trả về kết quả dưới dạng JSON object duy nhất có cấu trúc chính xác sau, không chứa ký tự markdown (như ```json) hay văn bản nào bên ngoài:\n"
            "{\n"
            "  \"tieuDe\": \"Tiêu đề public viết theo hướng dẫn của Bước 3\",\n"
            "  \"moTa\": \"Mô tả chi tiết viết theo hướng dẫn của Bước 3\",\n"
            "  \"phuongCu\": \"Tên phường cũ (nếu có sáp nhập phường, hoặc để trống)\"\n"
            "}"
        )
        if "tieuDe" not in system_prompt or "moTa" not in system_prompt:
            system_prompt += json_suffix
        
        # 1. Tính toán Tiền tố địa chỉ (Mặt tiền / HXH)
        so_nha = safe_str(data.get("soNha"))
        duong_truoc_nha = safe_str(data.get("duongTruocNha"))
        phan_loai_hem = safe_str(data.get("phanLoaiHem")).lower()
        
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
            
        # 2. Xử lý định dạng Giá (tương thích Thiên Khôi)
        gia_chao = data.get("giaChao", "")
        try:
            gia_ty = float(gia_chao)
            if gia_ty > 100:
                gia_ty = gia_ty / 1000
            gia_format = f"{gia_ty} tỷ" if gia_ty > 0 else ""
        except ValueError:
            gia_format = gia_chao
            
        # 3. Tạo User Prompt
        user_prompt = (
            "THÔNG TIN CĂN NHÀ:\n"
            f"- Địa chỉ: {data.get('soNha', '')} {data.get('duong', '')}, Phường {data.get('phuong', '')}, Quận {data.get('quan', '')}\n"
            f"- Nội dung chính gốc (chứa kích thước ở đầu): {data.get('noiDungChinh', '')}\n"
            f"- DT Thực tế: {data.get('dtThucTe', '')}m2 | DT Trên sổ: {data.get('dtTrenSo', '')}m2\n"
            f"- Chiều ngang (mặt tiền): {data.get('matTien', '')}m\n"
            f"- Hướng: {data.get('huong', '')}\n"
            f"- Kết cấu: {data.get('soTang', '')} tầng, {data.get('soPhongNgu', '')} PN, {data.get('soToilet', '')} WC\n"
            f"- Hẻm: {data.get('phanLoaiHem', '')} (Rộng: {data.get('duongTruocNha', '')}m)\n"
            f"- Giá: {gia_format}\n"
            f"- Phân loại / Tag USP: {data.get('phanLoai', '')}\n"
            f"- Điểm nổi bật của căn nhà (nguồn USP chính): {data.get('moTaChiTiet', '')}\n\n"
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
        
        api_base = cfg.get("openai_api_base", "https://api.openai.com/v1").strip().rstrip('/')
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{api_base}/chat/completions", json=payload, headers=headers, timeout=30)
        res_json = response.json()
        
        if response.status_code == 200:
            ai_message = res_json["choices"][0]["message"]["content"]
            add_log_message(f"[🤖 AI] Nhận kết quả từ OpenAI: {ai_message}")
            ai_data = json.loads(ai_message)
            
            # Lấy key linh hoạt chống lỗi OpenAI tự đổi tên hoặc định dạng key
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
            
            return jsonify({
                "status": "success",
                "tieu_de_public": tieu_de_clean,
                "mo_ta_public": mo_ta_raw,
                "phuong_cu": phuong_cu_raw
            })
        else:
            err_msg = res_json.get("error", {}).get("message", "Lỗi không xác định từ OpenAI.")
            return jsonify({"status": "error", "message": f"OpenAI API Error: {err_msg}"}), response.status_code
            
    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi gọi OpenAI API: {str(e)}"}), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """API lấy logs thời gian thực cho giao diện"""
    with LOGS_LOCK:
        return jsonify({"logs": LOGS_BUFFER})

@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """API xóa sạch logs buffer"""
    with LOGS_LOCK:
        LOGS_BUFFER.clear()
    return jsonify({"status": "success"})

@app.route('/api/cookie/save', methods=['POST'])
def save_cookie_endpoint():
    """API lưu Cookie đăng nhập mới từ frontend và lập tức ngắt luồng cào cũ"""
    data = request.json or {}
    cookie_payload = data.get("cookie") or data.get("crawler_cookie")
    if not cookie_payload:
        return jsonify({"status": "error", "message": "Thiếu dữ liệu cookie."}), 400
        
    try:
        # Ngắt tiến trình cào cũ ngay lập tức bằng cách kích hoạt cờ dừng
        fetcher.STOP_REQUESTED = True
        
        # Ghi cookie mới vào file COOKIE_FILE
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            f.write(cookie_payload.strip())
            
        # Xóa sạch logs cũ tránh nhảy báo động hết hạn lặp lại ở UI
        with LOGS_LOCK:
            LOGS_BUFFER.clear()
            
        add_log_message("[🔑] ĐÃ LƯU COOKIE THIÊN KHÔI MỚI VÀ DỌN SẠCH LOGS HẾT HẠN CŨ!")
        return jsonify({"status": "success", "message": "Đã lưu cookie thành công!"})
    except Exception as e:
        add_log_message(f"[❌ LỖI] Không thể ghi file cookie: {str(e)}")
        return jsonify({"status": "error", "message": f"Không thể ghi file cookie: {str(e)}"}), 500

@app.route('/api/crawl', methods=['POST'])
def trigger_crawl():
    """Kích hoạt tiến trình cào tin ngầm hoặc lưu Cookie"""
    global ACTIVE_CRAWLER_THREAD
    data = request.json or {}
    url = data.get("url")
    district = data.get("district")
    limit = data.get("limit")
    start_page = data.get("start_page")
    
    if not url:
        return jsonify({"status": "error", "message": "Thiếu tham số URL danh sách quận."}), 400
        
    # XỬ LÝ LƯU COOKIE TỪ FRONTEND
    if url == 'MOCK_SAVE_ONLY':
        cookie_payload = data.get("cookie")
        if cookie_payload:
            try:
                # Dừng luồng cũ ngay lập tức do cookie đã thay đổi
                fetcher.STOP_REQUESTED = True
                with open(COOKIE_FILE, "w", encoding="utf-8") as f:
                    f.write(cookie_payload.strip())
                # Xóa sạch logs cũ tránh nhảy báo động hết hạn lặp lại ở UI
                with LOGS_LOCK:
                    LOGS_BUFFER.clear()
                add_log_message("[🔑] ĐÃ LƯU COOKIE THIÊN KHÔI MỚI VÀ DỌN SẠCH LOGS HẾT HẠN CŨ!")
                return jsonify({"status": "success", "message": "Đã lưu cookie và gửi lệnh dừng tiến trình cũ thành công!"})
            except Exception as e:
                add_log_message(f"[❌ LỖI] Không thể ghi file cookie: {str(e)}")
                return jsonify({"status": "error", "message": f"Không thể ghi file cookie: {str(e)}"}), 500
        return jsonify({"status": "error", "message": "Thiếu dữ liệu cookie."}), 400
        
    # KIỂM TRA VÀ NGẮT TIẾN TRÌNH CŨ NẾU ĐANG CHẠY
    with ACTIVE_CRAWLER_LOCK:
        if ACTIVE_CRAWLER_THREAD and ACTIVE_CRAWLER_THREAD.is_alive():
            add_log_message("[⚠️] Phát hiện tiến trình cào cũ đang chạy. Đang gửi lệnh dừng khẩn cấp...")
            fetcher.STOP_REQUESTED = True
            
            # Đợi luồng cũ dừng tối đa 3 giây
            stopped_successfully = False
            for _ in range(30):
                if not ACTIVE_CRAWLER_THREAD.is_alive():
                    stopped_successfully = True
                    break
                time.sleep(0.1)
                
            if not stopped_successfully:
                add_log_message("[❌] Luồng cũ vẫn chưa dừng hoàn toàn. Vui lòng nhấn nút dán Cookie hoặc tải lại Curator sau 5 giây.")
                return jsonify({
                    "status": "error", 
                    "message": "Tiến trình cào cũ đang chạy và đang được ngắt. Vui lòng đợi 5 giây rồi nhấn Bắt đầu cào lại."
                }), 400
            else:
                add_log_message("[✅] Đã ngắt tiến trình cào cũ thành công. Bắt đầu tiến trình mới...")
                
    # Lấy Cookie từ file cache
    cookie = ""
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
        except Exception:
            pass
            
    # Reset cờ STOP_REQUESTED về False và khởi chạy luồng cào mới
    fetcher.STOP_REQUESTED = False
    
    t = threading.Thread(target=run_crawler_thread, args=(url, cookie, district, limit, start_page))
    t.daemon = True
    t.start()
    
    with ACTIVE_CRAWLER_LOCK:
        ACTIVE_CRAWLER_THREAD = t
        
    return jsonify({"status": "success", "message": "Đã khởi động tiến trình cào ngầm mới!"})

@app.route('/api/migrate', methods=['POST'])
def trigger_migration():
    """Kích hoạt tiến trình tải ảnh up Drive ngầm"""
    global IS_MIGRATION_ACTIVE
    data = request.json or {}
    limit = data.get("limit")
    
    with MIGRATION_LOCK:
        if IS_MIGRATION_ACTIVE:
            return jsonify({"status": "warning", "message": "Tiến trình di cư hình ảnh hiện đang chạy ngầm rồi!"}), 409
        IS_MIGRATION_ACTIVE = True
    
    cookie = ""
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
        except Exception:
            pass
            
    t = threading.Thread(target=run_auto_migration_wrapper_with_limit, args=(limit, cookie))
    t.daemon = True
    t.start()
    
    return jsonify({"status": "success", "message": "Đã bắt đầu di cư hình ảnh lên Drive chạy ngầm!"})

@app.route('/api/crawl/sessions', methods=['GET'])
def get_crawl_sessions():
    """Lấy danh sách lịch sử các phiên cào tin và tổng số thống kê tổng thể"""
    if not os.path.exists(DB_FILE):
        return jsonify({
            "sessions": [],
            "totals": {
                "total_sessions": 0,
                "total_crawled": 0,
                "total_duration": 0,
                "overall_avg_speed": "N/A"
            }
        })
        
    try:
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Kiểm tra sự tồn tại của bảng crawl_sessions
        table_exists = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='crawl_sessions'"
        ).fetchone()
        
        if not table_exists:
            conn.close()
            return jsonify({
                "sessions": [],
                "totals": {
                    "total_sessions": 0,
                    "total_crawled": 0,
                    "total_duration": 0,
                    "overall_avg_speed": "N/A"
                }
            })
            
        rows = cursor.execute("SELECT * FROM crawl_sessions ORDER BY id DESC").fetchall()
        conn.close()
        
        sessions = [dict(r) for r in rows]
        
        # Tính toán các chỉ số tổng cộng
        total_sessions = len(sessions)
        total_crawled = sum(s["crawled_count"] for s in sessions if s["crawled_count"] is not None)
        total_duration = sum(s["duration"] for s in sessions if s["duration"] is not None)
        
        overall_avg_speed = "N/A"
        if total_crawled > 0:
            overall_avg_speed = f"{total_duration / total_crawled:.1f} giây/căn"
            
        return jsonify({
            "sessions": sessions,
            "totals": {
                "total_sessions": total_sessions,
                "total_crawled": total_crawled,
                "total_duration": total_duration,
                "overall_avg_speed": overall_avg_speed
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Không thể lấy lịch sử phiên cào: {str(e)}"}), 500

@app.route('/api/listings/clear', methods=['POST'])
def clear_all_listings():
    """Xóa toàn bộ listings khỏi SQLite và dọn dẹp thư mục ảnh cục bộ"""
    if not os.path.exists(DB_FILE):
        return jsonify({"status": "success", "message": "Database đã trống."})
        
    try:
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {LISTINGS_TABLE}")
        # Reset autoincrement
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{LISTINGS_TABLE}'")
        conn.commit()
        conn.close()
        
        # Dọn dẹp thư mục ảnh static/images
        images_dir = os.path.join("static", "images")
        if os.path.exists(images_dir):
            import shutil
            for filename in os.listdir(images_dir):
                filepath = os.path.join(images_dir, filename)
                try:
                    if os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                    else:
                        os.unlink(filepath)
                except Exception:
                    pass
                    
        add_log_message("[🧹] ĐÃ XÓA SẠCH TOÀN BỘ DỮ LIỆU CRAWL VÀ HÌNH ẢNH CỤC BỘ THÀNH CÔNG!")
        return jsonify({"status": "success", "message": "Đã xóa sạch toàn bộ dữ liệu cào cũ và hình ảnh thành công!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Không thể xóa dữ liệu: {str(e)}"}), 500

@app.route('/api/listings', methods=['GET'])
def get_listings():
    """API lấy danh sách các căn từ SQLite với đầy đủ metadata"""
    if not os.path.exists(DB_FILE):
        return jsonify({"listings": []})
        
    status_filter = request.args.get("status")
    search_q = request.args.get("search")
    
    quan_filter = request.args.get("quan")
    duong_filter = request.args.get("duong")
    so_nha_filter = request.args.get("so_nha")
    
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    # Trả về kết quả dạng Dict
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Lấy danh sách cột thực tế của bảng listings để chống lỗi lệch cột/font chữ gạch dưới
    try:
        cursor.execute(f"PRAGMA table_info({LISTINGS_TABLE})")
        db_cols = [r[1] for r in cursor.fetchall()]
    except Exception:
        db_cols = []
        
    quan_col = next((c for c in db_cols if c in ["Quan", "Qu_n"]), "Quan")
    duong_col = next((c for c in db_cols if c in ["streetName", "Duong", "___ng"]), "Duong")
    so_nha_col = next((c for c in db_cols if c in ["Ngo_So_nha", "Ng__S__nh_"]), "Ngo_So_nha")
    
    t_prefix = "listings_v2." if LISTINGS_TABLE == "listings_v2" else ""
    if LISTINGS_TABLE == "listings_v2":
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
        """
    else:
        sql = f"SELECT * FROM {LISTINGS_TABLE}"

    conditions = []
    params = []
    
    if status_filter:
        if status_filter == "crawl_failed":
            conditions.append(f"{t_prefix}status LIKE 'crawl_failed:%'")
        elif status_filter == "missing_raw_json":
            if "raw_json_full" in db_cols:
                conditions.append(f"({t_prefix}raw_json_full IS NULL OR {t_prefix}raw_json_full = '')")
            else:
                conditions.append("1=0")
        else:
            conditions.append(f"{t_prefix}status = ?")
            params.append(status_filter)
        
    if search_q:
        # Tự động trích xuất UUID hoặc mã hàng số từ URL nếu người dùng dán cả link
        uuid_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', search_q, re.I)
        detail_match = re.search(r'/Detail/(\d+)', search_q, re.I)
        
        extracted_id = None
        if uuid_match:
            extracted_id = uuid_match.group(0)
        elif detail_match:
            extracted_id = detail_match.group(1)
            
        if extracted_id:
            conditions.append(f"({t_prefix}tk_id = ? OR {t_prefix}tk_id LIKE ? OR {t_prefix}Ma_Hang LIKE ? OR {t_prefix}`{quan_col}` LIKE ? OR {t_prefix}`{duong_col}` LIKE ? OR {t_prefix}`{so_nha_col}` LIKE ?)")
            search_like = f"%{search_q}%"
            params.extend([extracted_id, search_like, search_like, search_like, search_like, search_like])
        else:
            conditions.append(f"({t_prefix}tk_id LIKE ? OR {t_prefix}Ma_Hang LIKE ? OR {t_prefix}`{quan_col}` LIKE ? OR {t_prefix}`{duong_col}` LIKE ? OR {t_prefix}`{so_nha_col}` LIKE ?)")
            search_like = f"%{search_q}%"
            params.extend([search_like, search_like, search_like, search_like, search_like])
        
    if quan_filter:
        conditions.append(f"{t_prefix}`{quan_col}` LIKE ?")
        params.append(f"%{quan_filter}%")
        
    if duong_filter:
        conditions.append(f"{t_prefix}`{duong_col}` LIKE ?")
        params.append(f"%{duong_filter}%")
        
    if so_nha_filter:
        conditions.append(f"{t_prefix}`{so_nha_col}` LIKE ?")
        params.append(f"%{so_nha_filter}%")
        
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
        
    # Mặc định sắp xếp mới nhất lên trước
    if LISTINGS_TABLE == "listings_v2":
        sql += " ORDER BY listings_v2.rowid DESC"
    else:
        sql += " ORDER BY rowid DESC"
    
    rows = cursor.execute(sql, params).fetchall()
    conn.close()
    
    listings = [normalize_listing_for_client(r) for r in rows]
        
    # Tính toán số lượng căn theo từng trạng thái (status) toàn cục
    counts = {"raw_text": 0, "raw_complete": 0, "published": 0, "crawl_failed": 0, "missing_raw_json": 0}
    if os.path.exists(DB_FILE):
        try:
            conn_count = sqlite3.connect(DB_FILE, timeout=30.0)
            cursor_count = conn_count.cursor()
            for s in ["raw_text", "raw_complete", "published"]:
                c = cursor_count.execute(f"SELECT COUNT(*) FROM {LISTINGS_TABLE} WHERE status = ?", (s,)).fetchone()[0]
                counts[s] = c
            # Thêm đếm số lượng căn lỗi cào
            c_failed = cursor_count.execute(f"SELECT COUNT(*) FROM {LISTINGS_TABLE} WHERE status LIKE 'crawl_failed:%'").fetchone()[0]
            counts["crawl_failed"] = c_failed
            
            # Đếm số lượng căn thiếu raw_json_full
            cursor_count.execute(f"PRAGMA table_info({LISTINGS_TABLE})")
            cols = [r[1] for r in cursor_count.fetchall()]
            if "raw_json_full" in cols:
                c_missing = cursor_count.execute(f"SELECT COUNT(*) FROM {LISTINGS_TABLE} WHERE raw_json_full IS NULL OR raw_json_full = ''").fetchone()[0]
                counts["missing_raw_json"] = c_missing
            else:
                counts["missing_raw_json"] = 0
                
            conn_count.close()
        except Exception:
            pass
            
    return jsonify({
        "listings": listings,
        "status_counts": counts
    })

@app.route('/api/listings/check-exist', methods=['POST'])
def check_listings_exist():
    """Kiểm tra danh sách tk_id xem có tồn tại trong database local không (tối ưu hóa hiệu năng)"""
    data = request.json or {}
    tk_ids = data.get("tk_ids", [])
    if not tk_ids:
        return jsonify({"exists": []})
        
    if not os.path.exists(DB_FILE):
        return jsonify({"exists": []})
        
    # Lọc bỏ giá trị không hợp lệ
    tk_ids = [str(x).strip() for x in tk_ids if x]
    if not tk_ids:
        return jsonify({"exists": []})
        
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        # Tạo câu truy vấn IN với tham số an toàn
        placeholders = ",".join(["?"] * len(tk_ids))
        sql = f"SELECT tk_id FROM {LISTINGS_TABLE} WHERE tk_id IN ({placeholders})"
        rows = cursor.execute(sql, tk_ids).fetchall()
        conn.close()
        
        exists_ids = [r[0] for r in rows if r[0]]
        return jsonify({"exists": exists_ids})
    except Exception as e:
        add_log_message(f"[⚠️ WARNING] Lỗi kiểm tra tồn tại căn: {str(e)}")
        return jsonify({"exists": [], "error": str(e)}), 500

@app.route('/api/listings/<tk_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_listing_detail(tk_id):
    """Lấy chi tiết hoặc cập nhật cấu hình biên tập cho 1 căn"""
    if not os.path.exists(DB_FILE):
        return jsonify({"status": "error", "message": "Database không tồn tại"}), 404
        
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if LISTINGS_TABLE == "listings_v2":
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
        row = cursor.execute(f"SELECT * FROM {LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
    
    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "Mã căn không tồn tại"}), 404
        
    if request.method == 'DELETE':
        cursor.execute(f"DELETE FROM {LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,))
        conn.commit()
        conn.close()
        
        # Xóa folder ảnh cục bộ
        local_dir = os.path.join("static", "images", tk_id)
        if os.path.exists(local_dir):
            import shutil
            try:
                shutil.rmtree(local_dir)
            except Exception:
                pass
                
        add_log_message(f"[🧹] Đã xóa thành công căn {tk_id} khỏi database SQLite cục bộ!")
        return jsonify({"status": "success", "message": f"Đã xóa thành công căn {tk_id}"})
        
    if request.method == 'PUT':
        # CẬP NHẬT CẤU HÌNH BIÊN TẬP
        data = request.json
        curated_config = data.get("curated_config")
        
        # Cập nhật cột curated_config_json trước
        cursor.execute(
            f"UPDATE {LISTINGS_TABLE} SET curated_config_json = ? WHERE tk_id = ?",
            (json.dumps(curated_config, ensure_ascii=False), tk_id)
        )

        # Cập nhật manual_images_json cho Pool1 (đồng bộ nếu có ảnh thủ công bị xóa khỏi curated_config)
        if LISTINGS_TABLE == "listings" and curated_config and isinstance(curated_config, dict):
            row_db = cursor.execute("SELECT manual_images_json FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
            current_manual_json = row_db[0] if row_db else None
            try:
                current_manual = json.loads(current_manual_json) if current_manual_json else []
            except Exception:
                current_manual = []
                
            if current_manual:
                curated_urls = {img.get("url") for img in curated_config.get("images", []) if isinstance(img, dict) and img.get("url")}
                updated_manual = [url for url in current_manual if url in curated_urls]
                cursor.execute(
                    "UPDATE listings SET manual_images_json = ? WHERE tk_id = ?",
                    (json.dumps(updated_manual, ensure_ascii=False), tk_id)
                )
        
        # Cập nhật các trường chỉnh sửa của admin vào các cột tương ứng
        fields_to_update = {
            "Tiêu đề Public": trim_tieu_de_bds(data.get("tieu_de_public")),
            "Mô tả Public": data.get("mo_ta_public"),
            "Giá Public": data.get("gia_public"),
            "Mã Khang Ngô (ID)": data.get("ma_khang_ngo"),
            "Phân loại Hẻm": data.get("phan_loai_hem"),
            "Đường trước nhà (m)": data.get("duong_truoc_nha"),
            "Mặt Tiền": data.get("mat_tien"),
            "Chiều dài": data.get("chieu_dai"),
            "Tình trạng nhà": data.get("tinh_trang_nha"),
            "Số phòng ngủ": data.get("so_phong_ngu"),
            "Số nhà vệ sinh": data.get("so_nha_ve_sinh"),
            "Đánh giá (Admin)": data.get("danh_gia"),
            "Ngủ trệt (Admin)": data.get("ngu_tret"),
            "CHDV (Admin)": data.get("chdv"),
            "Phường cũ (AI)": data.get("phuong_cu_ai"),
            # Thực tế địa chỉ chỉnh sửa
            "Ngõ/Số nhà": data.get("ngo_so_nha"),
            "Quận": data.get("quan"),
            "Phường": data.get("phuong"),
            "Đường": data.get("duong"),
            # Link ảnh chi tiết đã chọn nhãn
            "Hình Nhận Diện": data.get("hinh_nhan_dien"),
            "Hình Mặt Tiền": data.get("hinh_mat_tien"),
            "Sơ đồ thửa đất 1": data.get("so_do_1"),
            "Sơ đồ thửa đất 2": data.get("so_do_2"),
            "Sơ đồ thửa đất 3": data.get("so_do_3"),
            "Sơ đồ thửa đất 4": data.get("so_do_4"),
            "Sơ đồ thửa đất 5": data.get("so_do_5"),
            "Ảnh Public (VD: 1,3,5)": data.get("anh_public_vd_1_3_5"),
            "Ảnh Hẻm Public (VD: 1,2)": data.get("anh_hem_public_vd_1_2")
        }
        
        # Cập nhật các cột Hẻm 1-10
        hem_imgs = data.get("hem_imgs", [])
        for i in range(10):
            col_name = f"Hình Hẻm {i+1}"
            fields_to_update[col_name] = hem_imgs[i] if i < len(hem_imgs) else ""
            
        # Cập nhật các cột Ảnh 1-25
        public_imgs = data.get("public_imgs", [])
        for i in range(25):
            col_name = f"Ảnh {i+1}"
            fields_to_update[col_name] = public_imgs[i] if i < len(public_imgs) else ""
            
        # Lấy danh sách cột thực tế của bảng SQLite mục tiêu để lọc cột động
        cursor.execute(f"PRAGMA table_info({LISTINGS_TABLE})")
        db_cols = {row[1] for row in cursor.fetchall()}

        # Xây dựng câu lệnh Update SQL động
        update_cols = []
        update_vals = []
        for key, val in fields_to_update.items():
            safe_col = get_safe_col_name(key)
            if safe_col in db_cols:
                # TRÁNH CẬP NHẬT CÁC CỘT PHẲNG HÌNH ẢNH Ở POOL1 (LISTINGS TABLE)
                if LISTINGS_TABLE == "listings":
                    is_flat_image = (
                        key in ["Hình Nhận Diện", "Hình Mặt Tiền", "Ảnh Public (VD: 1,3,5)", "Ảnh Hẻm Public (VD: 1,2)"] or
                        key.startswith("Hình Hẻm ") or
                        key.startswith("Ảnh ")
                    )
                    if is_flat_image:
                        continue
                update_cols.append(f"`{safe_col}` = ?")
                update_vals.append(str(val) if val is not None else "")
            
        if update_cols:
            update_vals.append(tk_id)
            update_sql = f"UPDATE {LISTINGS_TABLE} SET {', '.join(update_cols)} WHERE tk_id = ?"
            cursor.execute(update_sql, update_vals)
        
        # Nếu đang ở chế độ Pool2, đồng bộ cập nhật vào bảng listings_custom_v2
        if LISTINGS_TABLE == "listings_v2":
            try:
                row_v2 = cursor.execute("SELECT * FROM listings_v2 WHERE tk_id = ?", (tk_id,)).fetchone()
                if row_v2:
                    d_v2 = dict(row_v2)
                    system_id = d_v2.get("System_ID")
                    if system_id:
                        # Kiểm tra xem đã tồn tại System_ID trong listings_custom_v2 chưa
                        custom_exists = cursor.execute(
                            "SELECT 1 FROM listings_custom_v2 WHERE System_ID = ?", (system_id,)
                        ).fetchone()
                        
                        # Trích xuất danh sách ảnh an toàn từ curated_config
                        images_metadata = []
                        if curated_config and isinstance(curated_config, dict):
                            images_list = curated_config.get("images", [])
                            safe_roles = ["interior", "alley", "cover", "interior_public", "alley_public"]
                            images_metadata = [img for img in images_list if img.get("role") in safe_roles or not img.get("role")]
                        
                        # Điền thông tin vào listings_custom_v2
                        custom_data = {
                            "System_ID": system_id,
                            "Ma_Khang_Ngo": data.get("ma_khang_ngo") or d_v2.get("Ma_Khang_Ngo_ID") or "",
                            "Gia_Public": data.get("gia_public") or d_v2.get("Gia_Public") or "",
                            "Tieu_De_Public": trim_tieu_de_bds(data.get("tieu_de_public")) or d_v2.get("Tieu_de_Public") or "",
                            "Mo_ta_Public": data.get("mo_ta_public") or d_v2.get("Mo_ta_Public") or "",
                            "Note_Noi_Bo": data.get("note_noi_bo") or d_v2.get("Note_Noi_Bo") or "",
                            "Trang_Thai_Giao_Dich": data.get("tinh_trang_nha") or d_v2.get("Tinh_trang_nha") or "",
                            "Ngu_Tret": data.get("ngu_tret") or d_v2.get("Ngu_tret_Admin") or "",
                            "CHDV": data.get("chdv") or d_v2.get("CHDV_Admin") or "",
                            "Trang_Thai_KN": data.get("danh_gia") or d_v2.get("Danh_gia_Admin") or "",
                            "images_metadata_json": json.dumps(images_metadata),
                            "Dia_Chi_That": d_v2.get("Dia_Chi_That") or "",
                            "So_Nha": data.get("ngo_so_nha") or d_v2.get("Ngo_So_nha") or "",
                            "Ten_Duong": data.get("duong") or d_v2.get("Duong") or "",
                            "Quan": data.get("quan") or d_v2.get("Quan") or "",
                            "Phuong": data.get("phuong") or d_v2.get("Phuong") or "",
                            "Duong": data.get("duong") or d_v2.get("Duong") or "",
                            "Ngo_So_nha": data.get("ngo_so_nha") or d_v2.get("Ngo_So_nha") or "",
                            "bedrooms": data.get("so_phong_ngu") or d_v2.get("bedrooms") or d_v2.get("So_phong_ngu") or "",
                            "restrooms": data.get("so_nha_ve_sinh") or d_v2.get("restrooms") or d_v2.get("So_nha_ve_sinh") or "",
                            "minimumRoadWidth": data.get("duong_truoc_nha") or d_v2.get("minimumRoadWidth") or d_v2.get("Duong_truoc_nha_m") or "",
                            "Noi_dung_chinh": d_v2.get("Noi_dung_chinh") or "",
                            "Mo_ta_chi_tiet": d_v2.get("Mo_ta_chi_tiet") or "",
                            "Gia_chao": d_v2.get("Gia_chao") or "",
                            "DT_Thuc_te": d_v2.get("DT_Thuc_te") or "",
                            "DT_Tren_so": d_v2.get("DT_Tren_so") or "",
                            "So_Tang": d_v2.get("So_Tang") or "",
                            "Mat_Tien": data.get("mat_tien") or d_v2.get("Mat_Tien") or "",
                            "Chieu_dai": data.get("chieu_dai") or d_v2.get("Chieu_dai") or "",
                            "Huong": d_v2.get("Huong") or "",
                            "Criteria_Duong_truoc_nha": d_v2.get("Criteria_Duong_truoc_nha") or "",
                            "Criteria_Noi_that": d_v2.get("Criteria_Noi_that") or "",
                            "Criteria_Thang_may": d_v2.get("Criteria_Thang_may") or "",
                            "Criteria_Loai_ngo": d_v2.get("Criteria_Loai_ngo") or "",
                            "Criteria_Khoang_cach_bai_do_xe": d_v2.get("Criteria_Khoang_cach_bai_do_xe") or "",
                            "Criteria_Kinh_doanh_Dong_tien": d_v2.get("Criteria_Kinh_doanh_Dong_tien") or "",
                            "Criteria_Huong_nha": d_v2.get("Criteria_Huong_nha") or "",
                            "Criteria_Khoang_cach_duong_oto": d_v2.get("Criteria_Khoang_cach_duong_oto") or "",
                        }
                        
                        # Lấy danh sách cột thực tế của listings_custom_v2 đề phòng lệch schema
                        cursor.execute("PRAGMA table_info(listings_custom_v2)")
                        custom_db_cols = [r[1] for r in cursor.fetchall()]
                        
                        # Lọc bỏ cột không tồn tại
                        valid_custom_data = {k: v for k, v in custom_data.items() if k in custom_db_cols}
                        
                        if custom_exists:
                            # UPDATE
                            update_pairs = []
                            update_custom_vals = []
                            for col_k, col_v in valid_custom_data.items():
                                if col_k != "System_ID":
                                    update_pairs.append(f"`{col_k}` = ?")
                                    update_custom_vals.append(str(col_v) if col_v is not None else "")
                            update_custom_vals.append(system_id)
                            cursor.execute(
                                f"UPDATE listings_custom_v2 SET {', '.join(update_pairs)} WHERE System_ID = ?",
                                update_custom_vals
                            )
                        else:
                            # INSERT
                            cols_list = list(valid_custom_data.keys())
                            placeholders = ["?"] * len(cols_list)
                            insert_vals = [str(valid_custom_data[col_k]) if valid_custom_data[col_k] is not None else "" for col_k in cols_list]
                            cursor.execute(
                                f"INSERT INTO listings_custom_v2 ({', '.join(cols_list)}) VALUES ({', '.join(placeholders)})",
                                insert_vals
                            )
            except Exception as e_custom:
                add_log_message(f"[⚠️ WARNING] Lỗi khi đồng bộ vào bảng listings_custom_v2: {str(e_custom)}")
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": f"Đã lưu biên tập cục bộ cho căn {tk_id}"})
    else:
        # LẤY CHI TIẾT
        d = normalize_listing_for_client(row)
        conn.close()
        return jsonify({"status": "success", "listing": d})

def set_listing_crawl_failed(tk_id, reason):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        cursor = conn.cursor()
        row = cursor.execute(f"SELECT tk_id FROM {LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
        if row:
            cursor.execute(f"UPDATE {LISTINGS_TABLE} SET status = ? WHERE tk_id = ?", (f"crawl_failed:{reason}", tk_id))
            conn.commit()
        conn.close()
    except Exception as e:
        add_log_message(f"[⚠️ WARNING] Không thể cập nhật trạng thái lỗi cào cho căn {tk_id}: {str(e)}")

def run_ai_curation_for_crawled_listing(tk_id, data):
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
                    col_tieu_de = get_safe_col_name("Tiêu đề Public")
                    col_mo_ta = get_safe_col_name("Mô tả Public")
                    col_phuong_cu = get_safe_col_name("Phường cũ (AI)")
                    
                    cursor_update.execute(
                        f"UPDATE {LISTINGS_TABLE} SET `{col_tieu_de}` = ?, `{col_mo_ta}` = ?, `{col_phuong_cu}` = ? WHERE tk_id = ?",
                        (ai_result.get("tieu_de_public", ""), ai_result.get("mo_ta_public", ""), ai_result.get("phuong_cu", ""), tk_id)
                    )
                    conn_update.commit()
                    conn_update.close()
                    add_log_message(f"[🤖 AUTO-AI SUCCESS] Đã tự động tạo Tiêu đề Public và Mô tả bằng AI cho căn {tk_id}")
        except Exception as e_ai:
            add_log_message(f"[❌ AUTO-AI ERROR] Lỗi tự động tạo Curation AI cho căn {tk_id}: {str(e_ai)}")

@app.route('/api/listings/<tk_id>/recrawl', methods=['POST'])
def recrawl_single_listing(tk_id):
    """Cào lại hoặc cào mới duy nhất căn này bằng cookie Thiên Khôi hiện tại"""
    if not os.path.exists(DB_FILE):
        return jsonify({"status": "error", "message": "Database không tồn tại"}), 404
        
    data = {}
    try:
        data = request.json or {}
    except Exception:
        pass
        
    try:
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        row = cursor.execute(f"SELECT * FROM {LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
        
        d_row = {}
        if row:
            d_row = dict(row)
            
        detail_url = ""
        if row:
            detail_url = d_row.get("Link_Goc") or d_row.get("Link_Gốc")
            
        if not detail_url:
            if len(tk_id) == 36:
                detail_url = f"https://proptech.thienkhoi.com/warehouse/sources/{tk_id}"
            else:
                detail_url = f"https://data.thienkhoi.com/Hang/Detail/{tk_id}"
                
        conn.close()
        
        # Lấy Cookie
        cookie = ""
        if os.path.exists(COOKIE_FILE):
            try:
                with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                    cookie = f.read().strip()
            except Exception:
                pass
                
        if not cookie:
            set_listing_crawl_failed(tk_id, "cookie_expired")
            return jsonify({"status": "error", "message": "Không tìm thấy Cookie Thiên Khôi. Vui lòng cập nhật Cookie trước."}), 400
            
        add_log_message(f"[🚀] BẮT ĐẦU TIẾN TRÌNH CÀO LẺ 1 CĂN: {tk_id} - URL: {detail_url}")
        
        is_proptech = "proptech.thienkhoi.com" in detail_url or "backend.thienkhoi.com" in detail_url or len(tk_id) == 36
        
        if is_proptech:
            # Proptech detail API crawl
            access_token, _, _ = fetcher.extract_tokens(cookie)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://proptech.thienkhoi.com",
                "Referer": "https://proptech.thienkhoi.com/"
            }
            detail_api_url = f"https://backend.thienkhoi.com/product/v1/property/{tk_id}"
            r = requests.get(detail_api_url, headers=headers, timeout=20)
            if r.status_code in [401, 403]:
                refreshed_cookie = fetcher.try_refresh_tokens(COOKIE_FILE)
                if refreshed_cookie:
                    cookie = refreshed_cookie
                    _, access_token, _ = fetcher.extract_tokens(cookie)
                    headers["Authorization"] = f"Bearer {access_token}"
                    r = requests.get(detail_api_url, headers=headers, timeout=20)
                else:
                    set_listing_crawl_failed(tk_id, "cookie_expired")
                    return jsonify({"status": "error", "message": "Access token hết hạn và không thể refresh."}), 401
                    
            if r.status_code in [400, 404]:
                set_listing_crawl_failed(tk_id, "deleted")
                return jsonify({"status": "error", "message": f"Căn nhà đã bị khóa nguồn hoặc xóa trên Thiên Khôi (Mã lỗi {r.status_code})."}), 400
            elif r.status_code != 200:
                set_listing_crawl_failed(tk_id, "http_error")
                return jsonify({"status": "error", "message": f"Thiên Khôi API phản hồi mã lỗi {r.status_code}"}), 500
                
            detail_json = r.json()
            detail_data = detail_json.get("data") or {}
            if not detail_data:
                set_listing_crawl_failed(tk_id, "exception")
                return jsonify({"status": "error", "message": "Nội dung phản hồi API trống."}), 400
                
            ma_hang = detail_data.get("code") or tk_id
            tinh = (detail_data.get("district") or {}).get("provinceName", "TP Hồ Chí Minh")
            quan_name = (detail_data.get("district") or {}).get("name", "")
            phuong_name = (detail_data.get("ward") or {}).get("name", "")
            duong_name = (detail_data.get("street") or {}).get("name") if detail_data.get("street") else detail_data.get("streetName", "")
            ngo_so_nha = detail_data.get("address", "")
            
            phan_loai_names = [c.get("name") for c in (detail_data.get("criteria") or []) if c and c.get("name")]
            phan_loai = ", ".join(phan_loai_names)
            
            noi_dung_chinh = f"{ngo_so_nha} {duong_name}, {detail_data.get('area', '')}m2, {detail_data.get('floors', '')} tầng, mt {detail_data.get('wide', '')}m, sâu {detail_data.get('depth', '')}m, giá {detail_data.get('offeringPrice', '')} tỷ, Phường {phuong_name} {quan_name}"
            
            mo_ta_chi_tiet = detail_data.get("description", "")
            gia_chao = str(detail_data.get("offeringPrice", ""))
            dt_thuc_te = str(detail_data.get("actualArea", ""))
            dt_tren_so = str(detail_data.get("area", ""))
            so_tang = str(detail_data.get("floors", ""))
            mat_tien = str(detail_data.get("wide", ""))
            chieu_dai = str(detail_data.get("depth", ""))
            so_phong_ngu = str(detail_data.get("bedrooms") or "")
            so_nha_ve_sinh = str(detail_data.get("restrooms") or "")
            
            huong = detail_data.get("direction", "")
            duong_truoc_nha = str(detail_data.get("minimumRoadWidth") or "")
            trang_thai = detail_data.get("status", "")
            loai_hop_dong = detail_data.get("contractType", "")
            
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
                elif m_type in ["property_image"]:
                    property_images.append(m_url)
                    
            if not property_images:
                for m in media:
                    if m.get("type") == "checkin_image" and m.get("url"):
                        property_images.append(m.get("url"))
                        
            # Channels and tags processing
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
                "Link Gốc": detail_url,
                "System ID": d_row.get("System_ID") or f"SYS-{datetime.now().strftime('%Y%M%d').upper()}-{random.randint(100, 999)}",
                "Mã Khang Ngô (ID)": d_row.get("Ma_Khang_Ngo_ID") or gen_id_khang_ngo_python(ngo_so_nha, duong_name, quan_name),
                "Last Crawl": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                
                # English compatibility mapping
                "bedrooms": so_phong_ngu,
                "restrooms": so_nha_ve_sinh,
                "minimumRoadWidth": duong_truoc_nha,
                
                # Rich contract & technical fields from API
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
            
            for idx, url in enumerate(sodo_images[:5]):
                crawled_data[f"Sơ đồ thửa đất {idx+1}"] = url
                
            # Parse criteria groups and merge into crawled_data
            criteria_list = detail_data.get("criteria") or []
            
            # Save to scratch/last_crawled_criteria.json for debug
            try:
                os.makedirs("scratch", exist_ok=True)
                with open("scratch/last_crawled_criteria.json", "w", encoding="utf-8") as f:
                    json.dump(criteria_list, f, indent=4, ensure_ascii=False)
            except Exception as e_debug:
                add_log_message(f"[⚠️ WARNING] Lỗi ghi file debug criteria: {str(e_debug)}")
                
            criteria_cols = fetcher.parse_criteria_groups(criteria_list)
            crawled_data.update(criteria_cols)
            
            # Lưu raw_json_full và JSON_UI tinh gọn từ Proptech API
            crawled_data["raw_json_full"] = json.dumps(detail_data, ensure_ascii=False)
            try:
                import pool_lego
                json_ui_dict = pool_lego.extract_json_ui_data(detail_data)
                crawled_data["JSON_UI"] = json.dumps(json_ui_dict, ensure_ascii=False)
            except Exception as e_json_ui:
                add_log_message(f"[⚠️ WARNING] Lỗi trích xuất JSON_UI trong recrawl: {str(e_json_ui)}")
                
            fetcher.save_raw_to_sqlite(tk_id, crawled_data, property_images)
            
            # Call AI Curation helper
            run_ai_curation_for_crawled_listing(tk_id, data)
            
            add_log_message(f"[✅] Đã cào thô thành công căn (Proptech): {tk_id}. Tiến hành di cư ảnh và xuất bản...")
            
            # Gọi di cư ảnh & xuất bản đồng bộ
            try:
                run_image_migration_thread(limit=None, cookie=cookie, target_tk_id=tk_id)
            except Exception as e_mig:
                add_log_message(f"[⚠️ WARNING] Gặp lỗi khi tự động di cư ảnh hoặc xuất bản căn {tk_id}: {str(e_mig)}")
                
            # Trả về kết quả dòng đã cập nhật
            conn = sqlite3.connect(DB_FILE, timeout=30.0)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if LISTINGS_TABLE == "listings_v2":
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
                updated_row = cursor.execute(sql, (tk_id,)).fetchone()
            else:
                updated_row = cursor.execute(f"SELECT * FROM {LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
            conn.close()
            
            d = dict(updated_row)
            d["raw_images_tk"] = json.loads(d["raw_images_tk_json"]) if d.get("raw_images_tk_json") else []
            d["raw_drive_images"] = json.loads(d["raw_drive_images_json"]) if d.get("raw_drive_images_json") else []
            d["curated_config"] = json.loads(d["curated_config_json"]) if d.get("curated_config_json") else None
            
            status_text = d.get("status", "")
            if status_text == "published":
                msg = "Đã cào mới, di cư ảnh và xuất bản thành công trực tiếp lên Google Sheets Pool!"
            elif status_text == "raw_complete":
                msg = "Đã cào mới và di cư ảnh thành công (Gặp sự cố khi tự động đẩy lên Sheets Pool)."
            else:
                msg = "Đã cào mới thành công về SQLite (Gặp sự cố khi di cư ảnh hoặc đẩy lên Sheets)."
                
            return jsonify({"status": "success", "message": msg, "listing": d})

        # Thực hiện scrape chi tiết căn này trực tiếp trong Flask thread
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": cookie,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        r = requests.get(detail_url, headers=headers, timeout=20)
        if r.status_code in [400, 404]:
            set_listing_crawl_failed(tk_id, "deleted")
            return jsonify({"status": "error", "message": f"Căn nhà đã bị khóa nguồn hoặc xóa trên Thiên Khôi (HTTP {r.status_code})."}), 400
        elif r.status_code != 200:
            set_listing_crawl_failed(tk_id, "http_error")
            return jsonify({"status": "error", "message": f"Thiên Khôi phản hồi mã lỗi HTTP {r.status_code}"}), 500
            
        if "security.html" in r.url or "Account/Login" in r.url or "login" in r.url.lower():
            try:
                import winsound
                winsound.Beep(1000, 250)
                winsound.Beep(1000, 250)
                winsound.Beep(800, 450)
            except Exception:
                pass
            set_listing_crawl_failed(tk_id, "cookie_expired")
            return jsonify({"status": "error", "message": "Cookie đã hết hạn hoặc bị chặn bảo mật bởi Thiên Khôi."}), 401
            
        from bs4 import BeautifulSoup
        soup_detail = BeautifulSoup(r.text, "html.parser")
        
        # Kiểm tra tính hợp lệ của trang chi tiết để tránh ghi đè dữ liệu trống
        if not soup_detail.select_one('#Detail_sNoiDung') and not soup_detail.select_one('#Detail_sDiaChi') and not soup_detail.select_one('#Detail_iGiaChaoHopDong_show'):
            set_listing_crawl_failed(tk_id, "cookie_expired")
            return jsonify({"status": "error", "message": "Không tìm thấy nội dung chi tiết căn nhà trên trang Thiên Khôi. Vui lòng cập nhật lại Cookie."}), 400
            
        # Bóc tách DOM bằng helper của fetcher
        
        ma_hang_scraped = fetcher.get_val_by_label(soup_detail, "mã hàng") or tk_id
        
        phan_loai_scraped = ""
        btn_tieu_chi = soup_detail.select_one(".multiselect")
        if btn_tieu_chi:
            phan_loai_scraped = btn_tieu_chi.get("title", "").strip()
            
        mo_ta_scraped = fetcher.get_val_by_label(soup_detail, "mô tả")
        if not mo_ta_scraped:
            lbl_mota = soup_detail.find("label", text=re.compile(r'mô tả', re.I))
            if lbl_mota and lbl_mota.find_next_sibling():
                mo_ta_scraped = lbl_mota.find_next_sibling().text.strip()
                
        huong_scraped = ""
        sel_huong = soup_detail.select_one("#Detail_iID_HuongNha option[selected]")
        if sel_huong and sel_huong.get("value") != "0":
            huong_scraped = sel_huong.text.strip()
            
        duong_truoc_nha = fetcher.safe_get_val(soup_detail, '#Detail_iDuongVao_show') or fetcher.safe_get_val(soup_detail, '#Detail_iDuongVao')
        dt_dau_chu = fetcher.safe_get_val(soup_detail, '#Detail_sDienThoaiDauChu') or fetcher.get_val_by_label(soup_detail, "điện thoại đầu chủ") or fetcher.get_val_by_label(soup_detail, "đt đầu chủ")
        ten_dau_chu = fetcher.safe_get_val(soup_detail, '#Detail_sHopDongDauChu') or fetcher.get_val_by_label(soup_detail, "hợp đồng") or fetcher.get_val_by_label(soup_detail, "đầu chủ") or fetcher.get_val_by_label(soup_detail, "tên đầu chủ") or fetcher.get_val_by_label(soup_detail, "người ký")
        
        link_fb = fetcher.get_val_by_label(soup_detail, "facebook") or fetcher.get_val_by_label(soup_detail, "fb")
        if not link_fb:
            a_fb = soup_detail.find("a", href=re.compile(r'facebook\.com', re.I))
            if a_fb:
                link_fb = a_fb.get("href", "")
                
        img_els_td = soup_detail.select('#lightgalleryTD li')
        images_td = [li.get('data-src', '') for li in img_els_td if li.get('data-src')]
        
        img_els_nd = soup_detail.select('#lightgalleryND li')
        images_nd = [li.get('data-src', '') for li in img_els_nd if li.get('data-src')]
        
        so_nha = fetcher.safe_get_val(soup_detail, '#Detail_sDiaChi')
        duong_name = fetcher.safe_get_val(soup_detail, '#Detail_sDuongPho')
        quan_name = fetcher.safe_get_val(soup_detail, '#Detail_sTenQuan')
        phuong_name = fetcher.safe_get_val(soup_detail, '#Detail_sTenPhuongXa')
        
        behind_open_space = fetcher.get_val_by_label(soup_detail, "độ rộng mặt thoáng đằng sau nhà (m)") or fetcher.get_val_by_label(soup_detail, "độ rộng mặt thoáng đằng sau nhà") or fetcher.get_val_by_label(soup_detail, "mặt thoáng đằng sau")
        side_open_space = fetcher.get_val_by_label(soup_detail, "độ rộng mặt thoáng bên cạnh (m)") or fetcher.get_val_by_label(soup_detail, "độ rộng mặt thoáng bên cạnh") or fetcher.get_val_by_label(soup_detail, "mặt thoáng bên cạnh")
        bedrooms_scraped = fetcher.get_val_by_label(soup_detail, "số phòng ngủ") or fetcher.safe_get_val(soup_detail, '#Detail_iSoPhongNgu_show')
        restrooms_scraped = fetcher.get_val_by_label(soup_detail, "số nhà vệ sinh") or fetcher.get_val_by_label(soup_detail, "số toilet") or fetcher.safe_get_val(soup_detail, '#Detail_iSoToilet_show')
        balconies_scraped = fetcher.get_val_by_label(soup_detail, "số ban công")
        sidewalk_scraped = fetcher.get_val_by_label(soup_detail, "vỉa hè")
        commission_value = fetcher.get_val_by_label(soup_detail, "phần trăm trích thưởng") or fetcher.get_val_by_label(soup_detail, "phần trăm hoa hồng")
        certificate_series = fetcher.get_val_by_label(soup_detail, "series sổ đỏ") or fetcher.get_val_by_label(soup_detail, "series sổ")

        crawled_data = {
            "Mã Hàng": ma_hang_scraped,
            "Tỉnh": fetcher.safe_get_val(soup_detail, '#Detail_sTenTinh') or fetcher.get_val_by_label(soup_detail, "tỉnh/thành phố") or fetcher.get_val_by_label(soup_detail, "tỉnh"),
            "Quận": quan_name or fetcher.get_val_by_label(soup_detail, "quận/huyện") or fetcher.get_val_by_label(soup_detail, "quận"),
            "Phường": phuong_name or fetcher.get_val_by_label(soup_detail, "phường/xã") or fetcher.get_val_by_label(soup_detail, "phường"),
            "Đường": duong_name or fetcher.get_val_by_label(soup_detail, "đường/phố") or fetcher.get_val_by_label(soup_detail, "đường"),
            "Ngõ/Số nhà": so_nha or fetcher.get_val_by_label(soup_detail, "ngõ/số nhà"),
            "Phân loại": phan_loai_scraped,
            "Nội dung chính": fetcher.safe_get_val(soup_detail, '#Detail_sNoiDung').replace('\r', '').replace('\n', ' ') if fetcher.safe_get_val(soup_detail, '#Detail_sNoiDung') else "",
            "Mô tả chi tiết": mo_ta_scraped,
            "Giá chào": fetcher.safe_get_val(soup_detail, '#Detail_iGiaChaoHopDong_show') or fetcher.get_val_by_label(soup_detail, "giá chào"),
            "Giá Public": fetcher.safe_get_val(soup_detail, '#Detail_iGiaChaoHopDong_show') or fetcher.get_val_by_label(soup_detail, "giá chào"),
            "DT Thực tế": fetcher.safe_get_val(soup_detail, '#Detail_iDienTich_show') or fetcher.get_val_by_label(soup_detail, "diện tích thực tế"),
            "DT Trên sổ": fetcher.safe_get_val(soup_detail, '#Detail_iDienTichSo_show') or fetcher.get_val_by_label(soup_detail, "diện tích sổ"),
            "Mặt Tiền": fetcher.safe_get_val(soup_detail, '#Detail_iMatTien_show') or fetcher.get_val_by_label(soup_detail, "mặt tiền"),
            "Chieu_dai": fetcher.safe_get_val(soup_detail, '#Detail_iDai_show') or fetcher.safe_get_val(soup_detail, '#Detail_iDai') or fetcher.get_val_by_label(soup_detail, "chiều dài"),
            "Số Tầng": fetcher.safe_get_val(soup_detail, '#Detail_iSoTang_show') or fetcher.get_val_by_label(soup_detail, "số tầng"),
            "Số phòng ngủ": bedrooms_scraped,
            "Số nhà vệ sinh": restrooms_scraped,
            "Hướng": huong_scraped or fetcher.get_val_by_label(soup_detail, "hướng"),
            "Đường trước nhà (m)": duong_truoc_nha,
            "Tình trạng nhà": "Bình thường",
            "Trạng thái": fetcher.safe_get_val(soup_detail, '#Detail_iTrangThai') or fetcher.get_val_by_label(soup_detail, "trạng thái"),
            "Tên Chủ Nhà": fetcher.safe_get_val(soup_detail, '#Detail_sTenChuNha') or fetcher.get_val_by_label(soup_detail, "tên chủ nhà"),
            "Điện thoại 1": fetcher.safe_get_val(soup_detail, '#Detail_sDienThoaiChuNha') or fetcher.get_val_by_label(soup_detail, "điện thoại 1"),
            "Điện thoại Đầu Chủ": dt_dau_chu,
            "Tên Đầu Chủ (Hợp đồng)": ten_dau_chu,
            "Điểm Facebook": link_fb,
            "Link Gốc": detail_url,
            "System ID": d_row.get("System_ID") or f"SYS-{datetime.now().strftime('%Y%M%d').upper()}-{random.randint(100, 999)}",
            "Mã Khang Ngô (ID)": d_row.get("Ma_Khang_Ngo_ID") or gen_id_khang_ngo_python(so_nha, duong_name, quan_name),
            "Last Crawl": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),

            # English compatibility mapping
            "bedrooms": bedrooms_scraped,
            "restrooms": restrooms_scraped,
            "balconies": balconies_scraped,
            "sidewalk": sidewalk_scraped,
            "behindOpenSpace": behind_open_space,
            "sideOpenSpace": side_open_space,
            "minimumRoadWidth": duong_truoc_nha,
            "commissionValue": commission_value,
            "certificateSeries": certificate_series
        }

        # Parse criteria using direct label scraper + fallback to V1 multiselect
        classified_cols = fetcher.scrape_criteria_from_dom(soup_detail, phan_loai_scraped)
        crawled_data.update(classified_cols)
        
        if len(images_td) >= 1: crawled_data["Sơ đồ thửa đất 1"] = images_td[0]
        if len(images_td) >= 2: crawled_data["Sơ đồ thửa đất 2"] = images_td[1]
        if len(images_td) >= 3: crawled_data["Sơ đồ thửa đất 3"] = images_td[2]
        if len(images_td) >= 4: crawled_data["Sơ đồ thửa đất 4"] = images_td[3]
        if len(images_td) >= 5: crawled_data["Sơ đồ thửa đất 5"] = images_td[4]
        
        # Đưa trạng thái về raw_text để dọn dẹp ảnh cũ hoặc up Drive lại
        combined_images = []
        seen_images = set()
        for img in images_nd: # Only product/interior images, exclude diagrams
            if img and img not in seen_images:
                combined_images.append(img)
                seen_images.add(img)
        crawled_data["raw_images_tk_ordered"] = images_td + combined_images
        
        # Extract basic JSON_UI from columns for the HTML recrawler
        try:
            cfg = load_config()
            fields = cfg.get("json_ui_fields") or ["Criteria_Duong_truoc_nha"]
            json_ui_obj = {}
            for f in fields:
                json_ui_obj[f] = crawled_data.get(f, "")
            crawled_data["JSON_UI"] = json.dumps(json_ui_obj, ensure_ascii=False)
        except Exception as e_json_ui:
            add_log_message(f"[⚠️ WARNING] Lỗi trích xuất JSON_UI (HTML recrawl): {str(e_json_ui)}")
        crawled_data["raw_json_full"] = ""
        
        fetcher.save_raw_to_sqlite(tk_id, crawled_data, combined_images)
        
        # Call AI Curation helper
        run_ai_curation_for_crawled_listing(tk_id, data)
        
        add_log_message(f"[✅] Đã cào thô thành công căn: {tk_id}. Tiến hành di cư ảnh và xuất bản...")
        
        # Gọi di cư ảnh & xuất bản đồng bộ
        try:
            run_image_migration_thread(limit=None, cookie=cookie, target_tk_id=tk_id)
        except Exception as e_mig:
            add_log_message(f"[⚠️ WARNING] Gặp lỗi khi tự động di cư ảnh hoặc xuất bản căn {tk_id}: {str(e_mig)}")
            
        # Lấy lại dòng vừa cập nhật
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if LISTINGS_TABLE == "listings_v2":
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
            updated_row = cursor.execute(sql, (tk_id,)).fetchone()
        else:
            updated_row = cursor.execute(f"SELECT * FROM {LISTINGS_TABLE} WHERE tk_id = ?", (tk_id,)).fetchone()
        conn.close()
        
        d = dict(updated_row)
        d["raw_images_tk"] = json.loads(d["raw_images_tk_json"]) if d.get("raw_images_tk_json") else []
        d["raw_drive_images"] = json.loads(d["raw_drive_images_json"]) if d.get("raw_drive_images_json") else []
        d["curated_config"] = json.loads(d["curated_config_json"]) if d.get("curated_config_json") else None
        
        status_text = d.get("status", "")
        if status_text == "published":
            msg = "Đã cào mới, di cư ảnh và xuất bản thành công trực tiếp lên Google Sheets Pool!"
        elif status_text == "raw_complete":
            msg = "Đã cào mới và di cư ảnh thành công (Gặp sự cố khi tự động đẩy lên Sheets Pool)."
        else:
            msg = "Đã cào mới thành công về SQLite (Gặp sự cố khi di cư ảnh hoặc đẩy lên Sheets)."
            
        return jsonify({"status": "success", "message": msg, "listing": d})
        
    except Exception as e:
        add_log_message(f"[❌ LỖI] Lỗi cào lại căn {tk_id}: {str(e)}")
        set_listing_crawl_failed(tk_id, "exception")
        return jsonify({"status": "error", "message": f"Gặp sự cố khi cào lại: {str(e)}"}), 500

# ==================================================
# XUẤT BẢN LÊN GOOGLE SHEETS POOL (79 CỘT HOÀN CHỈNH)
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
    "Điện thoại Đầu Chủ", "Tên đầu chủ (BX)", "Điểm Facebook",
    "Last Crawl", "Last Sync", "Mã TK Mới",
    "Sơ đồ thửa đất 3", "Sơ đồ thửa đất 4", "Sơ đồ thửa đất 5",
    "Ảnh 16", "Ảnh 17", "Ảnh 18", "Ảnh 19", "Ảnh 20",
    "Ảnh 21", "Ảnh 22", "Ảnh 23", "Ảnh 24", "Ảnh 25"
]

def get_table_end_row_index(sheet_id, creds):
    """
    Truy vấn API Google Sheets để lấy endRowIndex của Table trên sheet tên 'Pool' (hoặc sheet đầu tiên).
    Trả về endRowIndex (int) hoặc None nếu không tìm thấy.
    """
    try:
        import requests
        # Lấy access token
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
    """Bảo vệ và định dạng trường dữ liệu TSV chuẩn để copy-paste không bao giờ bị lệch cột, gãy dòng"""
    if val is None:
        return ""
    val_str = str(val).strip()
    # 1. Khử hoàn toàn dấu tab (\t) để tránh lệch cột nghiêm trọng
    val_str = val_str.replace("\t", " ")
    # 2. Nếu chứa dấu xuống dòng (\n, \r) hoặc dấu nháy kép, bọc toàn bộ ô trong nháy kép Excel chuẩn
    if "\n" in val_str or "\r" in val_str or '"' in val_str:
        # Nhân đôi dấu nháy kép bên trong theo chuẩn RFC-4180
        val_str = val_str.replace('"', '""')
        return f'"{val_str}"'
    return val_str

generate_ai_curation_for_listing = generate_ai_curation_for_listing_backend

def execute_publish_listing(tk_id):
    return pool_lego.publish_listing(
        tk_id,
        get_google_credentials,
        load_config,
        add_log_message,
        db_file=DB_FILE
    )

@app.route('/api/publish/<tk_id>', methods=['POST'])
def publish_listing(tk_id):
    """API đẩy dòng dữ liệu 79 cột chính thức lên Google Sheets"""
    res = execute_publish_listing(tk_id)
    return jsonify(res)

@app.route('/api/listings/bulk-publish', methods=['POST'])
def bulk_publish_listings():
    """API đẩy hàng loạt danh sách các căn được chọn lên Google Sheets Pool"""
    try:
        data = request.get_json(force=True) or {}
        ids = data.get("ids", [])
        if not ids:
            return jsonify({"status": "error", "message": "Không có mã căn nào được chọn để xuất bản."}), 400
            
        add_log_message(f"[⚡] Bắt đầu đẩy hàng loạt {len(ids)} căn lên Google Sheets Pool...")
        
        success_count = 0
        for idx, tk_id in enumerate(ids):
            add_log_message(f"📦 [{idx+1}/{len(ids)}] Đang đẩy căn {tk_id}...")
            res = execute_publish_listing(tk_id)
            if res.get("status") == "success":
                success_count += 1
            else:
                add_log_message(f"[⚠️ WARNING] Căn {tk_id} đẩy không thành công: {res.get('message')}")
            time.sleep(0.5)  # Throttling to prevent API quota exhaust
            
        add_log_message(f"[✅] Đã hoàn thành đẩy hàng loạt! Thành công: {success_count}/{len(ids)} căn.")
        return jsonify({
            "status": "success",
            "success_count": success_count,
            "total_count": len(ids)
        })
    except Exception as e:
        add_log_message(f"[❌ LỖI] Lỗi trong quá trình xuất bản hàng loạt: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sync-databases', methods=['POST'])
def api_sync_databases():
    """API đồng bộ chéo giữa các pool database cục bộ"""
    try:
        data = request.get_json(force=True) or {}
        source = data.get("source")
        target = data.get("target")
        tk_id = data.get("tk_id")
        so_nha = data.get("so_nha")
        duong = data.get("duong")
        
        if not source or not target:
            return jsonify({"status": "error", "message": "Thiếu tham số source hoặc target."}), 400
            
        res = pool_lego.sync_between_databases(source, target, tk_id, so_nha, duong, add_log_message)
        return jsonify(res)
    except Exception as e:
        add_log_message(f"[❌ LỖI] Lỗi trong quá trình đồng bộ API: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
        
@app.route('/api/sync-json-ui', methods=['POST'])
def api_sync_json_ui():
    """Kích hoạt tiến trình đồng bộ và vá dữ liệu JSON UI"""
    try:
        data = request.get_json(force=True) or {}
        limit = data.get("limit")
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                limit = None
                
        def sync_worker():
            try:
                import scratch.sync_json_ui as sync_json_ui
                sync_json_ui.run_sync(limit=limit, add_log_message=add_log_message)
            except Exception as ex:
                add_log_message(f"[❌ LỖI] Lỗi tiến trình đồng bộ JSON UI: {str(ex)}")
                
        threading.Thread(target=sync_worker, daemon=True).start()
        
        return jsonify({
            "status": "success",
            "message": "Tiến trình đồng bộ và vá dữ liệu JSON UI đã được kích hoạt chạy ngầm."
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sync-databases/recrawl-all', methods=['POST'])
def api_recrawl_all():
    """API kích hoạt tiến trình cào lại định kỳ chạy ngầm toàn bộ CSDL và tổng hợp thay đổi"""
    def run_recrawl():
        try:
            pool_lego.recrawl_all_listings(add_log_message)
        except Exception as e:
            add_log_message(f"[❌ LỖI] Lỗi tiến trình cào lại ngầm: {str(e)}")
            
    threading.Thread(target=run_recrawl, daemon=True).start()
    return jsonify({"status": "success", "message": "Đã bắt đầu tiến trình cào lại định kỳ chạy ngầm toàn bộ CSDL."})

@app.route('/api/listings/apply-diff', methods=['POST'])
def apply_diff():
    """API áp dụng có chọn lọc các trường thay đổi từ Raw sang Custom"""
    try:
        data = request.get_json(force=True) or {}
        system_id = data.get("System_ID")
        fields = data.get("fields", [])
        
        if not system_id or not fields:
            return jsonify({"status": "error", "message": "Thiếu tham số System_ID hoặc danh sách fields."}), 400
            
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        raw_row = cursor.execute("SELECT * FROM listings_v2 WHERE System_ID = ?", (system_id,)).fetchone()
        if not raw_row:
            conn.close()
            return jsonify({"status": "error", "message": f"Không tìm thấy căn trong listings_v2 với System_ID {system_id}"}), 404
            
        raw_dict = dict(raw_row)
        
        custom_row = cursor.execute("SELECT * FROM listings_custom_v2 WHERE System_ID = ?", (system_id,)).fetchone()
        
        cursor.execute("PRAGMA table_info(listings_custom_v2)")
        custom_cols = {row[1] for row in cursor.fetchall()}
        
        update_fields = {}
        for f in fields:
            if f in custom_cols:
                update_fields[f] = raw_dict.get(f)
                
        if not update_fields:
            conn.close()
            return jsonify({"status": "error", "message": "Không có trường hợp lệ nào để cập nhật."}), 400
            
        if custom_row:
            set_clause = ", ".join([f"`{k}` = ?" for k in update_fields.keys()])
            vals = list(update_fields.values()) + [system_id]
            cursor.execute(f"UPDATE listings_custom_v2 SET {set_clause} WHERE System_ID = ?", vals)
        else:
            insert_fields = dict(update_fields)
            insert_fields['System_ID'] = system_id
            cols = list(insert_fields.keys())
            vals = list(insert_fields.values())
            placeholders = ", ".join(["?"] * len(cols))
            cursor.execute(f"INSERT INTO listings_custom_v2 ({', '.join([f'`{c}`' for c in cols])}) VALUES ({placeholders})", vals)
            
        cursor.execute("UPDATE listings_v2 SET pending_diff_json = NULL WHERE System_ID = ?", (system_id,))
        conn.commit()
        conn.close()
        
        add_log_message(f"[✅] Đã áp dụng thành công các trường {fields} từ Raw sang Custom cho System ID {system_id}.")
        return jsonify({"status": "success", "message": "Đã áp dụng thay đổi thành công."})
    except Exception as e:
        add_log_message(f"[❌ LỖI] Lỗi khi áp dụng diff: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/listings/clear-diff', methods=['POST'])
def clear_diff():
    """API bỏ qua thay đổi của đối tác và xóa pending_diff_json"""
    try:
        data = request.get_json(force=True) or {}
        system_id = data.get("System_ID")
        if not system_id:
            return jsonify({"status": "error", "message": "Thiếu tham số System_ID."}), 400
            
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("UPDATE listings_v2 SET pending_diff_json = NULL WHERE System_ID = ?", (system_id,))
        conn.commit()
        conn.close()
        
        add_log_message(f"[✅] Đã bỏ qua thay đổi và xoá pending_diff_json cho System ID {system_id}.")
        return jsonify({"status": "success", "message": "Đã xóa bỏ qua thay đổi thành công."})
    except Exception as e:
        add_log_message(f"[❌ LỖI] Lỗi khi clear diff: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

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
        
    cfg = load_config()
    port = int(os.environ.get("FLASK_PORT", 5000))
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
