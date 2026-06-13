import sqlite3
import os

db_path = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check R2 URLs in Anh_1
    count = c.execute("SELECT COUNT(*) FROM listings WHERE Anh_1 LIKE '%r2.dev%'").fetchone()[0]
    print(f"Listings with R2 URLs in Anh_1: {count}")
    
    # Check total listings that are live
    total_live = c.execute("SELECT COUNT(*) FROM listings WHERE Duyet_Public = 'TRUE'").fetchone()[0]
    print(f"Total live listings: {total_live}")
    
    conn.close()
else:
    print("DB not found")
