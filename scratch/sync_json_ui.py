#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==================================================
JSON UI MAINTENANCE & BULK SYNC ENGINE
Hỗ trợ vá dữ liệu thô (self-healing) + Trích xuất JSON UI 
và đồng bộ hàng loạt lên Google Sheets.
==================================================
"""

import os
import sys
import json
import sqlite3
import requests
import time
import random
from datetime import datetime

# Ép terminal Windows/các hệ điều hành mã hóa UTF-8 để hiển thị ký tự Tiếng Việt không bị lỗi
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Đưa thư mục gốc dự án vào sys.path để import chéo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pool_lego
import fetcher
import manager

def run_sync(limit=None, add_log_message=None):
    if add_log_message is None:
        def add_log_message(msg):
            print(msg)
            
    add_log_message("[🔄] Bắt đầu tiến trình vá dữ liệu và đồng bộ JSON UI...")
    
    # 1. Đọc cấu hình
    cfg = {}
    config_file = os.path.join(os.path.dirname(__file__), "..", "settings.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
        except Exception as e:
            add_log_message(f"[⚠️ WARNING] Không thể đọc settings.json: {str(e)}")
            
    is_pool2 = cfg.get("active_pool_system") == "Pool2"
    target_table = "listings_v2" if is_pool2 else "listings"
    db_file = pool_lego.get_db_file()
    
    add_log_message(f"Database: {db_file}, Table: {target_table}, Pool: {'Pool2' if is_pool2 else 'Pool1'}")
    
    # 2. Đọc session cookie và kiểm tra hiệu lực
    cookie_path = os.path.join(os.path.dirname(__file__), "..", "thienkhoi_cookie.txt")
    cookie_str = ""
    if os.path.exists(cookie_path):
        try:
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookie_str = f.read().strip()
        except Exception as e:
            add_log_message(f"[⚠️ WARNING] Không thể đọc thienkhoi_cookie.txt: {str(e)}")
            
    has_valid_cookie = False
    if cookie_str:
        if fetcher.check_cookie_valid(cookie_str):
            has_valid_cookie = True
            add_log_message("[✅ Cookie] Session cookie Thiên Khôi hiện tại còn hiệu lực.")
        else:
            add_log_message("[ℹ] Cookie hết hạn. Đang thử tự động refresh token...")
            refreshed = fetcher.try_refresh_tokens(cookie_path)
            if refreshed:
                cookie_str = refreshed
                has_valid_cookie = True
                add_log_message("[✅ Cookie] Đã refresh token thành công.")
            else:
                add_log_message("[⚠️ WARNING] Cookie hết hạn và refresh thất bại. Không thể cào bù các căn thiếu.")
    else:
        add_log_message("[⚠️ WARNING] Không tìm thấy file thienkhoi_cookie.txt. Bỏ qua cào chi tiết.")
        
    # 3. Kết nối CSDL SQLite quét dữ liệu thô
    if not os.path.exists(db_file):
        add_log_message(f"[❌ LỖI] Database local {db_file} không tồn tại.")
        return
        
    conn = sqlite3.connect(db_file, timeout=30.0)
    cursor = conn.cursor()
    
    # Kiểm tra/nâng cấp bảng đảm bảo có các cột cần thiết
    try:
        cursor.execute(f"PRAGMA table_info({target_table})")
        cols = [r[1] for r in cursor.fetchall()]
        if "raw_json_full" not in cols:
            cursor.execute(f"ALTER TABLE {target_table} ADD COLUMN raw_json_full TEXT")
            conn.commit()
            add_log_message("[🛡️ SCHEMA] Đã tạo bổ sung cột 'raw_json_full' trong SQLite.")
        if "JSON_UI" not in cols:
            cursor.execute(f"ALTER TABLE {target_table} ADD COLUMN JSON_UI TEXT")
            conn.commit()
            add_log_message("[🛡️ SCHEMA] Đã tạo bổ sung cột 'JSON_UI' trong SQLite.")
    except Exception as e_schema:
        add_log_message(f"[❌ SCHEMA ERROR] {str(e_schema)}")
        conn.close()
        return
        
    # Đọc danh sách tất cả các căn trong SQLite
    cursor.execute(f"SELECT tk_id, status, raw_json_full FROM {target_table}")
    db_listings = cursor.fetchall()
    
    to_crawl = []
    to_extract_only = []
    
    for tk_id, status, raw_json in db_listings:
        if not raw_json:
            to_crawl.append((tk_id, status))
        else:
            to_extract_only.append((tk_id, status, raw_json))
            
    add_log_message(f"Local database count: {len(db_listings)}")
    add_log_message(f"  - Cần cào bù (thiếu raw_json_full): {len(to_crawl)}")
    add_log_message(f"  - Chỉ cần trích xuất (đã có raw_json_full): {len(to_extract_only)}")
    
    crawl_success = 0
    crawl_failures = 0
    
    # Tiến hành cào bù cho các căn thiếu dữ liệu gốc
    for idx, (tk_id, status) in enumerate(to_crawl):
        if limit and (crawl_success + crawl_failures) >= limit:
            add_log_message(f"[ℹ] Đạt giới hạn xử lý được chỉ định: limit={limit}")
            break
            
        if not has_valid_cookie:
            add_log_message(f"  [-] Bỏ qua cào căn {tk_id} vì không có cookie hợp lệ.")
            continue
            
        add_log_message(f"📦 [{idx+1}/{len(to_crawl)}] Đang cào bù chi tiết cho UUID: {tk_id}...")
        
        # Nghỉ ngắn giữa các request để bảo vệ IP
        time.sleep(random.uniform(1.2, 2.5))
        
        # Lấy token và gửi request
        access_token, _, _ = fetcher.extract_tokens(cookie_str)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {access_token}" if access_token else "",
            "Accept": "application/json",
            "Origin": "https://proptech.thienkhoi.com",
            "Referer": "https://proptech.thienkhoi.com/"
        }
        detail_api_url = f"https://backend.thienkhoi.com/product/v1/property/{tk_id}"
        
        try:
            r = requests.get(detail_api_url, headers=headers, timeout=15)
            # Nếu token hết hạn đột ngột trong khi đang cào, thử refresh 1 lần
            if r.status_code in [401, 403]:
                add_log_message("  [!] Token hết hạn đột xuất. Thử làm mới...")
                refreshed = fetcher.try_refresh_tokens(cookie_path)
                if refreshed:
                    cookie_str = refreshed
                    access_token, _, _ = fetcher.extract_tokens(cookie_str)
                    headers["Authorization"] = f"Bearer {access_token}"
                    r = requests.get(detail_api_url, headers=headers, timeout=15)
                else:
                    has_valid_cookie = False
                    
            if r.status_code == 200:
                detail_json = r.json()
                detail_data = detail_json.get("data") or {}
                if detail_data:
                    raw_json_str = json.dumps(detail_data, ensure_ascii=False)
                    # Trích xuất dữ liệu UI tinh gọn
                    json_ui_dict = pool_lego.extract_json_ui_data(detail_data)
                    json_ui_str = json.dumps(json_ui_dict, ensure_ascii=False)
                    
                    # Cập nhật SQLite
                    new_status = status
                    if status and status.startswith("crawl_failed:"):
                        new_status = "raw_text" # Khôi phục trạng thái nếu cào lại thành công
                        
                    cursor.execute(
                        f"UPDATE {target_table} SET raw_json_full = ?, JSON_UI = ?, status = ? WHERE tk_id = ?",
                        (raw_json_str, json_ui_str, new_status, tk_id)
                    )
                    conn.commit()
                    crawl_success += 1
                else:
                    add_log_message(f"  [⚠️] Data trong API trả về rỗng cho căn {tk_id}")
            elif r.status_code in [404, 400]:
                add_log_message(f"  [❌] Căn {tk_id} đã bị xóa hoặc không tìm thấy trên nguồn (HTTP {r.status_code}).")
                cursor.execute(f"UPDATE {target_table} SET status = 'crawl_failed:deleted' WHERE tk_id = ?", (tk_id,))
                conn.commit()
                crawl_failures += 1
            elif r.status_code in [401, 403]:
                add_log_message(f"  [❌] Cookie hết hạn hoặc sai quyền truy cập (HTTP {r.status_code}).")
                cursor.execute(f"UPDATE {target_table} SET status = 'crawl_failed:cookie_expired' WHERE tk_id = ?", (tk_id,))
                conn.commit()
                crawl_failures += 1
                has_valid_cookie = False
            else:
                add_log_message(f"  [❌] API trả về mã lỗi HTTP {r.status_code} cho căn {tk_id}.")
                cursor.execute(f"UPDATE {target_table} SET status = 'crawl_failed:http_error' WHERE tk_id = ?", (tk_id,))
                conn.commit()
                crawl_failures += 1
        except Exception as e_fetch:
            add_log_message(f"  [❌ LỖI API] Ngoại lệ khi tải {tk_id}: {str(e_fetch)}")
            cursor.execute(f"UPDATE {target_table} SET status = 'crawl_failed:exception' WHERE tk_id = ?", (tk_id,))
            conn.commit()
            crawl_failures += 1
            
    # Trích xuất lại cho các căn đã có sẵn raw_json_full (hữu ích khi đổi cấu hình lọc)
    extract_success = 0
    for tk_id, status, raw_json in to_extract_only:
        try:
            detail_data = json.loads(raw_json)
            json_ui_dict = pool_lego.extract_json_ui_data(detail_data)
            json_ui_str = json.dumps(json_ui_dict, ensure_ascii=False)
            
            cursor.execute(f"UPDATE {target_table} SET JSON_UI = ? WHERE tk_id = ?", (json_ui_str, tk_id))
            extract_success += 1
            if extract_success % 500 == 0:
                conn.commit()
                add_log_message(f"  - Đã trích xuất xong {extract_success} căn...")
        except Exception as e_extract:
            add_log_message(f"  [⚠️ WARNING] Không thể parse raw_json_full cho {tk_id}: {str(e_extract)}")
            
    conn.commit()
    conn.close()
    
    add_log_message(f"[✅ local] Cập nhật SQLite thành công: Cào bù {crawl_success}, Thất bại {crawl_failures}, Trích xuất {extract_success} căn.")
    
    # 4. Đẩy đồng bộ cột JSON_UI lên Google Sheets
    add_log_message("[⚡] Đang kết nối tới Google Sheets API để đồng bộ hàng loạt...")
    
    creds = manager.get_google_credentials()
    sheet_id = cfg.get("sheet_id")
    if not creds or not sheet_id:
        add_log_message("[❌ Sheets] Không thể tải credentials hoặc sheet_id cấu hình. Hủy đồng bộ Sheets.")
        return
        
    try:
        import gspread
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        sheet = None
        try:
            sheet = spreadsheet.worksheet("Pool")
        except Exception:
            sheet = spreadsheet.get_worksheet(0)
            
        # Đọc toàn bộ giá trị dòng trong bảng trực tuyến để lấy số thứ tự dòng tương ứng
        all_rows = sheet.get_all_values()
        add_log_message(f"Đọc thành công {len(all_rows)} dòng từ Google Sheets.")
        if not all_rows:
            add_log_message("[❌ Sheets] Bảng trực tuyến trống.")
            return
            
        headers = all_rows[0]
        # Đảm bảo bảng trực tuyến có ít nhất 94 cột để chứa JSON_UI tại cột CP
        if len(headers) < 94:
            add_log_message(f"[ℹ] Mở rộng số cột của sheet từ {len(headers)} lên 94 cột...")
            sheet.add_cols(94 - len(headers))
            # Đọc lại toàn bộ bảng sau khi resize
            all_rows = sheet.get_all_values()
            headers = all_rows[0]
            
        # Đổi tên cột 94 thành JSON_UI nếu chưa đúng tên
        if len(headers) >= 94:
            if headers[93] != "JSON_UI":
                add_log_message(f"[ℹ] Thiết lập tiêu đề cột 94 (CP) thành 'JSON_UI' (tên cũ: '{headers[93]}')")
                sheet.update(range_name="CP1", values=[["JSON_UI"]], value_input_option='USER_ENTERED')
                headers[93] = "JSON_UI"
                
        # Nạp lại dữ liệu JSON_UI mới nhất vừa cập nhật từ SQLite local để tránh query lặp trong vòng lặp
        conn = sqlite3.connect(db_file, timeout=30.0)
        cursor = conn.cursor()
        ma_hang_to_json_ui = {}
        for row in cursor.execute(f"SELECT Ma_Hang, JSON_UI FROM {target_table}").fetchall():
            if row[0]:
                ma_hang_to_json_ui[row[0].strip()] = row[1] or ""
        conn.close()
        
        # Tạo mảng giá trị cột JSON_UI khớp với từng dòng trên Sheets trực tuyến
        col_values = [["JSON_UI"]] # Row 1 header
        for i in range(1, len(all_rows)):
            row = all_rows[i]
            ma_hang = row[0].strip() if row else ""
            json_val = ma_hang_to_json_ui.get(ma_hang, "")
            col_values.append([json_val])
            
        # Đẩy đồng bộ cột CP hàng loạt
        range_str = f"CP1:CP{len(col_values)}"
        add_log_message(f"Đang đồng bộ cột CP ghi hàng loạt dữ liệu '{range_str}' lên Sheets...")
        sheet.update(range_name=range_str, values=col_values, value_input_option='USER_ENTERED')
        
        add_log_message("[🎉 Pool] Đồng bộ thành công cột JSON_UI lên Pool Sheet!")

        # --- ĐỒNG BỘ TIẾP SANG SOURCE VÀ PUBLIC SHEETS ---
        try:
            add_log_message("[⚡] Đang đồng bộ JSON_UI sang Source và Public sheets...")
            
            # Map System_ID sang JSON_UI từ SQLite
            conn = sqlite3.connect(db_file, timeout=30.0)
            cursor = conn.cursor()
            sys_id_to_json_ui = {}
            for sys_id, json_ui in cursor.execute(f"SELECT System_ID, JSON_UI FROM {target_table}").fetchall():
                if sys_id:
                    sys_id_to_json_ui[sys_id.strip()] = json_ui or ""
            conn.close()
            
            # 1. Đồng bộ lên Source Sheet
            source_sheet_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
            source_ss = client.open_by_key(source_sheet_id)
            source_sheet = source_ss.worksheet("Source")
            source_rows = source_sheet.get_all_values()
            
            headers_row = source_rows[0]
            if len(headers_row) < 47:
                add_log_message(f"  [-] Mở rộng Source Sheet từ {len(headers_row)} lên 47 cột...")
                source_sheet.add_cols(47 - len(headers_row))
                source_rows = source_sheet.get_all_values()
                headers_row = source_rows[0]
                
            source_sheet.update(range_name="AU1:AU2", values=[["JSON_UI"], ["JSON_UI"]], value_input_option='USER_ENTERED')
            
            source_col_vals = [["JSON_UI"], ["JSON_UI"]]
            for i in range(2, len(source_rows)):
                row = source_rows[i]
                sys_id = row[37].strip() if len(row) > 37 else ""
                json_val = sys_id_to_json_ui.get(sys_id, "")
                source_col_vals.append([json_val])
                
            source_range = f"AU1:AU{len(source_col_vals)}"
            add_log_message(f"  [-] Đang ghi cột {source_range} lên Source Sheet...")
            source_sheet.update(range_name=source_range, values=source_col_vals, value_input_option='USER_ENTERED')
            add_log_message("[✅ Source] Đồng bộ JSON_UI sang Source Sheet thành công!")
            
            # 2. Cập nhật Public Sheet
            public_sheet_id = "1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0"
            public_ss = client.open_by_key(public_sheet_id)
            public_sheet = public_ss.get_worksheet(0)
            public_rows = public_sheet.get_all_values()
            
            public_headers = public_rows[0]
            if len(public_headers) < 44:
                add_log_message(f"  [-] Mở rộng Public Sheet từ {len(public_headers)} lên 44 cột...")
                public_sheet.add_cols(44 - len(public_headers))
                public_rows = public_sheet.get_all_values()
                public_headers = public_rows[0]
                
            public_sheet.update(range_name="AR1:AR2", values=[["JSON_UI"], ["JSON_UI"]], value_input_option='USER_ENTERED')
            
            current_a3 = public_sheet.acell("A3", value_render_option='FORMULA').value
            new_a3 = current_a3.replace("Source!D3:AT1000", "Source!D3:AU1000")
            add_log_message(f"  [-] Cập nhật công thức IMPORTRANGE ở cell A3 của Public Sheet...")
            public_sheet.update(range_name="A3", values=[[new_a3]], value_input_option='USER_ENTERED')
            
            add_log_message("[🎉 THÀNH CÔNG] Hoàn tất đồng bộ toàn bộ cột JSON_UI lên cả Pool, Source và Public sheets!")
            
        except Exception as e_sync_others:
            add_log_message(f"[⚠️ WARNING] Lỗi đồng bộ sang Source/Public: {str(e_sync_others)}")
        
    except Exception as e_sheet:
        add_log_message(f"[❌ Sheets LỖI] Sự cố đồng bộ hàng loạt lên Sheets: {str(e_sheet)}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="JSON UI Maintenance Tool")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of crawls")
    args = parser.parse_args()
    
    run_sync(limit=args.limit)
