import sqlite3
import json

conn = sqlite3.connect("raw_archive.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

rows = cursor.execute("SELECT Ma_Hang, raw_json_full, Last_Crawl FROM listings WHERE raw_json_full IS NOT NULL LIMIT 10").fetchall()
for i, row in enumerate(rows):
    d = dict(row)
    ma_hang = d.get("Ma_Hàng") or d.get("Ma_Hang")
    raw_json = d.get("raw_json_full")
    try:
        raw_data = json.loads(raw_json)
        print(f"{i+1}. Mã Hàng: {ma_hang}")
        print(f"   listedAt:        {raw_data.get('listedAt')}")
        print(f"   updatedAt:       {raw_data.get('updatedAt')}")
        print(f"   createdAt:       {raw_data.get('createdAt')}")
        print(f"   createdAtSigned: {raw_data.get('createdAtSigned')}")
        print(f"   Last_Crawl:      {d.get('Last_Crawl')}")
        print("-" * 40)
    except Exception as e:
        print(f"Error parsing row: {e}")

conn.close()
