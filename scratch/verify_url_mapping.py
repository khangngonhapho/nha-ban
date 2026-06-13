import sqlite3
import os
import json

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Query one live listing
    c.execute("SELECT tk_id, raw_images_tk_json, Anh_1, Anh_2, Anh_3, So_do_thua_dat_1 FROM listings WHERE Duyet_Public = 'TRUE' LIMIT 1")
    row = c.fetchone()
    if row:
        tk_id, tk_json, anh1, anh2, anh3, sodo1 = row
        print(f"tk_id: {tk_id}")
        try:
            tk_urls = json.loads(tk_json)
            print("\nOriginal URLs from raw_images_tk_json:")
            for idx, u in enumerate(tk_urls):
                print(f"  [{idx}]: {u}")
        except Exception as e:
            print("Error parsing json:", e)
            
        print("\nCloudinary URLs in columns:")
        print(f"  Anh_1: {anh1}")
        print(f"  Anh_2: {anh2}")
        print(f"  Anh_3: {anh3}")
        print(f"  So_do_thua_dat_1: {sodo1}")
    else:
        print("No live listings found")
        
    conn.close()
else:
    print("DB not found")
