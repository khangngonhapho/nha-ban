import os
import sys
import sqlite3
import requests

# Đảm bảo import được các module trong project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from core.business_rules import recover_listing_from_raw_json
from core.config import read_settings

def recover_data():
    backup_db = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive (1).db"
    active_db = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
    cookie_file = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/thienkhoi_cookie.txt"
    
    # 1. Kéo dữ liệu raw_json_full từ backup db (nếu có)
    if os.path.exists(backup_db):
        print(f"[*] Đang phục hồi cột raw_json_full từ {backup_db} sang {active_db}...")
        conn_b = sqlite3.connect(backup_db)
        cursor_b = conn_b.cursor()
        
        try:
            rows_b = cursor_b.execute(
                "SELECT tk_id, raw_json_full FROM listings WHERE raw_json_full IS NOT NULL AND raw_json_full != ''"
            ).fetchall()
            print(f"  - Phát hiện {len(rows_b)} căn chứa raw_json_full trong bản backup.")
            
            conn_a = sqlite3.connect(active_db)
            cursor_a = conn_a.cursor()
            
            copied_count = 0
            for tk_id, raw_json in rows_b:
                exists = cursor_a.execute("SELECT tk_id FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
                if exists:
                    current_raw = cursor_a.execute("SELECT raw_json_full FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
                    if not current_raw or not current_raw[0]:
                        cursor_a.execute("UPDATE listings SET raw_json_full = ? WHERE tk_id = ?", (raw_json, tk_id))
                        copied_count += 1
            conn_a.commit()
            conn_a.close()
            print(f"[+] Đã chép thành công {copied_count} bản ghi raw_json_full từ backup DB.")
        except Exception as e_copy:
            print(f"[⚠️ WARNING] Lỗi khi chép raw_json_full từ backup: {str(e_copy)}")
        finally:
            conn_b.close()
    else:
        print(f"[-] Không tìm thấy file backup tại: {backup_db}. Bỏ qua bước phục hồi từ backup.")

    # 2. Khởi động khôi phục toàn bộ database
    print(f"[*] Đang tải danh sách listings từ CSDL hiện tại...")
    conn = sqlite3.connect(active_db)
    cursor = conn.cursor()
    
    try:
        listings = cursor.execute("SELECT tk_id, raw_json_full FROM listings").fetchall()
    except Exception as e_db:
        print(f"[❌ LỖI] Không thể đọc bảng listings: {str(e_db)}")
        conn.close()
        return
        
    print(f"  - Tổng số căn trong CSDL: {len(listings)}")
    
    cookie = ""
    if os.path.exists(cookie_file):
        try:
            with open(cookie_file, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
        except Exception:
            pass
            
    active_port = 5001
    try:
        cfg = read_settings()
        active_port = cfg.get("port", 5001)
    except Exception:
        pass
        
    success_count = 0
    crawl_fallback_count = 0
    fail_count = 0
    
    for idx, (tk_id, raw_json) in enumerate(listings, 1):
        if not tk_id:
            continue
            
        # Nếu raw_json_full trống -> Chạy Fallback Crawl qua localhost API
        if not raw_json:
            print(f"  [{idx}/{len(listings)}] [{tk_id}] Cảnh báo: raw_json_full trống. Đang gọi API cào bù...")
            if not cookie:
                print(f"  [{idx}/{len(listings)}] [{tk_id}] Thất bại: Thiếu cookie Thiên Khôi.")
                fail_count += 1
                continue
                
            try:
                url = f"http://127.0.0.1:{active_port}/api/listings/{tk_id}/recrawl"
                r_crawl = requests.post(url, json={"cookie": cookie}, timeout=60)
                if r_crawl.status_code == 200:
                    crawl_fallback_count += 1
                    # Tải lại dữ liệu raw_json_full mới cào
                    row_new = cursor.execute("SELECT raw_json_full FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
                    raw_json = row_new[0] if row_new else None
                else:
                    print(f"  [{idx}/{len(listings)}] [{tk_id}] API cào bù trả về lỗi HTTP {r_crawl.status_code}. Vui lòng bật Web Server!")
                    fail_count += 1
                    continue
            except Exception as e_crawl:
                print(f"  [{idx}/{len(listings)}] [{tk_id}] Không thể kết nối Web Server để cào bù: {str(e_crawl)}")
                fail_count += 1
                continue
                
        # Gọi hàm khôi phục
        if raw_json:
            try:
                res = recover_listing_from_raw_json(conn, tk_id, active_table="listings", update_type="all")
                if res:
                    success_count += 1
                    
                    # Đồng bộ lên Google Sheets sau khi khôi phục thành công
                    try:
                        import manager
                        sync_res = manager.execute_publish_listing(tk_id)
                        if sync_res.get("status") == "success":
                            print(f"  [{idx}/{len(listings)}] [{tk_id}] Đồng bộ Google Sheets thành công.")
                        else:
                            print(f"  [{idx}/{len(listings)}] [{tk_id}] Đồng bộ Google Sheets thất bại: {sync_res.get('message')}")
                    except Exception as e_sync:
                        print(f"  [{idx}/{len(listings)}] [{tk_id}] Lỗi ngoại lệ khi đồng bộ Google Sheets: {str(e_sync)}")
                else:
                    print(f"  [{idx}/{len(listings)}] [{tk_id}] Lỗi định dạng JSON thô.")
                    fail_count += 1
            except Exception as e_rec:
                print(f"  [{idx}/{len(listings)}] [{tk_id}] Lỗi khi chạy khôi phục: {str(e_rec)}")
                fail_count += 1
        else:
            fail_count += 1

    conn.close()
    print(f"\n[✅] HOÀN TẤT TIẾN TRÌNH CỨU HỘ:")
    print(f"  - Khôi phục thành công: {success_count}/{len(listings)} căn.")
    print(f"  - Cào bù thành công (Crawl Fallback): {crawl_fallback_count} căn.")
    print(f"  - Thất bại hoặc Bỏ qua: {fail_count} căn.")

if __name__ == "__main__":
    recover_data()
