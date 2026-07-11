import sys
import os
import sqlite3
import requests
import json
import random
import time
from datetime import datetime
from flask import Flask

# Thiết lập project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import manager
import fetcher
import core.db as db_core
from api.routes_crawl import recrawl_single_listing
from api.routes_pool import parse_price_float, parse_db_datetime

def main():
    cookie = ""
    if os.path.exists(manager.COOKIE_FILE):
        try:
            with open(manager.COOKIE_FILE, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
        except Exception:
            pass
            
    if not cookie:
        print("[❌ LỖI] Không tìm thấy Cookie Thiên Khôi tại thienkhoi_cookie.txt.")
        sys.exit(1)
        
    access_token, _, _ = fetcher.extract_tokens(cookie)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://proptech.thienkhoi.com",
        "Referer": "https://proptech.thienkhoi.com/"
    }
    
    # 1. Đọc danh sách các căn đang có trong SQLite
    db_file = db_core.get_db_file()
    listings_table = manager.LISTINGS_TABLE
    
    try:
        conn = sqlite3.connect(db_file, timeout=30.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT tk_id, Gia_chao, Last_Crawl FROM {listings_table} WHERE status IS NULL OR status = '' OR status NOT LIKE 'crawl_failed:%'")
        rows = cursor.fetchall()
        db_map = {r["tk_id"].lower(): {"price": r["Gia_chao"], "updated_at": r["Last_Crawl"]} for r in rows if r["tk_id"]}
        conn.close()
    except Exception as e_db:
        print(f"[❌ LỖI] Không thể đọc SQLite: {str(e_db)}")
        sys.exit(1)
        
    print(f"==================================================")
    print(f"🚀 KHỞI ĐỘNG QUÉT THAY ĐỔI HÀNG LOẠT (DAILY WORKER)")
    print(f"Tổng số căn trong SQLite: {len(db_map)}")
    print(f"Database File: {db_file}")
    print(f"==================================================")
    
    changed_ids = []
    
    # Quét 15 trang danh sách mới nhất để phát hiện thay đổi
    for page in range(1, 16):
        list_api_url = "https://backend.thienkhoi.com/product/v1/property"
        params = {"page": str(page), "limit": "20", "searchBy": "address"}
        
        try:
            r = requests.get(list_api_url, headers=headers, params=params, timeout=20)
            if r.status_code in [401, 403]:
                refreshed_cookie = fetcher.try_refresh_tokens(manager.COOKIE_FILE)
                if refreshed_cookie:
                    cookie = refreshed_cookie
                    _, access_token, _ = fetcher.extract_tokens(cookie)
                    headers["Authorization"] = f"Bearer {access_token}"
                    r = requests.get(list_api_url, headers=headers, params=params, timeout=20)
                else:
                    print("[❌ LỖI] Phiên đăng nhập hết hạn khi quét. Dừng.")
                    break
                    
            if r.status_code != 200:
                print(f"[⚠️ WARNING] Lỗi tải trang danh sách {page}: HTTP {r.status_code}")
                continue
                
            res_json = r.json()
            listings = (res_json.get("data") or {}).get("data", [])
            if not listings:
                break
                
            for item in listings:
                tk_id = item.get("id")
                if not tk_id:
                    continue
                tk_id_lower = tk_id.lower()
                
                # CHỈ xử lý các căn đã tồn tại trong SQLite (ko thêm mới)
                if tk_id_lower not in db_map:
                    continue
                    
                db_item = db_map[tk_id_lower]
                
                # So sánh giá
                card_price = float(item.get("offeringPrice") or 0)
                db_price = parse_price_float(db_item["price"])
                price_changed = abs(card_price - db_price) > 0.01
                
                # So sánh ngày
                card_date_str = item.get("updatedAt") or item.get("createdAt")
                db_date_str = db_item["updated_at"]
                
                card_date = parse_db_datetime(card_date_str)
                db_date = parse_db_datetime(db_date_str)
                date_changed = card_date and db_date and card_date > db_date
                
                if price_changed or date_changed:
                    if tk_id not in changed_ids:
                        changed_ids.append(tk_id)
                        print(f"[!] Phát hiện thay đổi căn {tk_id}:")
                        if price_changed:
                            print(f"    - Giá chào: {db_price} tỷ -> {card_price} tỷ")
                        if date_changed:
                            print(f"    - Ngày cập nhật: {db_date} -> {card_date}")
                        
        except Exception as e_page:
            print(f"[⚠️ WARNING] Lỗi xử lý trang {page}: {str(e_page)}")
            
    if not changed_ids:
        print("[✅ SUCCESS] Đã hoàn tất quét: Không phát hiện thay đổi nào.")
        return
        
    print(f"[🎯] PHÁT HIỆN {len(changed_ids)} CĂN CÓ THAY ĐỔI. BẮT ĐẦU CÀO CẬP NHẬT TRONG APP CONTEXT...")
    
    app = Flask(__name__)
    with app.test_request_context(json={"cookie": cookie}):
        for tk_id in changed_ids:
            delay = random.uniform(2.0, 4.0)
            print(f"Nghỉ tàng hình {delay:.2f}s...")
            time.sleep(delay)
            
            try:
                res_val = recrawl_single_listing(tk_id)
                if isinstance(res_val, tuple):
                    resp, status_code = res_val
                else:
                    resp = res_val
                    status_code = 200
                
                res_data = resp.get_json()
                if status_code == 200:
                    print(f"  [✅ Cập nhật] Cào thành công căn {tk_id}!")
                else:
                    print(f"  [❌ Thất bại] Lỗi cào lại căn {tk_id}: HTTP {status_code} - {res_data}")
            except Exception as e_crawl:
                print(f"  [❌ Thất bại] Lỗi khi cào căn {tk_id}: {str(e_crawl)}")
                
    print("[✅ SUCCESS] Hoàn thành quét và cập nhật hàng loạt!")

if __name__ == "__main__":
    main()
