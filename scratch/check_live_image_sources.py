import sqlite3
import os
import json

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Query all live listings
    c.execute("SELECT tk_id, raw_images_tk_json FROM listings WHERE Duyet_Public = 'TRUE'")
    rows = c.fetchall()
    
    print(f"Total live listings: {len(rows)}")
    cloudinary_count = 0
    cloudfront_count = 0
    other_count = 0
    empty_count = 0
    
    for r in rows:
        tk_id, tk_json = r[0], r[1]
        if not tk_json:
            empty_count += 1
            continue
        try:
            urls = json.loads(tk_json)
            if not urls:
                empty_count += 1
                continue
            first_url = urls[0]
            if "cloudinary.com" in first_url:
                cloudinary_count += 1
            elif "cloudfront.net" in first_url or "thienkhoi.com" in first_url:
                cloudfront_count += 1
            else:
                other_count += 1
        except Exception:
            other_count += 1
            
    print(f"Breakdown of raw_images_tk_json for live listings:")
    print(f"  Contains Cloudinary URLs: {cloudinary_count}")
    print(f"  Contains CloudFront / Thien Khoi URLs: {cloudfront_count}")
    print(f"  Other: {other_count}")
    print(f"  Empty: {empty_count}")
    
    # If they contain Cloudinary URLs, can we reconstruct the original URLs?
    # How are Cloudinary URLs named?
    # Example: https://res.cloudinary.com/deru9p712/image/upload/v1779937063/BDS-KhangNgo/edxm07-mbkf2yty-f4e40e56/invggqg5d7axqzpevfus.jpg
    # Does this match the filename of the Thien Khoi URL?
    # Let's inspect one sample row and print its raw crawled data if there is a backup or log.
    conn.close()
else:
    print("DB not found")
