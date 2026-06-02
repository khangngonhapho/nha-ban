import sqlite3
import json

conn = sqlite3.connect("raw_archive.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

try:
    rows = cursor.execute("SELECT Ma_Hang, Gia_chao, Gia_Public, Last_Crawl FROM listings ORDER BY rowid DESC LIMIT 10").fetchall()
    data = [dict(r) for r in rows]
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
