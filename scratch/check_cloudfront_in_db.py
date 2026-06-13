import sqlite3
import os

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if there are any mentions of cloudfront or thienkhoi in raw_images_tk_json
    c.execute("SELECT COUNT(*) FROM listings WHERE raw_images_tk_json LIKE '%cloudfront.net%' OR raw_images_tk_json LIKE '%thienkhoi.com%'")
    count_orig = c.fetchone()[0]
    print(f"Listings containing original cloudfront/thienkhoi URLs in raw_images_tk_json: {count_orig}")
    
    # Let's check if there are other columns, like raw_images_tk_json, that contain original urls
    c.execute("SELECT tk_id, raw_images_tk_json FROM listings WHERE raw_images_tk_json LIKE '%cloudfront.net%' OR raw_images_tk_json LIKE '%thienkhoi.com%' LIMIT 3")
    sample_rows = c.fetchall()
    print("\nSamples:")
    for r in sample_rows:
        print(f"  tk_id: {r[0]}, length: {len(r[1]) if r[1] else 0}")
        if r[1]:
            print(f"    {r[1][:200]}...")
            
    conn.close()
else:
    print("DB not found")
