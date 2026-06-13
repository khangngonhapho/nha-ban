import sqlite3
import os

db_paths = [
    "D:/LHTBrain/01_PROJECTS/raw_archive.db",
    "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive_v2.db",
    "D:/LHTBrain/01_PROJECTS/raw_archive_v2.db",
    "raw_archive_v2.db",
    "raw_archive.db"
]

for db_path in db_paths:
    if not os.path.exists(db_path):
        continue
    print(f"\n=========================================")
    print(f"Checking DB: {db_path}")
    print(f"=========================================")
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        tables = [x[0] for x in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print("Tables:", tables)
        
        for table in tables:
            count = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"Table {table}: {count} records")
            
        if "listings_images" in tables:
            total_images = c.execute("SELECT COUNT(*) FROM listings_images").fetchone()[0]
            cld_count = c.execute("SELECT COUNT(*) FROM listings_images WHERE cloudinary_url IS NOT NULL AND cloudinary_url != ''").fetchone()[0]
            cld_distinct = c.execute("SELECT COUNT(DISTINCT cloudinary_url) FROM listings_images WHERE cloudinary_url IS NOT NULL AND cloudinary_url != ''").fetchone()[0]
            
            print(f"Total image records in listings_images: {total_images}")
            print(f"Image records with Cloudinary URL: {cld_count}")
            print(f"Unique Cloudinary URLs: {cld_distinct}")
            
            # Print sample
            c.execute("SELECT tk_id, image_url, cloudinary_url, role FROM listings_images WHERE cloudinary_url IS NOT NULL AND cloudinary_url != '' LIMIT 5")
            samples = c.fetchall()
            print("\nSamples (tk_id, image_url, cloudinary_url, role):")
            for s in samples:
                print(s)
                
            # Count type of image_url
            c.execute("SELECT image_url FROM listings_images")
            all_urls = [x[0] for x in c.fetchall()]
            local_count = sum(1 for x in all_urls if x and (x.startswith("static/") or os.path.exists(x)))
            http_count = sum(1 for x in all_urls if x and x.startswith("http"))
            print(f"Original image URLs type breakdown:")
            print(f"  Local/relative paths: {local_count}")
            print(f"  HTTP/remote URLs: {http_count}")
            
        if "listings" in tables:
            # Check if there are columns with cloudinary URLs
            c.execute(f"PRAGMA table_info(listings)")
            cols = [col[1] for col in c.fetchall()]
            print("listings table columns:", len(cols))
            
        conn.close()
    except Exception as e:
        print(f"Error checking {db_path}: {e}")

# Check local image directory
static_images_paths = [
    "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/images",
    "./static/images"
]
for sip in static_images_paths:
    if os.path.exists(sip):
        subdirs = os.listdir(sip)
        total_files = sum(len(files) for _, _, files in os.walk(sip))
        print(f"\nStatic images directory ({sip}) exists. Subdirs: {len(subdirs)}, Total files: {total_files}")
    else:
        print(f"\nStatic images directory does not exist at {sip}")
