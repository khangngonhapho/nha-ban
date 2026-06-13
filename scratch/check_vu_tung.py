import sys
import sqlite3
import json

# Force UTF-8 encoding for stdout
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

db_file = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
conn = sqlite3.connect(db_file)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Query listings
rows = cursor.execute("SELECT tk_id, Ngo_So_nha, Duong, Phuong, Quan, status, raw_images_tk_json, raw_drive_images_json, Last_Sync FROM listings WHERE Ngo_So_nha LIKE '%17%' AND Duong LIKE '%Vũ Tùng%'").fetchall()

print(f"Tìm thấy {len(rows)} căn khớp:")
for idx, r in enumerate(rows):
    print(f"\n--- Căn {idx+1} ---")
    r_dict = dict(r)
    for k, v in r_dict.items():
        if k in ["raw_images_tk_json", "raw_drive_images_json"]:
            try:
                urls = json.loads(v) if v else []
                print(f"{k}: {len(urls)} ảnh - {urls[:2]}...")
            except:
                print(f"{k}: Lỗi parse - {v[:100]}")
        else:
            print(f"{k}: {v}")

conn.close()
