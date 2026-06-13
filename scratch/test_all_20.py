import sqlite3
import requests

db_path = "D:/LHTBrain/01_PROJECTS/raw_archive.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT tk_id, Anh_1 FROM listings WHERE Duyet_Public = 'TRUE' AND Anh_1 LIKE '%cloudinary.com%'")
rows = c.fetchall()

print(f"Testing access to all {len(rows)} pending live Cloudinary images:")
count_200 = 0
count_404 = 0
count_other = 0

for tk_id, url in rows:
    try:
        r = requests.head(url, timeout=10)
        status = r.status_code
        print(f"- {tk_id}: status={status}")
        if status == 200:
            count_200 += 1
        elif status == 404:
            count_404 += 1
        else:
            count_other += 1
    except Exception as e:
        print(f"- {tk_id}: error: {e}")
        count_other += 1
        
print(f"\nSummary: 200 OK={count_200}, 404={count_404}, Other={count_other}")
conn.close()
