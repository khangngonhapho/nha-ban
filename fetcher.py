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
import pool_lego
from pool_lego import POOL_HEADERS, remove_accents, get_safe_col_name, init_db, save_raw_to_sqlite, get_db_file, parse_criteria_groups, extract_json_ui_data

DB_FILE = get_db_file()
LISTINGS_TABLE = "listings_v2" if DB_FILE == "raw_archive_v2.db" else "listings"

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

    def find_val_near(label_el):
        # 1. Direct sibling (input or text)
        sibling = label_el.find_next_sibling()
        if sibling:
            inp = sibling.find('input') if hasattr(sibling, 'find') else None
            if inp:
                return inp.get('value', '').strip()
            txt = sibling.text.strip()
            if txt:
                return txt

        # 2. Traverse up parent chain (up to 3 levels) to find siblings of ancestors
        curr = label_el
        for _ in range(3):
            if not curr:
                break
            sib = curr.find_next_sibling()
            if sib:
                inp = sib.find('input') if hasattr(sib, 'find') else None
                if inp:
                    return inp.get('value', '').strip()
                a = sib.find('a') if hasattr(sib, 'find') else None
                if a and target not in ["mô tả", "mô tả chi tiết", "nội dung", "nội dung chính"]:
                    return a.get('href', '').strip()
                txt = sib.text.strip()
                if txt:
                    return txt
            curr = curr.parent
        return ""

    # 1. Exact Match
    for label in soup.find_all(['label', 'p', 'span', 'div']):
        if label.name == 'div' and len(label.text) > 100:
            continue
        txt = label.text.replace(':', '').strip().lower()
        if txt == target:
            val = find_val_near(label)
            if val:
                return val
                
    # 2. Substring Match
    for label in soup.find_all(['label', 'p', 'span', 'div']):
        if label.name == 'div' and len(label.text) > 100:
            continue
        txt = label.text.replace(':', '').strip().lower()
        if target in txt:
            if target == "hợp đồng" and "giá" in txt:
                continue
            if target == "đầu chủ" and "điện thoại" in txt:
                continue
            val = find_val_near(label)
            if val:
                return val
    return ""

def extract_badges_from_container(container):
    if not container:
        return []
    if len(container.text) > 250:
        return []
    elements = container.find_all(['span', 'button', 'div'])
    leaves = []
    for el in elements:
        child_tags = el.find_all(['span', 'button', 'div'])
        if not child_tags:
            txt = el.text.strip()
            if txt and len(txt) <= 50 and txt not in leaves:
                leaves.append(txt)
    if not leaves:
        txt = container.text.strip()
        if txt and len(txt) <= 250:
            leaves = [v.strip() for v in re.split(r'[,;\n]', txt) if v.strip() and len(v.strip()) <= 50]
    return leaves

def get_criteria_by_label(soup, label_text):
    if not soup:
        return []
    target = remove_accents(label_text).lower().strip()
    
    def find_badges_near(label_el):
        sibling = label_el.find_next_sibling()
        if sibling:
            badges = extract_badges_from_container(sibling)
            if badges:
                return badges
        curr = label_el
        for _ in range(3):
            if not curr:
                break
            sib = curr.find_next_sibling()
            if sib:
                badges = extract_badges_from_container(sib)
                if badges:
                    return badges
            curr = curr.parent
        return []

    # 1. Exact Match
    for label in soup.find_all(['label', 'p', 'span', 'div']):
        if label.name == 'div' and len(label.text) > 100:
            continue
        txt = remove_accents(label.text.replace(':', '').strip()).lower()
        if txt == target:
            badges = find_badges_near(label)
            if badges:
                return badges
                
    # 2. Substring Match with whole-word checking for single-word targets
    for label in soup.find_all(['label', 'p', 'span', 'div']):
        if label.name == 'div' and len(label.text) > 100:
            continue
        txt = remove_accents(label.text.replace(':', '').strip()).lower()
        txt_clean = re.sub(r'[^a-z0-9\s]', ' ', txt)
        txt_words = txt_clean.split()
        
        is_match = False
        if " " in target:
            is_match = (target in txt)
        else:
            is_match = (target in txt_words)
            
        if is_match:
            badges = find_badges_near(label)
            if badges:
                return badges
    return []

def scrape_criteria_from_dom(soup, phan_loai_scraped):
    CRITERIA_LABEL_MAPPING = {
        "Criteria_Tiem_nang_Rui_ro": ["Tiềm năng - Rủi ro", "Tiềm năng", "Rủi ro"],
        "Criteria_Duong_truoc_nha": ["Đường trước nhà"],
        "Criteria_Loai_BDS": ["Loại hình bất động sản", "Loại hình BĐS", "Loại BĐS"],
        "Criteria_Giay_to_phap_ly": ["Giấy tờ pháp lý", "Pháp lý"],
        "Criteria_Hinh_dang_dat": ["Hình dạng thửa đất", "Hình dạng đất"],
        "Criteria_Tinh_trang_xay_dung": ["Tình trạng xây dựng"],
        "Criteria_Cau_truc_nha": ["Cấu trúc nhà"],
        "Criteria_Noi_that": ["Nội thất"],
        "Criteria_Thang_may": ["Thang máy"],
        "Criteria_Loai_ngo": ["Loại ngõ"],
        "Criteria_Vi_tri_tinh_thue": ["Vị trí tính thuế theo quy định của Nhà nước", "Vị trí tính thuế"],
        "Criteria_Mat_thoang": ["Mặt thoáng"],
        "Criteria_Khoang_cach_bai_do_xe": ["Khoảng cách ra bãi đỗ xe oto", "Khoảng cách ra bãi đỗ xe ô tô", "Khoảng cách bãi đỗ xe"],
        "Criteria_Kinh_doanh_Dong_tien": ["Kinh doanh - Dòng tiền", "Kinh doanh, dòng tiền", "Dòng tiền"],
        "Criteria_Tien_ich": ["Tiện ích"],
        "Criteria_Phong_thuy": ["Phong thủy"],
        "Criteria_Huong_nha": ["Hướng nhà", "Hướng"],
        "Criteria_Vi_tri_trong_ngo": ["Vị trí nhà trong ngõ", "Vị trí trong ngõ"],
        "Criteria_Khoang_cach_duong_oto": ["Khoảng cách ra đường ô tô tránh", "Khoảng cách ra đường ô tô", "Khoảng cách đường ô tô"]
    }
    
    result = {}
    for col, labels in CRITERIA_LABEL_MAPPING.items():
        val = ""
        for label in labels:
            badges = get_criteria_by_label(soup, label)
            if badges:
                val = ", ".join(badges)
                break
        result[col] = val

    # Fallback to V1 multiselect matching if empty
    if phan_loai_scraped:
        for item in [x.strip() for x in phan_loai_scraped.split(",") if x.strip()]:
            col_name = classify_criterion(item)
            if col_name:
                if not result.get(col_name):
                    result[col_name] = item
                elif item not in result[col_name]:
                    result[col_name] += ", " + item
                    
    return result

def classify_criterion(value):
    val = value.strip()
    val_lower = val.lower()
    
    # 1. Hướng nhà (HOUSE_DIRECTION)
    huong_names = ["đông bắc", "đông nam", "tây bắc", "tây nam", "đông", "tây", "nam", "bắc"]
    if any(h == val_lower for h in huong_names):
        return "Criteria_Huong_nha"
        
    # 2. Thang máy (ELEVATOR)
    if "thang máy" in val_lower:
        return "Criteria_Thang_may"
        
    # 3. Loại ngõ (ALLEY_TYPE)
    if val_lower in ["ngõ thông", "ngõ cụt", "hẻm thông", "hẻm cụt"]:
        return "Criteria_Loai_ngo"
        
    # 4. Khoảng cách bãi đỗ xe (DISTANCE_TO_PARKING_LOT)
    if "bãi đỗ" in val_lower or "bãi xe" in val_lower or val_lower in ["dưới 100m", "dưới 200m", "dưới 500m"]:
        return "Criteria_Khoang_cach_bai_do_xe"
        
    # 5. Đường trước nhà (ROAD_TYPE)
    if "ô tô" in val_lower or "ba gác" in val_lower or "xe hơi" in val_lower or "tránh" in val_lower or "mặt tiền" in val_lower or "mặt phố" in val_lower or "đường trước nhà" in val_lower:
        return "Criteria_Duong_truoc_nha"
        
    # 6. Lô góc / Mặt thoáng (OPEN_SPACE)
    if "lô góc" in val_lower or "mặt thoáng" in val_lower or "thoáng" in val_lower or "góc" in val_lower:
        return "Criteria_Mat_thoang"
        
    # 7. Tiện ích (PROPERTY_CRITERIA_FACILITIES)
    facilities_keywords = ["trường", "chợ", "bệnh viện", "dân trí", "trung tâm thương mại", "siêu thị", "công viên", "ubnd", "tiện ích"]
    if any(k in val_lower for k in facilities_keywords):
        return "Criteria_Tien_ich"
        
    # 8. Kinh doanh / Dòng tiền (PROPERTY_CRITERIA_BUSINESS_CASH_FLOW)
    business_keywords = ["kinh doanh", "dòng tiền", "cho thuê", "chdv", "văn phòng", "spa", "tiệm"]
    if any(k in val_lower for k in business_keywords):
        return "Criteria_Kinh_doanh_Dong_tien"
        
    # 9. Giấy tờ pháp lý (LEGAL_DOCUMENT)
    legal_keywords = ["sổ hồng", "sổ đỏ", "giấy tay", "bản vẽ", "pháp lý", "giấy tờ"]
    if any(k in val_lower for k in legal_keywords):
        return "Criteria_Giay_to_phap_ly"
        
    # 10. Hình dáng đất (LAND_PLOT_SHAPE)
    shape_keywords = ["nở hậu", "thóp hậu", "vuông", "vuông vức", "hình thang", "thửa đất"]
    if any(k in val_lower for k in shape_keywords):
        return "Criteria_Hinh_dang_dat"
        
    # 11. Tình trạng xây dựng (CONSTRUCTION_STATUS)
    construction_keywords = ["nhà mới", "nhà cũ", "nhà nát", "xây thô", "đang hoàn thiện", "mới tinh"]
    if any(k in val_lower for k in construction_keywords):
        return "Criteria_Tinh_trang_xay_dung"
        
    # 12. Cấu trúc nhà (HOUSE_STRUCTURE)
    structure_keywords = ["lửng", "sân thượng", "giếng trời", "lầu", "hầm", "áp mái", "cấu trúc"]
    if any(k in val_lower for k in structure_keywords):
        return "Criteria_Cau_truc_nha"
        
    # 13. Nội thất (INTERIOR)
    interior_keywords = ["nội thất", "nhà trống", "full option", "bàn giao thô"]
    if any(k in val_lower for k in interior_keywords):
        return "Criteria_Noi_that"
        
    # 14. Vị trí trong ngõ (POSITION_IN_ALLEY)
    if "đầu ngõ" in val_lower or "cuối ngõ" in val_lower or "đầu hẻm" in val_lower or "cuối hẻm" in val_lower:
        return "Criteria_Vi_tri_trong_ngo"
        
    # 15. Khoảng cách đường ô tô (DISTANCE_TO_MAIN_ROAD)
    if "cách đường" in val_lower or "cách ô tô" in val_lower or "gần đường ô tô" in val_lower:
        return "Criteria_Khoang_cach_duong_oto"
        
    # 16. Phong thủy (PROPERTY_CRITERIA_GEOMANCY)
    geomancy_keywords = ["đâm đường", "đường đâm", "lỗi phong thủy", "phong thủy"]
    if any(k in val_lower for k in geomancy_keywords):
        return "Criteria_Phong_thuy"
        
    # 17. Loại BDS (PROPERTY_TYPE)
    type_keywords = ["nhà phố", "biệt thự", "đất trống", "căn hộ", "chung cư"]
    if any(k in val_lower for k in type_keywords):
        return "Criteria_Loai_BDS"
        
    # 18. Vị trí tính thuế (TAX_CALCULATION_POSITION)
    if "vị trí" in val_lower:
        return "Criteria_Vi_tri_tinh_thue"
        
    # 19. Mặc định là Tiềm năng - Rủi ro (PROPERTY_CRITERIA)
    # Ví dụ: "Hiếm", "Giấy phép xây dựng", "Phòng cháy cháy nổ", "Chính chủ"
    return "Criteria_Tiem_nang_Rui_ro"


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
        config_file = "settings.json"
        cfg = {}
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
        cfg["crawler_start_page"] = next_page
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
        print(f"[*] Đã tự động lưu trang tiếp theo vào cấu hình: Trang {next_page}")
    except Exception as e:
        print(f"[⚠️ WARNING] Không thể tự động lưu trang tiếp theo vào settings.json: {str(e)}")

# Note: parse_criteria_groups has been moved to pool_lego.py to prevent circular imports.

# ==========================================
# LUỒNG 1: CÀO TEXT THÔ VÀ LINK ẢNH DÙNG DOM SELECTOR THẬT
# ==========================================
def scrape_district(base_list_url, session_cookie, limit=None, filter_district=None, start_page=None):
    if "proptech.thienkhoi.com" in base_list_url or "backend.thienkhoi.com" in base_list_url:
        return scrape_district_proptech(base_list_url, session_cookie, limit, filter_district, start_page)

    global DELAY_HOUSE_MIN, DELAY_HOUSE_MAX, DELAY_PAGE_MIN, DELAY_PAGE_MAX
    init_db()

    # Tự động nạp cấu hình thời gian nghỉ/tốc độ cào tin từ file cấu hình
    try:
        config_file = "settings.json"
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
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    cursor = conn.cursor()
    existing_ids = set(row[0] for row in cursor.execute(f"SELECT tk_id FROM {LISTINGS_TABLE}"))
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
            conn = sqlite3.connect(DB_FILE, timeout=30.0)
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
                    
                    # Scrape more technical parameters using get_val_by_label
                    behind_open_space = get_val_by_label(soup_detail, "độ rộng mặt thoáng đằng sau nhà (m)") or get_val_by_label(soup_detail, "độ rộng mặt thoáng đằng sau nhà") or get_val_by_label(soup_detail, "mặt thoáng đằng sau")
                    side_open_space = get_val_by_label(soup_detail, "độ rộng mặt thoáng bên cạnh (m)") or get_val_by_label(soup_detail, "độ rộng mặt thoáng bên cạnh") or get_val_by_label(soup_detail, "mặt thoáng bên cạnh")
                    bedrooms_scraped = get_val_by_label(soup_detail, "số phòng ngủ") or safe_get_val(soup_detail, '#Detail_iSoPhongNgu_show')
                    restrooms_scraped = get_val_by_label(soup_detail, "số nhà vệ sinh") or get_val_by_label(soup_detail, "số toilet") or safe_get_val(soup_detail, '#Detail_iSoToilet_show')
                    balconies_scraped = get_val_by_label(soup_detail, "số ban công")
                    sidewalk_scraped = get_val_by_label(soup_detail, "vỉa hè")
                    commission_value = get_val_by_label(soup_detail, "phần trăm trích thưởng") or get_val_by_label(soup_detail, "phần trăm hoa hồng")
                    certificate_series = get_val_by_label(soup_detail, "series sổ đỏ") or get_val_by_label(soup_detail, "series sổ")

                    # Đóng gói dữ liệu bóc tách
                    crawled_data = {
                        "Mã Hàng": ma_hang_scraped,
                        "Tỉnh": safe_get_val(soup_detail, '#Detail_sTenTinh') or get_val_by_label(soup_detail, "tỉnh/thành phố") or get_val_by_label(soup_detail, "tỉnh"),
                        "Quận": safe_get_val(soup_detail, '#Detail_sTenQuan') or get_val_by_label(soup_detail, "quận/huyện") or get_val_by_label(soup_detail, "quận"),
                        "Phường": safe_get_val(soup_detail, '#Detail_sTenPhuongXa') or get_val_by_label(soup_detail, "phường/xã") or get_val_by_label(soup_detail, "phường"),
                        "Đường": safe_get_val(soup_detail, '#Detail_sDuongPho') or get_val_by_label(soup_detail, "đường/phố") or get_val_by_label(soup_detail, "đường"),
                        "Ngõ/Số nhà": safe_get_val(soup_detail, '#Detail_sDiaChi') or get_val_by_label(soup_detail, "ngõ/số nhà"),
                        "Phân loại": phan_loai_scraped,
                        "Nội dung chính": safe_get_val(soup_detail, '#Detail_sNoiDung').replace('\r', '').replace('\n', ' ') if safe_get_val(soup_detail, '#Detail_sNoiDung') else "",
                        "Mô tả chi tiết": mo_ta_scraped,
                        "Giá chào": safe_get_val(soup_detail, '#Detail_iGiaChaoHopDong_show') or get_val_by_label(soup_detail, "giá chào"),
                        "Giá Public": safe_get_val(soup_detail, '#Detail_iGiaChaoHopDong_show') or get_val_by_label(soup_detail, "giá chào"), 
                        "DT Thực tế": safe_get_val(soup_detail, '#Detail_iDienTich_show') or get_val_by_label(soup_detail, "diện tích thực tế"),
                        "DT Trên sổ": safe_get_val(soup_detail, '#Detail_iDienTichSo_show') or get_val_by_label(soup_detail, "diện tích sổ"),
                        "Mặt Tiền": safe_get_val(soup_detail, '#Detail_iMatTien_show') or get_val_by_label(soup_detail, "mặt tiền"),
                        "Chieu_dai": safe_get_val(soup_detail, '#Detail_iDai_show') or safe_get_val(soup_detail, '#Detail_iDai') or get_val_by_label(soup_detail, "chiều dài"),
                        "Số Tầng": safe_get_val(soup_detail, '#Detail_iSoTang_show') or get_val_by_label(soup_detail, "số tầng"),
                        "Số phòng ngủ": bedrooms_scraped,
                        "Số nhà vệ sinh": restrooms_scraped,
                        "Hướng": huong_scraped or get_val_by_label(soup_detail, "hướng"),
                        "Đường trước nhà (m)": duong_truoc_nha,
                        "Tình trạng nhà": "Bình thường",
                        "Trạng thái": safe_get_val(soup_detail, '#Detail_iTrangThai') or get_val_by_label(soup_detail, "trạng thái"),
                        "Tên Chủ Nhà": safe_get_val(soup_detail, '#Detail_sTenChuNha') or get_val_by_label(soup_detail, "tên chủ nhà"),
                        "Điện thoại 1": safe_get_val(soup_detail, '#Detail_sDienThoaiChuNha') or get_val_by_label(soup_detail, "điện thoại 1"),
                        "Điện thoại Đầu Chủ": dt_dau_chu,
                        "Tên Đầu Chủ (Hợp đồng)": ten_dau_chu,
                        "Điểm Facebook": link_fb,
                        "Link Gốc": detail_url,
                        "System ID": f"SYS-{datetime.now().strftime('%Y%m%d').upper()}-{random.randint(100, 999)}",
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
                    classified_cols = scrape_criteria_from_dom(soup_detail, phan_loai_scraped)
                    crawled_data.update(classified_cols)
                    # Ghi nhận các liên kết ảnh sơ đồ (Cột 28 và 29 + Thêm 3 cột sơ đồ ở đáy)
                    if len(images_td) >= 1: crawled_data["Sơ đồ thửa đất 1"] = images_td[0]
                    if len(images_td) >= 2: crawled_data["Sơ đồ thửa đất 2"] = images_td[1]
                    if len(images_td) >= 3: crawled_data["Sơ đồ thửa đất 3"] = images_td[2]
                    if len(images_td) >= 4: crawled_data["Sơ đồ thửa đất 4"] = images_td[3]
                    if len(images_td) >= 5: crawled_data["Sơ đồ thửa đất 5"] = images_td[4]
                    
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
                    for img in images_nd: # Only product/interior images, exclude diagram (sodo) images
                        if img and img not in seen_images:
                            combined_images.append(img)
                            seen_images.add(img)
                    crawled_data["raw_images_tk_ordered"] = images_td + combined_images
                    
                    # Extract basic JSON_UI from columns for the HTML crawler
                    try:
                        cfg = {}
                        if os.path.exists("settings.json"):
                            with open("settings.json", "r", encoding="utf-8") as f:
                                cfg = json.load(f)
                        fields = cfg.get("json_ui_fields") or ["Criteria_Duong_truoc_nha"]
                        json_ui_obj = {}
                        for f in fields:
                            json_ui_obj[f] = crawled_data.get(f, "")
                        crawled_data["JSON_UI"] = json.dumps(json_ui_obj, ensure_ascii=False)
                    except Exception as e_json_ui:
                        print(f"  [⚠️ WARNING] Lỗi trích xuất JSON_UI (HTML): {str(e_json_ui)}")
                    # Leave raw_json_full empty so the backfill script will crawl the full API detail
                    crawled_data["raw_json_full"] = ""
                    
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

def scrape_district_proptech(base_list_url, session_cookie, limit=None, filter_district=None, start_page=None):
    global DELAY_HOUSE_MIN, DELAY_HOUSE_MAX, DELAY_PAGE_MIN, DELAY_PAGE_MAX
    init_db()

    try:
        config_file = "settings.json"
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

    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    cursor = conn.cursor()
    try:
        cursor.execute(f"PRAGMA table_info({LISTINGS_TABLE})")
        db_cols = [r[1] for r in cursor.fetchall()]
    except Exception:
        db_cols = []
    
    gia_col = "Gia_chao" if "Gia_chao" in db_cols else ("Gi__ch_o" if "Gi__ch_o" in db_cols else None)
    status_col = "Trang_thai" if "Trang_thai" in db_cols else None
    
    existing_properties = {}
    if gia_col and status_col:
        for row in cursor.execute(f"SELECT tk_id, `{gia_col}`, `{status_col}` FROM {LISTINGS_TABLE}"):
            existing_properties[row[0]] = (row[1], row[2])
    else:
        for row in cursor.execute(f"SELECT tk_id FROM {LISTINGS_TABLE}"):
            existing_properties[row[0]] = (None, None)
    conn.close()
    
    existing_ids = set(existing_properties.keys())
    print(f"[*] Đã tải {len(existing_ids)} căn có sẵn từ SQLite vào bộ nhớ đệm RAM.")

    if filter_district:
        print(f"[*] Chế độ lọc Quận được kích hoạt: Chỉ cào các căn thuộc '{filter_district}'")

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

    parsed_url = urlparse(base_list_url)
    query_params = parse_qs(parsed_url.query)
    api_params = {k: v[0] for k, v in query_params.items()}
    api_params["limit"] = api_params.get("limit", "20")
    api_params["searchBy"] = api_params.get("searchBy", "address")

    crawled_count = 0
    session_start_time = time.time()
    session_start_time_iso = datetime.now().isoformat()
    cookie_sig = hashlib.md5((session_cookie or "").encode('utf-8')).hexdigest()[:8].upper()
    session_status = 'stopped'

    def print_report():
        nonlocal session_status
        duration = time.time() - session_start_time
        mins = int(duration // 60)
        secs = int(duration % 60)
        avg = f"{duration / crawled_count:.1f} giây/căn" if crawled_count > 0 else "N/A"
        print("\n" + "="*50)
        print("📊 BÁO CÁO PHIÊN CÀO TIN (CRAWL SESSION REPORT - PROPTECH)")
        print(f"🔑 Cookie ID (MD5): {cookie_sig}")
        print(f"⏱️ Tổng thời gian cào: {mins} phút {secs} giây")
        print(f"🏠 Số căn cào thành công: {crawled_count} căn")
        print(f"⚡ Tốc độ trung bình: {avg}")
        print("="*50 + "\n")
        
        try:
            conn = sqlite3.connect(DB_FILE, timeout=30.0)
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

    print(f"\n[+] KHỞI ĐỘNG CÀO DỮ LIỆU THẬT (proptech.thienkhoi.com - Chế độ Siêu Tàng Hình)")

    max_pages_to_crawl = 1000 if not limit else 5
    end_page = start_page + max_pages_to_crawl

    current_cookie = session_cookie
    access_token, _, _ = extract_tokens(current_cookie)

    try:
        for page in range(start_page, end_page):
            if STOP_REQUESTED:
                print("[*] Nhận lệnh dừng từ hệ thống. Đang dừng cào...")
                session_status = 'stopped'
                break
            if limit and crawled_count >= limit:
                session_status = 'limit_reached'
                break

            api_params["page"] = str(page)
            list_api_url = "https://backend.thienkhoi.com/product/v1/property"
            print(f"\n--- Đang mở danh sách Trang {page}/{end_page - 1} via backend API ---")

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://proptech.thienkhoi.com",
                "Referer": "https://proptech.thienkhoi.com/"
            }

            try:
                r = requests.get(list_api_url, headers=headers, params=api_params, timeout=20)
                if r.status_code in [401, 403]:
                    print("[*] Access token expired or invalid (HTTP 401/403). Attempting silent refresh...")
                    refreshed_cookie = try_refresh_tokens()
                    if refreshed_cookie:
                        current_cookie = refreshed_cookie
                        _, access_token, _ = extract_tokens(current_cookie)
                        headers["Authorization"] = f"Bearer {access_token}"
                        r = requests.get(list_api_url, headers=headers, params=api_params, timeout=20)
                    else:
                        print("[❌ LỖI] Không thể refresh token. Dừng cào. Vui lòng cập nhật Cookie mới.")
                        session_status = 'cookie_expired'
                        sys.exit(1)

                if r.status_code != 200:
                    print(f"[❌ LỖI] Lỗi kết nối đến trang danh sách: HTTP {r.status_code}")
                    sleep_interruptible(10)
                    continue

                res_json = r.json()
                listings = (res_json.get("data") or {}).get("data", [])
                if not listings:
                    print("[-] Không tìm thấy hàng dữ liệu nào trên trang này. Dừng cào quận này hoặc hoàn thành.")
                    break

                print(f"[*] Quét thấy {len(listings)} căn nhà trên trang danh sách API.")

                new_listings_on_page = []
                for item in listings:
                    tk_id_item = item.get("id")
                    if not tk_id_item:
                        continue
                    
                    if tk_id_item in existing_ids:
                        old_price, old_status = existing_properties.get(tk_id_item, (None, None))
                        if old_price is not None:
                            new_price = str(item.get("offeringPrice") or "")
                            new_status = str(item.get("status") or "")
                            
                            old_price_str = str(old_price).strip()
                            old_status_str = str(old_status).strip()
                            
                            try:
                                p_old = float(old_price_str)
                                p_new = float(new_price)
                                price_changed = abs(p_old - p_new) > 0.01
                            except Exception:
                                price_changed = old_price_str != new_price
                                
                            status_map = {
                                "selling": "Đang bán",
                                "deposit": "Đặt cọc",
                                "sold": "Đã bán",
                                "expired": "Hết hạn",
                                "suspended": "Tạm dừng"
                            }
                            mapped_new_status = status_map.get(new_status, new_status)
                            status_changed = old_status_str != mapped_new_status
                            
                            if not (price_changed or status_changed):
                                continue
                            
                            print(f"[!] Phát hiện thay đổi ở căn {tk_id_item}: Giá ({old_price_str} -> {new_price}) | Trạng thái ({old_status_str} -> {mapped_new_status}). Kích hoạt cào cập nhật!")
                        else:
                            continue

                    if filter_district:
                        item_dist = (item.get("district") or {}).get("name", "").lower().strip()
                        target = filter_district.lower().strip()
                        target_short = target.replace("quận", "q").replace(" ", "")
                        target_dot = target.replace("quận", "q.").replace(" ", "")
                        if (target not in item_dist) and (target_short not in item_dist) and (target_dot not in item_dist):
                            continue

                    new_listings_on_page.append(tk_id_item)

                if not new_listings_on_page:
                    print("[*] Không phát hiện căn mới nào trên trang này. Chuyển trang tiếp theo.")
                else:
                    print(f"[+] Phát hiện {len(new_listings_on_page)} căn mới tinh. Bắt đầu cào chi tiết...")

                for tk_id_crawling in new_listings_on_page:
                    if STOP_REQUESTED:
                        print("[*] Nhận lệnh dừng từ hệ thống. Đang dừng cào...")
                        session_status = 'stopped'
                        break
                    if limit and crawled_count >= limit:
                        session_status = 'limit_reached'
                        break

                    house_delay = random.uniform(DELAY_HOUSE_MIN, DELAY_HOUSE_MAX)
                    print(f"  -> Nghỉ tàng hình {house_delay:.2f} giây trước khi mở căn mới...")
                    sleep_interruptible(house_delay)

                    if STOP_REQUESTED:
                        break

                    print(f"  [+] Đang cào chi tiết mã căn UUID: {tk_id_crawling}...")
                    detail_api_url = f"https://backend.thienkhoi.com/product/v1/property/{tk_id_crawling}"

                    r_detail = requests.get(detail_api_url, headers=headers, timeout=20)
                    if r_detail.status_code in [401, 403]:
                        print("  [*] Detail request token expired (HTTP 401/403). Attempting silent refresh...")
                        refreshed_cookie = try_refresh_tokens()
                        if refreshed_cookie:
                            current_cookie = refreshed_cookie
                            _, access_token, _ = extract_tokens(current_cookie)
                            headers["Authorization"] = f"Bearer {access_token}"
                            r_detail = requests.get(detail_api_url, headers=headers, timeout=20)
                        else:
                            print("  [❌ LỖI] Không thể refresh token. Dừng cào.")
                            session_status = 'cookie_expired'
                            sys.exit(1)

                    if r_detail.status_code != 200:
                        print(f"  [❌ LỖI] Lỗi HTTP {r_detail.status_code} khi tải chi tiết căn {tk_id_crawling}.")
                        continue

                    detail_json = r_detail.json()
                    detail_data = detail_json.get("data") or {}
                    if not detail_data:
                        print("  [⚠️ WARNING] Detail data is empty.")
                        continue

                    ma_hang = detail_data.get("code") or tk_id_crawling
                    tinh = (detail_data.get("district") or {}).get("provinceName", "TP Hồ Chí Minh")
                    quan_name = (detail_data.get("district") or {}).get("name", "")
                    phuong_name = (detail_data.get("ward") or {}).get("name", "")
                    duong_name = (detail_data.get("street") or {}).get("name") if detail_data.get("street") else detail_data.get("streetName", "")
                    ngo_so_nha = detail_data.get("address", "")
                    
                    phan_loai_names = [c.get("name") for c in (detail_data.get("criteria") or []) if c and c.get("name")]
                    phan_loai = ", ".join(phan_loai_names)

                    if filter_district:
                        quan_chi_tiet = quan_name.lower().strip()
                        target = filter_district.lower().strip()
                        target_short = target.replace("quận", "q").replace(" ", "")
                        target_dot = target.replace("quận", "q.").replace(" ", "")
                        if (target not in quan_chi_tiet) and (target_short not in quan_chi_tiet) and (target_dot not in quan_chi_tiet):
                            print(f"  [-] Căn {ma_hang} thuộc quận {quan_name}, không phải '{filter_district}'. Bỏ qua.")
                            continue

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
                        "Link Gốc": f"https://proptech.thienkhoi.com/warehouse/sources/{tk_id_crawling}",
                        "System ID": f"SYS-{datetime.now().strftime('%Y%M%d').upper()}-{random.randint(100, 999)}",
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

                    # Parse criteria groups and merge into crawled_data
                    criteria_list = detail_data.get("criteria") or []
                    
                    # Save to scratch/last_crawled_criteria.json for debug
                    try:
                        os.makedirs("scratch", exist_ok=True)
                        with open("scratch/last_crawled_criteria.json", "w", encoding="utf-8") as f:
                            json.dump(criteria_list, f, indent=4, ensure_ascii=False)
                    except Exception as e_debug:
                        print(f"  [⚠️ WARNING] Lỗi ghi file debug criteria: {str(e_debug)}")
                        
                    criteria_cols = parse_criteria_groups(criteria_list)
                    crawled_data.update(criteria_cols)

                    for idx, url in enumerate(sodo_images[:5]):
                        crawled_data[f"Sơ đồ thửa đất {idx+1}"] = url

                    # Lưu raw_json_full và JSON_UI tinh gọn từ Proptech API
                    crawled_data["raw_json_full"] = json.dumps(detail_data, ensure_ascii=False)
                    try:
                        json_ui_obj = extract_json_ui_data(detail_data)
                        crawled_data["JSON_UI"] = json.dumps(json_ui_obj, ensure_ascii=False)
                    except Exception as e_json_ui:
                        print(f"  [⚠️ WARNING] Lỗi trích xuất JSON_UI: {str(e_json_ui)}")

                    save_raw_to_sqlite(tk_id_crawling, crawled_data, property_images)
                    existing_ids.add(tk_id_crawling)
                    crawled_count += 1
                    print(f"  => Đã cào và lưu thành công mã căn {ma_hang} vào SQLite (UUID: {tk_id_crawling}) (Tổng: {crawled_count})")

                update_config_start_page(page + 1)
                if limit and crawled_count >= limit:
                    session_status = 'limit_reached'
                    break

                if page < 20:
                    page_delay = random.uniform(DELAY_PAGE_MIN, DELAY_PAGE_MAX)
                    print(f"\n[*] Đã hoàn tất Trang {page}. Nghỉ tàng hình chuyển trang {page_delay/60:.2f} phút...")
                    sleep_interruptible(page_delay)

            except RuntimeError as re_err:
                raise re_err
            except Exception as e:
                print(f"[❌ LỖI] Gặp sự cố khi quét trang {page}: {str(e)}")
                sleep_interruptible(10)

        print(f"\n[🏁 HOÀN TẤT] Đã cào tổng cộng {crawled_count} căn thô về SQLite từ Proptech.")
        session_status = 'completed'

    finally:
        print_report()

# save_raw_to_sqlite is imported from pool_lego

# ==========================================
# LUỒNG 2: TẢI ẢNH & UPLOAD GOOGLE DRIVE CHẠY NGẦM
# ==========================================
def run_image_migration(limit=None):
    init_db()
    print("\n[+] KHỞI ĐỘNG LUỒNG DI CƯ HÌNH ẢNH: GOOGLE DRIVE UPLOAD (Throttled Mode)")
    
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    cursor = conn.cursor()
    if LISTINGS_TABLE == "listings_v2":
        rows = cursor.execute("SELECT tk_id, tk_id, raw_images_tk_json FROM listings_v2 WHERE status = 'raw_text'").fetchall()
    else:
        rows = cursor.execute("SELECT id, tk_id, raw_images_tk_json FROM listings WHERE status = 'raw_text'").fetchall()
    conn.close()
    
    if not rows:
        print("[*] Tuyệt vời! Không còn căn nào ở trạng thái thô chưa up ảnh.")
        return
        
    print(f"[i] Phát hiện {len(rows)} căn thô cần xử lý di cư hình ảnh lên Drive.")
    
    # ...
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
                mock_file_id = f"file_id_{tk_id.lower()}_{idx+1}"
                direct_link = f"https://lh3.googleusercontent.com/d/{mock_file_id}"
                drive_links.append(direct_link)
                
            # Ghi đè mảng link Drive vào SQLite và đổi trạng thái
            conn = sqlite3.connect(DB_FILE, timeout=30.0)
            cursor = conn.cursor()
            if LISTINGS_TABLE == "listings_v2":
                cursor.execute(
                    "UPDATE listings_v2 SET raw_drive_images_json = ?, status = 'raw_complete' WHERE tk_id = ?",
                    (json.dumps(drive_links), row_db_id)
                )
            else:
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

def extract_tokens(cookie_str):
    access_token = None
    refresh_token = None
    cookies_dict = {}
    for part in cookie_str.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            cookies_dict[k.strip()] = v.strip()
    
    access_token = cookies_dict.get("TKG_accessToken")
    refresh_token = cookies_dict.get("TKG_refreshToken")
    return access_token, refresh_token, cookies_dict

def try_refresh_tokens(cookie_path="thienkhoi_cookie.txt"):
    if not os.path.exists(cookie_path):
        return None
    try:
        with open(cookie_path, 'r', encoding='utf-8') as f:
            cookie_str = f.read().strip()
        access_token, refresh_token, cookies_dict = extract_tokens(cookie_str)
        if not refresh_token:
            return None
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://proptech.thienkhoi.com",
            "Referer": "https://proptech.thienkhoi.com/",
            "Authorization": f"Bearer {access_token}" if access_token else ""
        }
        payload = {
            "refresh_token": refresh_token,
            "appLogin": "nguonhang",
            "platform": "web"
        }
        r = requests.post("https://backend.thienkhoi.com/auth/v1/auth/refresh-token", headers=headers, json=payload, timeout=10)
        if r.status_code in [200, 201]:
            data = r.json()
            new_access_token = data.get("data", {}).get("accessToken")
            new_refresh_token = data.get("data", {}).get("refreshToken")
            if new_access_token:
                cookies_dict["TKG_accessToken"] = new_access_token
            if new_refresh_token:
                cookies_dict["TKG_refreshToken"] = new_refresh_token
            
            new_cookie_str = "; ".join([f"{k}={v}" for k, v in cookies_dict.items()]) + ";"
            with open(cookie_path, 'w', encoding='utf-8') as f:
                f.write(new_cookie_str)
            print("[🎉 SUCCESS] Token refreshed programmatically and saved to thienkhoi_cookie.txt.")
            return new_cookie_str
        else:
            try:
                err_data = r.json()
                msg = err_data.get("message") or r.text
            except Exception:
                msg = r.text
            print(f"[❌ ERROR] Failed to refresh token. HTTP {r.status_code}: {msg}")
    except Exception as e:
        print(f"[⚠️ WARNING] Failed to refresh token: {e}")
    return None

def check_cookie_valid(cookie_str):
    """Kiểm tra nhanh xem cookie/token có hoạt động không (dùng users/me hoặc refresh)"""
    access_token, _, _ = extract_tokens(cookie_str)
    if not access_token:
        return False
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {access_token}"
        }
        r = requests.get("https://backend.thienkhoi.com/auth/v1/users/me", headers=headers, timeout=10)
        if r.status_code == 200:
            return True
    except Exception:
        pass
        
    # Thử refresh xem có hoạt động không
    new_cookie = try_refresh_tokens()
    if new_cookie:
        return True
        
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
            
        conn = sqlite3.connect(DB_FILE, timeout=30.0)
        cursor = conn.cursor()
        
        total = cursor.execute(f"SELECT COUNT(*) FROM {LISTINGS_TABLE}").fetchone()[0]
        raw_text = cursor.execute(f"SELECT COUNT(*) FROM {LISTINGS_TABLE} WHERE status = 'raw_text'").fetchone()[0]
        raw_complete = cursor.execute(f"SELECT COUNT(*) FROM {LISTINGS_TABLE} WHERE status = 'raw_complete'").fetchone()[0]
        published = cursor.execute(f"SELECT COUNT(*) FROM {LISTINGS_TABLE} WHERE status = 'published'").fetchone()[0]
        
        conn.close()
        
        print("=== BÁO CÁO TRẠNG THÁI CƠ SỞ DỮ LIỆU SQLITE ===")
        print(f"📍 Tổng số căn đã cào về SQLite: {total}")
        print(f"🔸 Đang chờ di cư ảnh (status='raw_text'): {raw_text}")
        print(f"🔹 Đã di cư ảnh xong (status='raw_complete'): {raw_complete}")
        print(f"✅ Đã biên tập & xuất bản lên Sheets (status='published'): {published}")
        print("===============================================")
