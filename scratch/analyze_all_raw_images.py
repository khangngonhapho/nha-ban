import sqlite3
import os

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    total = c.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
    cld_count = c.execute("SELECT COUNT(*) FROM listings WHERE raw_images_tk_json LIKE '%cloudinary.com%'").fetchone()[0]
    cf_count = c.execute("SELECT COUNT(*) FROM listings WHERE raw_images_tk_json LIKE '%cloudfront.net%' OR raw_images_tk_json LIKE '%thienkhoi.com%'").fetchone()[0]
    other_count = c.execute("SELECT COUNT(*) FROM listings WHERE raw_images_tk_json IS NOT NULL AND raw_images_tk_json != '' AND raw_images_tk_json NOT LIKE '%cloudinary.com%' AND raw_images_tk_json NOT LIKE '%cloudfront.net%' AND raw_images_tk_json NOT LIKE '%thienkhoi.com%'").fetchone()[0]
    
    print(f"Total listings: {total}")
    print(f"raw_images_tk_json containing Cloudinary: {cld_count}")
    print(f"raw_images_tk_json containing CloudFront/Thien Khoi: {cf_count}")
    print(f"raw_images_tk_json other/empty: {other_count}")
    
    conn.close()
else:
    print("DB not found")
