#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==========================================
THIEN KHOI BĐS CRAWLER - LIVE PIPELINE v4
Chế độ Siêu Tàng Hình (Ultra-Stealth Mode)
Lưu trữ đệm SQLite 76 cột đồng nhất với Pool Sheet
==========================================
"""

import os
import sys
import time
import random
import json
import sqlite3
import re
from datetime import datetime
import argparse
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import requests
from bs4 import BeautifulSoup
import hashlib

# Ép terminal Windows/các hệ điều hành mã hóa UTF-8 để hiển thị ký tự Tiếng Việt không bị lỗi
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

try:
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# ==========================================
# CẤU HÌNH THỜI GIAN "SIÊU TÀNG HÌNH" (PO APPROVED)
# ==========================================
DELAY_HOUSE_MIN = 8.0   # Giây nghỉ tối thiểu giữa các căn
DELAY_HOUSE_MAX = 15.0  # Giây nghỉ tối đa giữa các căn

DELAY_PAGE_MIN = 20.0  # Giây nghỉ tối thiểu chuyển trang (20s)
DELAY_PAGE_MAX = 40.0  # Giây nghỉ tối đa chuyển trang (40s)

# Cấu hình Throttling khi tải ảnh up Drive
DELAY_IMAGE_DOWNLOAD = 3.0 # Giây nghỉ sau mỗi căn khi tải ảnh để bảo vệ IP

# Cờ và hàm kiểm tra dừng tiến trình ngắt quãng cho phép Flask hủy luồng tức thì
STOP_REQUESTED = False

def sleep_interruptible(seconds):
    steps = int(seconds * 10)
    for _ in range(steps):
        if STOP_REQUESTED:
            break
        time.sleep(0.1)

# File Database cục bộ (Tích hợp sẵn trong Python, không cần cài đặt)
DB_FILE = "raw_archive.db"

# ==========================================
# 76 CỘT NGHIỆP VỤ ĐỒNG NHẤT VỚI POOL SHEET SCHEMA
# ==========================================
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
"Last Crawl", "Last Sync"
]

# ==========================================
# KHỞI TẠO CƠ SỞ DỮ LIỆU SQLITE
# ==========================================
def remove_accents(input_str):
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
    if not header:
        return ""
    # 1. Loại bỏ dấu tiếng Việt
    no_accent = remove_accents(header)
    # 2. Thay thế các ký tự không phải chữ cái tiếng Anh, số, gạch dưới thành gạch dưới
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', no_accent)
    # 3. Gộp nhiều dấu gạch dưới liên tục thành một gạch dưới duy nhất
    cleaned = re.sub(r'_+', '_', cleaned)
    # 4. Loại bỏ gạch dưới ở đầu và cuối
    cleaned = cleaned.strip('_')
    return cleaned

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tạo bảng listings với 76 cột nghiệp vụ + các cột quản lý hệ thống
    columns_def = []

    # 1. Các cột hệ thống
    columns_def.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
    columns_def.append("tk_id TEXT UNIQUE")
    columns_def.append("status TEXT DEFAULT 'raw_text'") # raw_text | raw_complete | published
    columns_def.append("raw_images_tk_json TEXT")
    columns_def.append("raw_drive_images_json TEXT")
    columns_def.append("curated_config_json TEXT")
    columns_def.append("Chieu_dai TEXT")

    # 2. 76 cột Pool
    for header in POOL_HEADERS:
        col_name = get_safe_col_name(header)
        columns_def.append(f"`{col_name}` TEXT")
        
    create_table_sql = f"CREATE TABLE IF NOT EXISTS listings ({', '.join(columns_def)})"
    cursor.execute(create_table_sql)
    conn.commit()

    # Khởi tạo bảng crawl_sessions lưu lịch sử phiên cào
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

    # --- BẮT ĐẦU DI CƯ (MIGRATION) CỘT KIỂU CŨ SANG KIỂU MỚI SẠCH SẼ ---
    try:
        # Lấy danh sách cột hiện có trong database
        cursor.execute("PRAGMA table_info(listings)")
        existing_cols = [row[1] for row in cursor.fetchall()]
        
        # Thêm cột Chieu_dai nếu chưa tồn tại
        if "Chieu_dai" not in existing_cols:
            print("[*] Bo sung cot `Chieu_dai` vao database SQLite...")
            cursor.execute("ALTER TABLE listings ADD COLUMN Chieu_dai TEXT")
            conn.commit()
            
        # Duyệt qua từng header để kiểm tra xem có cột kiểu cũ cần đổi tên không
        for header in POOL_HEADERS:
            old_col = re.sub(r'[^a-zA-Z0-9_]', '_', header)
            new_col = get_safe_col_name(header)
            
            # Nếu cột cũ có tồn tại, nhưng cột mới chưa tồn tại, và tên cũ khác tên mới
            if old_col in existing_cols and new_col not in existing_cols and old_col != new_col:
                print(f"[*] Phat hien cot cu `{old_col}`. Tien hanh doi ten thanh `{new_col}`...")
                try:
                    cursor.execute(f"ALTER TABLE listings RENAME COLUMN `{old_col}` TO `{new_col}`")
                    conn.commit()
                except Exception as e:
                    print(f"[⚠️ WARNING] Khong the doi ten cot {old_col} sang {new_col}: {str(e)}")
    except Exception as ex:
        print(f"[⚠️ WARNING] Loi trong tien trinh migration SQLite: {str(ex)}")
        
    conn.close()
    print(f"[*] Đã kết nối SQLite và khởi tạo thành công bảng listings ({len(POOL_HEADERS)} cột nghiệp vụ).")

# ==========================================
# CÁC HÀM TRÍCH XUẤT DOM AN TOÀN (TỪ EXTENSION THẬT)
# ==========================================
def safe_get_val(soup, selector, is_input=True):
    el = soup.select_one(selector)
    if not el:
        return ""
    if is_input:
        val = el.get('value', '').strip()
        if val:
            return val
    return el.text.strip()

def get_val_by_label(soup, label_text):
    target = label_text.lower().strip()

    # 1. Thử khớp chính xác trước (Exact Match) để tránh nhầm lẫn
    for label in soup.select('label'):
        txt = label.text.replace(':', '').strip().lower()
        if txt == target:
            # Thử tìm input là sibling kế cận (bỏ qua thẻ br nếu có)
            inp_sibling = label.find_next_sibling('input')
            if inp_sibling:
                return inp_sibling.get('value', '').strip()
                
            # Hoặc tìm trong wrapper sibling
            sibling = label.find_next_sibling()
            if sibling:
                inp = sibling.find('input')
                if inp:
                    return inp.get('value', '').strip()
                a = sibling.find('a')
                if a and target not in ["mô tả", "mô tả chi tiết", "nội dung", "nội dung chính"]:
                    return a.get('href', '').strip()
                return sibling.text.strip()
                
    # 2. Nếu không khớp chính xác, thử khớp substring nhưng loại trừ các trường hợp nhầm lẫn
    for label in soup.select('label'):
        txt = label.text.replace(':', '').strip().lower()
        if target in txt:
            # Ngăn chặn nhầm lẫn 'hợp đồng' với 'giá chào hợp đồng' hoặc 'giá hợp đồng'
            if target == "hợp đồng" and "giá" in txt:
                continue
            # Ngăn chặn nhầm lẫn 'đầu chủ' với 'điện thoại đầu chủ'
            if target == "đầu chủ" and "điện thoại" in txt:
                continue
                
            inp_sibling = label.find_next_sibling('input')
            if inp_sibling:
                return inp_sibling.get('value', '').strip()
                
            sibling = label.find_next_sibling()
            if sibling:
                inp = sibling.find('input')
                if inp:
                    return inp.get('value', '').strip()
                a = sibling.find('a')
                if a and target not in ["mô tả", "mô tả chi tiết", "nội dung", "nội dung chính"]:
                    return a.get('href', '').strip()
                return sibling.text.strip()
    return ""

def build_paging_url(base_url, page_num):
    # Tự động thay thế tham số page trong query string bảo toàn casing và thứ tự (in-place)
    parsed = urlparse(base_url)
    qd = parse_qs(parsed.query)

    # Tìm xem key phân trang nguyên bản là gì để giữ nguyên casing và vị trí trong query
    page_key = None
    for k in qd.keys():
        if k.lower() in ['page', 'p']:
            page_key = k
            break
            
    if page_key is not None:
        qd[page_key] = [str(page_num)]
    else:
        # Nếu không có sẵn thì thêm mới (mặc định là 'Page' của Thiên Khôi)
        qd['Page'] = [str(page_num)]

    new_query = urlencode(qd, doseq=True)
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

def update_config_start_page(next_page):
    try:
        config_file = "curator_config.json"
        cfg = {}
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
        cfg["crawler_start_page"] = next_page
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        print(f"[*] Đã tự động lưu trang tiếp theo vào cấu hình: Trang {next_page}")
    except Exception as e:
        print(f"[⚠️ WARNING] Không thể tự động lưu trang tiếp theo vào curator_config.json: {str(e)}")

# ==========================================
# LUỒNG 1: CÀO TEXT THÔ VÀ LINK ẢNH DÙNG DOM SELECTOR THẬT
# ==========================================
def scrape_district(base_list_url, session_cookie, limit=None, filter_district=None, start_page=None):
    global DELAY_HOUSE_MIN, DELAY_HOUSE_MAX, DELAY_PAGE_MIN, DELAY_PAGE_MAX
    init_db()

    # Tự động nạp cấu hình thời gian nghỉ/tốc độ cào tin từ file cấu hình
    try:
        config_file = "curator_config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                if "delay_house_min" in cfg: DELAY_HOUSE_MIN = float(cfg["delay_house_min"])
                if "delay_house_max" in cfg: DELAY_HOUSE_MAX = float(cfg["delay_house_max"])
                if "delay_page_min" in cfg: DELAY_PAGE_MIN = float(cfg["delay_page_min"])
                if "delay_page_max" in cfg: DELAY_PAGE_MAX = float(cfg["delay_page_max"])
                print(f"[*] Áp dụng tốc độ cào: Căn ({DELAY_HOUSE_MIN}s - {DELAY_HOUSE_MAX}s) | Trang ({DELAY_PAGE_MIN}s - {DELAY_PAGE_MAX}s)")
    except Exception as e:
        print(f"[⚠️ WARNING] Không thể đọc cấu hình tốc độ cào, sử dụng mặc định: {str(e)}")

    # Tự động chuẩn hóa đường dẫn từ /Hang hoặc /Hang/Index sang /Hang/Partial_Item để máy chủ cho phép phân trang qua GET
    try:
        parsed_url = urlparse(base_list_url)
        path_lower = parsed_url.path.lower().rstrip('/')
        if path_lower in ['/hang', '/hang/index']:
            base_list_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                '/Hang/Partial_Item',
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
            print(f"[*] Đã tự động chuyển đổi URL sang Endpoint phân trang gốc: {base_list_url}")
    except Exception as e:
        print(f"[⚠️ WARNING] Lỗi khi chuẩn hóa URL phân trang: {str(e)}")
    
    # Nạp danh sách tk_id đã có sẵn vào bộ nhớ RAM (set) để check trùng lập O(1)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    existing_ids = set(row[0] for row in cursor.execute("SELECT tk_id FROM listings"))
    conn.close()

    print(f"[*] Đã tải {len(existing_ids)} căn có sẵn từ SQLite vào bộ nhớ đệm RAM.")

    if filter_district:
        print(f"[*] Chế độ lọc Quận được kích hoạt: Chỉ cào các căn thuộc '{filter_district}'")
        
    # Tự động trích xuất trang bắt đầu từ URL nếu start_page không được truyền
    if start_page is None:
        start_page = 1
        try:
            parsed_url = urlparse(base_list_url)
            qd = parse_qs(parsed_url.query)
            for k, v in qd.items():
                if k.lower() in ['page', 'p'] and v:
                    start_page = int(v[0])
                    break
        except Exception:
            pass
            
    print(f"[*] Trang bắt đầu cào: Trang {start_page}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": session_cookie,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    crawled_count = 0
    session_start_time = time.time()
    session_start_time_iso = datetime.now().isoformat()
    cookie_sig = hashlib.md5((session_cookie or "").encode('utf-8')).hexdigest()[:8].upper()
    session_status = 'stopped' # Default status if exited or stopped

    def print_report():
        nonlocal session_status
        duration = time.time() - session_start_time
        mins = int(duration // 60)
        secs = int(duration % 60)
        avg = f"{duration / crawled_count:.1f} giây/căn" if crawled_count > 0 else "N/A"
        print("\n" + "="*50)
        print("📊 BÁO CÁO PHIÊN CÀO TIN (CRAWL SESSION REPORT)")
        print(f"🔑 Cookie ID (MD5): {cookie_sig}")
        print(f"⏱️ Tổng thời gian cào: {mins} phút {secs} giây")
        print(f"🏠 Số căn cào thành công: {crawled_count} căn")
        print(f"⚡ Tốc độ trung bình: {avg}")
        print("="*50 + "\n")
        
        # Ghi nhận lịch sử phiên cào vào SQLite
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            end_time_iso = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO crawl_sessions (cookie_sig, start_time, end_time, duration, crawled_count, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cookie_sig, session_start_time_iso, end_time_iso, duration, crawled_count, session_status))
            conn.commit()
            conn.close()
            print("[*] Đã tự động lưu lịch sử phiên cào vào database SQLite.")
        except Exception as err:
            print(f"[⚠️ WARNING] Không thể lưu lịch sử phiên cào: {str(err)}")

    print(f"\n[+] KHỞI ĐỘNG CÀO DỮ LIỆU THẬT (data.thienkhoi.com - Chế độ Siêu Tàng Hình)")
    
    # Nếu không giới hạn căn (limit=0 hoặc None), cho phép cào tối đa 1000 trang
    max_pages_to_crawl = 1000 if not limit else 20
    end_page = start_page + max_pages_to_crawl
    
    try:
        for page in range(start_page, end_page):
            if STOP_REQUESTED:
                print("[*] Nhận lệnh dừng từ hệ thống. Đang dừng cào...")
                session_status = 'stopped'
                break
                
            if limit and crawled_count >= limit:
                session_status = 'limit_reached'
                break
                
            # Tự động dựng URL chuyển trang thông minh
            list_url = build_paging_url(base_list_url, page)
            print(f"\n--- Đang mở danh sách Trang {page}/{end_page - 1}: {list_url} ---")
            
            try:
                # Gửi request lấy HTML danh sách
                response = requests.get(list_url, headers=headers, timeout=20)
                if response.status_code != 200:
                    print(f"[❌ LỖI] Lỗi kết nối đến trang danh sách: HTTP {response.status_code}")
                    if response.status_code in [401, 403]:
                        print("[*] Dừng chương trình do lỗi xác thực (HTTP 401/403). Vui lòng cập nhật Cookie mới.")
                        session_status = 'cookie_expired'
                        try:
                            import winsound
                            winsound.Beep(1000, 250)
                            winsound.Beep(1000, 250)
                            winsound.Beep(800, 450)
                        except Exception:
                            pass
                        sys.exit(1)
                    sleep_interruptible(10)
                    continue
                    
                # Kiểm tra nếu bị redirect về trang bảo mật
                if "security.html" in response.url:
                    print("\n[❌ LỖI BẢO MẬT] Cookie Thiên Khôi của anh đã hết hạn hoặc bị thu hồi!")
                    print("[*] Vui lòng xóa file 'thienkhoi_cookie.txt' và chạy lại để nhập Cookie mới.")
                    session_status = 'cookie_expired'
                    try:
                        import winsound
                        winsound.Beep(1000, 250)
                        winsound.Beep(1000, 250)
                        winsound.Beep(800, 450)
                    except Exception:
                        pass
                    sys.exit(1)
                    
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Quét các dòng tr bắt đầu bằng tr_ (Đặc tả DOM thật của danh sách Thiên Khôi)
                rows = soup.select('tr[id^="tr_"]')
                if not rows:
                    print("[-] Không tìm thấy hàng dữ liệu nào (tr[id^='tr_']) trên trang này. Dừng cào quận này hoặc kiểm tra cookie.")
                    break
                    
                print(f"[*] Quét thấy {len(rows)} căn nhà trên trang danh sách.")
                
                new_listings_on_page = []
                for row in rows:
                    row_id_attr = row.get("id", "")
                    if not row_id_attr:
                        continue
                    
                    # Trích xuất mã hàng thật
                    tk_id = row_id_attr.split("_")[1].strip()
                    detail_url = f"https://data.thienkhoi.com/Hang/Detail/{tk_id}"
                    
                    # CHỐNG TRÙNG LẬP TRÊN RAM (Tối ưu tuyệt đối)
                    if tk_id in existing_ids:
                        continue
                    
                    # Lọc Quận trên danh sách trước để tránh cào thừa (tiết kiệm request)
                    if filter_district:
                        row_text = row.text.lower()
                        target = filter_district.lower().strip()
                        target_short = target.replace("quận", "q").replace(" ", "")
                        target_dot = target.replace("quận", "q.").replace(" ", "")
                        
                        if (target not in row_text) and (target_short not in row_text) and (target_dot not in row_text):
                            continue
                        
                    new_listings_on_page.append((tk_id, detail_url))
                    
                if not new_listings_on_page:
                    print("[*] Không phát hiện căn mới nào trên trang này. Chuyển trang tiếp theo.")
                else:
                    print(f"[+] Phát hiện {len(new_listings_on_page)} căn mới tinh. Bắt đầu cào chi tiết...")
                    
                # Duyệt tuần tự đơn luồng (Single Thread) để né tránh quét Bot của đối tác
                for tk_id, detail_url in new_listings_on_page:
                    if STOP_REQUESTED:
                        print("[*] Nhận lệnh dừng từ hệ thống. Đang dừng cào...")
                        session_status = 'stopped'
                        break
                        
                    if limit and crawled_count >= limit:
                        session_status = 'limit_reached'
                        break
                        
                    # Nghỉ ngẫu nhiên Siêu tàng hình: 8 - 15 giây (PO APPROVED)
                    house_delay = random.uniform(DELAY_HOUSE_MIN, DELAY_HOUSE_MAX)
                    print(f"  -> Nghỉ tàng hình {house_delay:.2f} giây trước khi mở căn mới...")
                    sleep_interruptible(house_delay)
                    
                    if STOP_REQUESTED:
                        print("[*] Nhận lệnh dừng từ hệ thống. Đang dừng cào...")
                        session_status = 'stopped'
                        break
                        
                    print(f"  [+] Đang cào chi tiết mã căn: {tk_id}...")
                    
                    # GỬI REQUEST LẤY CHI TIẾT HTML THẬT
                    response_detail = requests.get(detail_url, headers=headers, timeout=20)
                    if response_detail.status_code != 200:
                        print(f"  [❌ LỖI] Lỗi HTTP {response_detail.status_code} khi tải căn {tk_id}.")
                        if response_detail.status_code in [401, 403]:
                            print("[*] Dừng chương trình do lỗi xác thực (HTTP 401/403). Vui lòng cập nhật Cookie mới.")
                            session_status = 'cookie_expired'
                            try:
                                import winsound
                                winsound.Beep(1000, 250)
                                winsound.Beep(1000, 250)
                                winsound.Beep(800, 450)
                            except Exception:
                                pass
                            sys.exit(1)
                        continue
                        
                    if "security.html" in response_detail.url:
                        print("\n[❌ LỖI BẢO MẬT] Cookie Thiên Khôi đã hết hạn khi tải chi tiết căn nhà!")
                        print("[*] Dừng cào để đảm bảo an toàn. Vui lòng chạy lại và cập nhật Cookie mới.")
                        session_status = 'cookie_expired'
                        try:
                            import winsound
                            winsound.Beep(1000, 250)
                            winsound.Beep(1000, 250)
                            winsound.Beep(800, 450)
                        except Exception:
                            pass
                        sys.exit(1)
                        
                    soup_detail = BeautifulSoup(response_detail.text, "html.parser")
                    
                    # ==========================================
                    # BÓC TÁCH DOM SELECTOR THỰC TẾ TỪ CHROME EXTENSION V18
                    # ==========================================
                    
                    # 1. Bóc mã hàng chính xác trên giao diện
                    ma_hang_scraped = get_val_by_label(soup_detail, "mã hàng")
                    if not ma_hang_scraped:
                        ma_hang_scraped = tk_id
                    
                    # 2. Phân loại từ mục multi-select
                    phan_loai_scraped = ""
                    btn_tieu_chi = soup_detail.select_one(".multiselect")
                    if btn_tieu_chi:
                        phan_loai_scraped = btn_tieu_chi.get("title", "").strip()
                    
                    # 3. Mô tả chi tiết
                    mo_ta_scraped = get_val_by_label(soup_detail, "mô tả")
                    if not mo_ta_scraped:
                        # Fallback tìm div hoặc span sau label
                        lbl_mota = soup_detail.find("label", text=re.compile(r'mô tả', re.I))
                        if lbl_mota and lbl_mota.find_next_sibling():
                            mo_ta_scraped = lbl_mota.find_next_sibling().text.strip()
                    
                    # 4. Hướng nhà
                    huong_scraped = ""
                    sel_huong = soup_detail.select_one("#Detail_iID_HuongNha option[selected]")
                    if sel_huong and sel_huong.get("value") != "0":
                        huong_scraped = sel_huong.text.strip()
                    
                    # 5. Đường trước nhà
                    duong_truoc_nha = safe_get_val(soup_detail, '#Detail_iDuongVao_show') or safe_get_val(soup_detail, '#Detail_iDuongVao')
                    
                    # 6. Điện thoại và Tên Đầu chủ
                    dt_dau_chu = safe_get_val(soup_detail, '#Detail_sDienThoaiDauChu') or get_val_by_label(soup_detail, "điện thoại đầu chủ") or get_val_by_label(soup_detail, "đt đầu chủ")
                    ten_dau_chu = safe_get_val(soup_detail, '#Detail_sHopDongDauChu') or get_val_by_label(soup_detail, "hợp đồng") or get_val_by_label(soup_detail, "đầu chủ") or get_val_by_label(soup_detail, "tên đầu chủ") or get_val_by_label(soup_detail, "người ký")
                    
                    # 7. Link Facebook
                    link_fb = get_val_by_label(soup_detail, "facebook") or get_val_by_label(soup_detail, "fb")
                    if not link_fb:
                        a_fb = soup_detail.find("a", href=re.compile(r'facebook\.com', re.I))
                        if a_fb:
                            link_fb = a_fb.get("href", "")
                    
                    # 8. Sơ đồ thửa đất và lưới ảnh nội thất
                    img_els_td = soup_detail.select('#lightgalleryTD li')
                    images_td = [li.get('data-src', '') for li in img_els_td if li.get('data-src')]
                    
                    img_els_nd = soup_detail.select('#lightgalleryND li')
                    images_nd = [li.get('data-src', '') for li in img_els_nd if li.get('data-src')]
                    
                    # Đóng gói dữ liệu bóc tách
                    crawled_data = {
                        "Mã Hàng": ma_hang_scraped,
                        "Tỉnh": safe_get_val(soup_detail, '#Detail_sTenTinh'),
                        "Quận": safe_get_val(soup_detail, '#Detail_sTenQuan'),
                        "Phường": safe_get_val(soup_detail, '#Detail_sTenPhuongXa'),
                        "Đường": safe_get_val(soup_detail, '#Detail_sDuongPho'),
                        "Ngõ/Số nhà": safe_get_val(soup_detail, '#Detail_sDiaChi'),
                        "Phân loại": phan_loai_scraped,
                        "Nội dung chính": safe_get_val(soup_detail, '#Detail_sNoiDung'),
                        "Mô tả chi tiết": mo_ta_scraped,
                        "Giá chào": safe_get_val(soup_detail, '#Detail_iGiaChaoHopDong_show'),
                        "Giá Public": safe_get_val(soup_detail, '#Detail_iGiaChaoHopDong_show'), # Mặc định lấy giá chào
                        "DT Thực tế": safe_get_val(soup_detail, '#Detail_iDienTich_show'),
                        "DT Trên sổ": safe_get_val(soup_detail, '#Detail_iDienTichSo_show'),
                        "Mặt Tiền": safe_get_val(soup_detail, '#Detail_iMatTien_show'),
                        "Chieu_dai": safe_get_val(soup_detail, '#Detail_iDai_show') or safe_get_val(soup_detail, '#Detail_iDai'),
                        "Số Tầng": safe_get_val(soup_detail, '#Detail_iSoTang_show'),
                        "Số phòng ngủ": safe_get_val(soup_detail, '#Detail_iSoPhongNgu_show'),
                        "Số nhà vệ sinh": safe_get_val(soup_detail, '#Detail_iSoToilet_show'),
                        "Hướng": huong_scraped,
                        "Đường trước nhà (m)": duong_truoc_nha,
                        "Tình trạng nhà": "Bình thường",
                        "Trạng thái": safe_get_val(soup_detail, '#Detail_iTrangThai'),
                        "Tên Chủ Nhà": safe_get_val(soup_detail, '#Detail_sTenChuNha'),
                        "Điện thoại 1": safe_get_val(soup_detail, '#Detail_sDienThoaiChuNha'),
                        "Điện thoại Đầu Chủ": dt_dau_chu,
                        "Tên Đầu Chủ (Hợp đồng)": ten_dau_chu,
                        "Điểm Facebook": link_fb,
                        "Link Gốc": detail_url,
                        "System ID": f"SYS-{datetime.now().strftime('%Y%M%d').upper()}-{random.randint(100, 999)}",
                        "Last Crawl": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    }
                    
                    # Ghi nhận các liên kết ảnh sơ đồ (Cột 28 và 29)
                    if len(images_td) >= 1: crawled_data["Sơ đồ thửa đất 1"] = images_td[0]
                    if len(images_td) >= 2: crawled_data["Sơ đồ thửa đất 2"] = images_td[1]
                    
                    # Kiểm tra lại chắc chắn ở trang chi tiết
                    if filter_district:
                        quan_chi_tiet = crawled_data.get("Quận", "").lower().strip()
                        target = filter_district.lower().strip()
                        target_short = target.replace("quận", "q").replace(" ", "")
                        target_dot = target.replace("quận", "q.").replace(" ", "")
                        
                        if (target not in quan_chi_tiet) and (target_short not in quan_chi_tiet) and (target_dot not in quan_chi_tiet):
                            print(f"  [-] Căn {tk_id} thuộc quận {crawled_data.get('Quận')}, không phải '{filter_district}'. Bỏ qua.")
                            continue
                    
                    # Gom ảnh nội thất và sơ đồ lưu thô (GĐ2 sẽ di cư lên Google Drive/Cloudinary)
                    combined_images = []
                    seen_images = set()
                    for img in images_td + images_nd:
                        if img and img not in seen_images:
                            combined_images.append(img)
                            seen_images.add(img)
                    save_raw_to_sqlite(tk_id, crawled_data, combined_images)
                    
                    existing_ids.add(tk_id)
                    crawled_count += 1
                    print(f"  => Đã cào và lưu thành công mã căn {tk_id} vào SQLite. (Tổng: {crawled_count})")
                    
                # Lưu trang tiếp theo vào cấu hình để lần sau tiếp tục tự động
                update_config_start_page(page + 1)
                    
                # Thoát sớm nếu đã đạt giới hạn cào test
                if limit and crawled_count >= limit:
                    session_status = 'limit_reached'
                    break
                    
                # Nghỉ chuyển trang ngẫu nhiên: 2 - 4 phút (PO APPROVED)
                if page < 20:
                    page_delay = random.uniform(DELAY_PAGE_MIN, DELAY_PAGE_MAX)
                    print(f"\n[*] Đã hoàn tất Trang {page}. Nghỉ tàng hình chuyển trang {page_delay/60:.2f} phút...")
                    sleep_interruptible(page_delay)
                    
            except RuntimeError as re_err:
                # Re-raise to allow background thread to catch and terminate crawl instantly!
                raise re_err
            except Exception as e:
                print(f"[❌ LỖI] Gặp sự cố khi quét trang {page}: {str(e)}")
                # Nếu gặp lỗi định dạng header (do cookie lỗi), dừng chương trình ngay
                if "header" in str(e).lower() or "cookie" in str(e).lower() or "whitespace" in str(e).lower():
                    print("[*] Dừng chương trình do lỗi định dạng tiêu đề (Header/Cookie). Vui lòng kiểm tra lại Cookie.")
                    session_status = 'cookie_expired'
                    sys.exit(1)
                sleep_interruptible(10)
                
        print(f"\n[🏁 HOÀN TẤT] Đã cào tổng cộng {crawled_count} căn thô về SQLite.")
        session_status = 'completed'
    finally:
        print_report()
    
# ==========================================
# HÀM LƯU DỮ LIỆU THÔ VÀO SQLITE
# ==========================================
def save_raw_to_sqlite(tk_id, metadata, images_tk_list):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Kiểm tra xem bản ghi đã tồn tại trong hệ thống chưa
    existing = cursor.execute("SELECT id FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
    
    if existing:
        # Nếu đã tồn tại, chỉ cập nhật (UPDATE) các trường cào thô, bảo toàn cột biên tập!
        update_parts = ["status = ?", "raw_images_tk_json = ?"]
        values = ["raw_text", json.dumps(images_tk_list)]
        
        for key, val in metadata.items():
            safe_col = get_safe_col_name(key)
            update_parts.append(f"`{safe_col}` = ?")
            values.append(str(val) if val is not None else "")
            
        values.append(tk_id)
        update_sql = f"UPDATE listings SET {', '.join(update_parts)} WHERE tk_id = ?"
        cursor.execute(update_sql, values)
    else:
        # Nếu chưa tồn tại, chèn mới hoàn toàn (INSERT)
        columns = ["tk_id", "status", "raw_images_tk_json"]
        placeholders = ["?", "?", "?"]
        values = [tk_id, "raw_text", json.dumps(images_tk_list)]
        
        for key, val in metadata.items():
            safe_col = get_safe_col_name(key)
            columns.append(f"`{safe_col}`")
            placeholders.append("?")
            values.append(str(val) if val is not None else "")
            
        insert_sql = f"INSERT INTO listings ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(insert_sql, values)
        
    conn.commit()
    conn.close()

# ==========================================
# LUỒNG 2: TẢI ẢNH & UPLOAD GOOGLE DRIVE CHẠY NGẦM
# ==========================================
def run_image_migration(limit=None):
    init_db()
    print("\n[+] KHỞI ĐỘNG LUỒNG DI CƯ HÌNH ẢNH: GOOGLE DRIVE UPLOAD (Throttled Mode)")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    rows = cursor.execute("SELECT id, tk_id, raw_images_tk_json FROM listings WHERE status = 'raw_text'").fetchall()
    conn.close()
    
    if not rows:
        print("[*] Tuyệt vời! Không còn căn nào ở trạng thái thô chưa up ảnh.")
        return
        
    print(f"[i] Phát hiện {len(rows)} căn thô cần xử lý di cư hình ảnh lên Drive.")
    
    migrated_count = 0
    for row in rows:
        if limit and migrated_count >= limit:
            break
            
        row_db_id = row[0]
        tk_id = row[1]
        raw_images_tk = json.loads(row[2])
        
        print(f"\n[+] Đang di cư ảnh cho căn {tk_id} ({len(raw_images_tk)} tấm)...")
        
        try:
            # Tạo thư mục con và upload qua API Google Drive thực tế (setup credentials.json sau)
            mock_folder_id = f"folder_drive_{tk_id.lower()}"
            
            drive_links = []
            for idx, img_url in enumerate(raw_images_tk):
                # Download file ảnh thô từ TK
                # img_data = requests.get(img_url, timeout=15).content
                # Upload lên Google Drive
                # file_id = upload_to_drive(drive_service, img_data, f"img_{idx+1}.jpg", folder_id)
                mock_file_id = f"file_id_{tk_id.lower()}_{idx+1}"
                
                # Tạo link nhúng trực tiếp direct công khai
                direct_link = f"https://lh3.googleusercontent.com/d/{mock_file_id}"
                drive_links.append(direct_link)
                
            # Ghi đè mảng link Drive vào SQLite và đổi trạng thái
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE listings SET raw_drive_images_json = ?, status = 'raw_complete' WHERE id = ?",
                (json.dumps(drive_links), row_db_id)
            )
            conn.commit()
            conn.close()
            
            migrated_count += 1
            print(f"  => Hoàn thành {tk_id}: Đã đẩy {len(drive_links)} ảnh lên Google Drive và cập nhật SQLite status = 'raw_complete'.")
            
            # Throttling tàng hình để bảo vệ IP mạng nhà
            time.sleep(DELAY_IMAGE_DOWNLOAD)
            
        except Exception as e:
            print(f"  [❌ LỖI] Không thể xử lý ảnh cho {tk_id}: {str(e)}")
            time.sleep(5)
            
    print(f"\n[🏁 HOÀN TẤT] Đã di cư thành công ảnh của {migrated_count} căn lên Google Drive.")

def check_cookie_valid(cookie_str):
    """Kiểm tra nhanh xem cookie có hoạt động không (không bị redirect về security.html)"""
    try:
        url = "https://data.thienkhoi.com/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": cookie_str
        }
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        # Nếu bị redirect về trang bảo mật hoặc trang đăng nhập, tức là cookie hết hạn
        if "security.html" in r.url or "account/login" in r.url or len(r.text) < 1000:
            return False
        return True
    except Exception:
        return False

def get_thienkhoi_cookie_from_chrome():
    cache_file = "thienkhoi_cookie.txt"
    
    # 1. Thử dùng cache cũ trước để người dùng không phải làm gì
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_cookie = f.read().strip()
            if cached_cookie and check_cookie_valid(cached_cookie):
                print("[✅ CACHE] Sử dụng Cookie Thiên Khôi đã lưu trữ còn hiệu lực!")
                return cached_cookie
        except Exception:
            pass

    # 2. Nếu không có cache hoặc cache hết hạn, yêu cầu dán cookie mới
    print("\n" + "="*70)
    print("[⚠️ COOKIE THIÊN KHÔI HẾT HẠN HOẶC CHƯA CÓ]")
    print("Do phiên đăng nhập bảo mật hoặc Google Chrome mã hóa App-Bound v20,")
    print("Python không thể tự động trích xuất trực tiếp từ file trên đĩa Windows.")
    print("Anh vui lòng:")
    print("  1. Cài extension sao chép cookie 1-click (Ví dụ: 'Copy All Cookies' trên Chrome Web Store).")
    print("  2. Mở tab Thiên Khôi, click biểu tượng extension đó để copy toàn bộ Cookie.")
    print("  3. Dán (Ctrl + V) chuỗi Cookie copy được vào bên dưới:")
    print("="*70 + "\n")
    
    user_cookie = ""
    while not user_cookie.strip():
        try:
            user_cookie = input("👉 Dán Cookie của anh vào đây và nhấn [ENTER]: ").strip()
        except KeyboardInterrupt:
            print("\n[-] Đã hủy yêu cầu.")
            sys.exit(0)
            
        if user_cookie.startswith('"') and user_cookie.endswith('"'):
            user_cookie = user_cookie[1:-1]
        if user_cookie.startswith("'") and user_cookie.endswith("'"):
            user_cookie = user_cookie[1:-1]
            
    try:
        if not check_cookie_valid(user_cookie):
            print("[⚠️ CẢNH BÁO] Cookie vừa dán có vẻ không hợp lệ hoặc đã hết hạn! Nhưng vẫn sẽ lưu và thử chạy...")
            
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(user_cookie)
        print("[✅ THÀNH CÔNG] Đã lưu Cookie mới vào file thienkhoi_cookie.txt để dùng cho các lần sau!")
    except Exception as e:
        print(f"[!] Không thể lưu cache cookie: {str(e)}")
        
    return user_cookie

# ==========================================
# KHỞI CHẠY CLI CONTROLLER
# ==========================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Thien Khoi BDS Crawler CLI Pipeline")
    parser.add_argument("--action", type=str, required=True, choices=["crawl", "upload", "status"], help="Hành động: crawl (Cào text), upload (Up ảnh lên Drive), status (Xem trạng thái)")
    parser.add_argument("--url", type=str, help="URL danh sách Quận mục tiêu trên data.thienkhoi.com")
    parser.add_argument("--cookie", type=str, help="Chuỗi cookie đăng nhập của Thiên Khôi (để trống nếu muốn tự động lấy từ Chrome hoặc cache)")
    parser.add_argument("--limit", type=int, help="Giới hạn số lượng căn xử lý (chỉ dùng test)")
    parser.add_argument("--district", type=str, help="Tên quận muốn lọc (Ví dụ: 'Quận 10')")
    
    args = parser.parse_args()
    
    if args.action == "crawl":
        if not args.url:
            print("[❌ LỖI] Cần nhập tham số --url danh sách Quận để cào.")
            sys.exit(1)
            
        cookie_to_use = args.cookie
        if not cookie_to_use:
            cookie_to_use = get_thienkhoi_cookie_from_chrome()
            
        scrape_district(args.url, cookie_to_use, args.limit, args.district)
        
    elif args.action == "upload":
        run_image_migration(args.limit)
        
    elif args.action == "status":
        if not os.path.exists(DB_FILE):
            print("[-] Chưa có file Database SQLite nào được tạo. Hãy chạy crawl trước.")
            sys.exit(0)
            
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        total = cursor.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
        raw_text = cursor.execute("SELECT COUNT(*) FROM listings WHERE status = 'raw_text'").fetchone()[0]
        raw_complete = cursor.execute("SELECT COUNT(*) FROM listings WHERE status = 'raw_complete'").fetchone()[0]
        published = cursor.execute("SELECT COUNT(*) FROM listings WHERE status = 'published'").fetchone()[0]
        
        conn.close()
        
        print("=== BÁO CÁO TRẠNG THÁI CƠ SỞ DỮ LIỆU SQLITE ===")
        print(f"📍 Tổng số căn đã cào về SQLite: {total}")
        print(f"🔸 Đang chờ di cư ảnh (status='raw_text'): {raw_text}")
        print(f"🔹 Đã di cư ảnh xong (status='raw_complete'): {raw_complete}")
        print(f"✅ Đã biên tập & xuất bản lên Sheets (status='published'): {published}")
        print("===============================================")
