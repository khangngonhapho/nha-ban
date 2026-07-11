import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = "raw_archive.db"
if not os.path.exists(db_path):
    print("raw_archive.db not found!")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    print("Tables:", tables)
    
    # Query for Phan Dinh Phung
    if "listings" in tables:
        cursor.execute("SELECT id, Ma_Khang_Ngo_ID, Ngo_So_nha, Duong, status FROM listings WHERE Duong LIKE '%Phan Đình Phùng%' OR Ngo_So_nha LIKE '%Phan%'")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} matching listings:")
        for r in rows:
            print(dict(r))
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
