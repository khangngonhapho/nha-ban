import sqlite3
import os
import json

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    total = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    has_tk_json = c.execute("SELECT COUNT(*) FROM listings WHERE raw_images_tk_json IS NOT NULL AND raw_images_tk_json != '' AND raw_images_tk_json != '[]'").fetchone()[0]
    
    print(f"Total listings in raw_archive: {total}")
    print(f"Listings with raw_images_tk_json: {has_tk_json}")
    
    # Check sample lengths
    c.execute("SELECT id, tk_id, raw_images_tk_json, Anh_1, Anh_2, Anh_3, Anh_4, Anh_5 FROM listings WHERE raw_images_tk_json IS NOT NULL AND raw_images_tk_json != '' AND raw_images_tk_json != '[]' LIMIT 5")
    rows = c.fetchall()
    
    for r in rows:
        lid, tk_id, tk_json = r[0], r[1], r[2]
        cld_urls = [x for x in r[3:] if x and "cloudinary.com" in x]
        try:
            tk_urls = json.loads(tk_json)
            print(f"Listing ID {tk_id}: original urls count = {len(tk_urls)}, cloudinary urls count in columns (up to 5) = {len(cld_urls)}")
        except Exception as e:
            print(f"Error parsing json for {tk_id}: {e}")
            
    conn.close()
else:
    print("DB not found")
