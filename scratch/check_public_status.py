import sqlite3
import os
import sys

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    print("Distinct values in Trang_thai_Public:")
    try:
        rows = c.execute("SELECT Trang_thai_Public, COUNT(*) FROM listings GROUP BY Trang_thai_Public").fetchall()
        for r in rows:
            print(f"  {r[0]}: {r[1]}")
    except Exception as e:
        print(e)
        
    print("\nDistinct values in Duyet_Public:")
    try:
        rows = c.execute("SELECT Duyet_Public, COUNT(*) FROM listings GROUP BY Duyet_Public").fetchall()
        for r in rows:
            print(f"  {r[0]}: {r[1]}")
    except Exception as e:
        print(e)
        
    print("\nDistinct values in Trang_thai:")
    try:
        rows = c.execute("SELECT Trang_thai, COUNT(*) FROM listings GROUP BY Trang_thai").fetchall()
        for r in rows:
            print(f"  {r[0]}: {r[1]}")
    except Exception as e:
        print(e)
        
    # Let's count how many listings are actually live (Duyet_Public = 'TRUE')
    cld_live_images = 0
    cld_columns = [
        "Hinh_Nhan_Dien", "So_do_thua_dat_1", "So_do_thua_dat_2", "So_do_thua_dat_3", "So_do_thua_dat_4", "So_do_thua_dat_5",
        "Hinh_Mat_Tien", "Hinh_Hem_1", "Hinh_Hem_2", "Hinh_Hem_3", "Hinh_Hem_4", "Hinh_Hem_5",
        "Hinh_Hem_6", "Hinh_Hem_7", "Hinh_Hem_8", "Hinh_Hem_9", "Hinh_Hem_10",
        "Anh_1", "Anh_2", "Anh_3", "Anh_4", "Anh_5", "Anh_6", "Anh_7", "Anh_8", "Anh_9", "Anh_10"
    ]
    
    # Check listings with Duyet_Public = 'TRUE'
    c.execute(f"SELECT id, tk_id, {', '.join(cld_columns)} FROM listings WHERE Duyet_Public = 'TRUE'")
    live_rows = c.fetchall()
    print(f"\nLive listings count (Duyet_Public = 'TRUE'): {len(live_rows)}")
    
    live_cld_urls = set()
    for r in live_rows:
        for val in r[2:]:
            if val and "cloudinary.com" in str(val):
                live_cld_urls.add(str(val))
                
    print(f"Total Cloudinary image URLs in live listings: {len(live_cld_urls)}")
    
    conn.close()
else:
    print("DB not found")
