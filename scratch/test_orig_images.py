import sqlite3
import requests
import os

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get a few listings with original urls that were uploaded to cloudinary
    c.execute("PRAGMA table_info(listings)")
    cols = [col[1] for col in c.fetchall()]
    
    # We will search listings v2 if it exists, or listings
    # Let's query from listings_images in raw_archive_v2.db since it has both
    v2_db = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive_v2.db"
    
    test_urls = []
    if os.path.exists(v2_db):
        conn2 = sqlite3.connect(v2_db)
        c2 = conn2.cursor()
        c2.execute("SELECT image_url, cloudinary_url FROM listings_images WHERE cloudinary_url IS NOT NULL AND cloudinary_url != '' LIMIT 3")
        test_urls.extend(c2.fetchall())
        conn2.close()
        
    if not test_urls:
        # Fallback to listings in raw_archive.db
        # Find some non-empty image columns
        c.execute("SELECT Anh_1, Anh_2 FROM listings WHERE Anh_1 LIKE '%cloudinary.com%' LIMIT 3")
        # Wait, listings table only stores the Cloudinary URL after it's migrated.
        # But we can look at the raw crawler data: raw_images_tk_json or raw_drive_images_json
        c.execute("SELECT raw_images_tk_json, Anh_1 FROM listings WHERE raw_images_tk_json IS NOT NULL AND raw_images_tk_json != '' LIMIT 3")
        rows = c.fetchall()
        import json
        for r in rows:
            try:
                urls = json.loads(r[0])
                if urls:
                    test_urls.append((urls[0], r[1]))
            except Exception:
                pass
                
    print(f"Test urls to fetch: {len(test_urls)}")
    for orig, cld in test_urls:
        print(f"\nOriginal URL: {orig}")
        print(f"Cloudinary URL: {cld}")
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = requests.head(orig, headers=headers, timeout=5)
            print(f"  Original URL status: {r.status_code}")
            
            r2 = requests.head(cld, headers=headers, timeout=5)
            print(f"  Cloudinary URL status: {r2.status_code}")
        except Exception as e:
            print(f"  Error testing URL: {e}")
            
    conn.close()
else:
    print("DB not found")
