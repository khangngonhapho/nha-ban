import sqlite3
import requests
import sys
import shutil
import os
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding='utf-8')

def check_url(row_id, col_name, url):
    try:
        r = requests.head(url, timeout=5)
        return row_id, col_name, url, r.status_code
    except Exception as e:
        return row_id, col_name, url, -1

def main():
    db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
    temp_db = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive_temp_404.db"
    
    try:
        shutil.copy2(db_file, temp_db)
    except Exception as e:
        print(f"Error copying database: {e}")
        return
        
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(listings)")
        cols = [col[1] for col in cursor.fetchall()]
        
        image_cols = [
            "Hinh_Nhan_Dien", "So_do_thua_dat_1", "So_do_thua_dat_2", "So_do_thua_dat_3", "So_do_thua_dat_4", "So_do_thua_dat_5",
            "Hinh_Mat_Tien", "Hinh_Hem_1", "Hinh_Hem_2", "Hinh_Hem_3", "Hinh_Hem_4", "Hinh_Hem_5",
            "Hinh_Hem_6", "Hinh_Hem_7", "Hinh_Hem_8", "Hinh_Hem_9", "Hinh_Hem_10",
            "Anh_1", "Anh_2", "Anh_3", "Anh_4", "Anh_5", "Anh_6", "Anh_7", "Anh_8", "Anh_9", "Anh_10",
            "Anh_11", "Anh_12", "Anh_13", "Anh_14", "Anh_15", "Anh_16", "Anh_17", "Anh_18", "Anh_19", "Anh_20",
            "Anh_21", "Anh_22", "Anh_23", "Anh_24", "Anh_25"
        ]
        active_cols = [c for c in image_cols if c in cols]
        
        cursor.execute(f"SELECT id, tk_id, {', '.join(active_cols)} FROM listings")
        rows = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")
        return
    finally:
        if os.path.exists(temp_db):
            try:
                os.remove(temp_db)
            except Exception:
                pass
                
    cloudinary_urls = []
    for r in rows:
        db_id = r[0]
        tk_id = r[1]
        for col_idx, val in enumerate(r[2:]):
            col_name = active_cols[col_idx]
            if val and "cloudinary.com" in str(val):
                cloudinary_urls.append((tk_id, col_name, str(val)))
                
    print(f"Total Cloudinary cells in DB: {len(cloudinary_urls)}")
    if not cloudinary_urls:
        return
        
    # Check first 50 urls in parallel
    print("Checking HTTP status of first 50 Cloudinary URLs...")
    to_check = cloudinary_urls[:50]
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_url, tk_id, col_name, url) for tk_id, col_name, url in to_check]
        for f in futures:
            tk_id, col_name, url, status = f.result()
            print(f"[{tk_id}] {col_name}: Status {status} | URL: {url[:80]}...")
            
if __name__ == '__main__':
    main()
