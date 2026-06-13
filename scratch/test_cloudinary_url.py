import sqlite3
import requests

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT tk_id, Anh_1 FROM listings WHERE Duyet_Public = 'TRUE' AND Anh_1 LIKE '%cloudinary.com%' LIMIT 5")
rows = c.fetchall()

print("Testing access to Cloudinary images:")
for tk_id, url in rows:
    try:
        r = requests.head(url, timeout=10)
        print(f"- {tk_id}: {url[:60]}... status={r.status_code}")
    except Exception as e:
        print(f"- {tk_id}: error: {e}")
        
conn.close()
