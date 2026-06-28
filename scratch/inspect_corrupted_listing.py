import sqlite3
import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

tk_id = "36644ec1-c501-45aa-81af-5f9268352d87"

db_files = ["raw_archive.db", "raw_archive_v2.db"]
backup_dir = "Backup DB"
if os.path.exists(backup_dir):
    for f in os.listdir(backup_dir):
        if f.endswith(".db"):
            db_files.append(os.path.join(backup_dir, f))

for db in db_files:
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in c.fetchall()]
        for tbl in ['listings', 'listings_v2']:
            if tbl in tables:
                c.execute(f"PRAGMA table_info({tbl})")
                cols = [col[1] for col in c.fetchall()]
                
                # Check if tk_id exists
                c.execute(f"SELECT * FROM {tbl} WHERE tk_id = ?", (tk_id,))
                row = c.fetchone()
                if row:
                    print(f"\n=== Found in {db} -> table {tbl} ===")
                    row_dict = dict(zip(cols, row))
                    print("  Ma_Hang:", row_dict.get("Ma_Hang"))
                    print("  Ngo_So_nha:", row_dict.get("Ngo_So_nha"))
                    print("  Duong:", row_dict.get("Duong"))
                    print("  raw_images_tk_json:", row_dict.get("raw_images_tk_json"))
                    print("  raw_drive_images_json:", row_dict.get("raw_drive_images_json"))
                    print("  raw_sodo_tk_json:", row_dict.get("raw_sodo_tk_json"))
                    print("  Sơ đồ thửa đất 1:", row_dict.get("Sơ đồ thửa đất 1") or row_dict.get("S__đ___th_a___t_1"))
                    print("  Sơ đồ thửa đất 2:", row_dict.get("Sơ đồ thửa đất 2") or row_dict.get("S__đ___th_a___t_2"))
                    print("  raw_json_full exists:", "raw_json_full" in row_dict)
                    if "raw_json_full" in row_dict and row_dict["raw_json_full"]:
                        try:
                            raw_data = json.loads(row_dict["raw_json_full"])
                            print("    raw_json_full media count:", len(raw_data.get("media", [])))
                            if raw_data.get("media"):
                                print("    raw_json_full first media URL:", raw_data["media"][0].get("url")[:80])
                        except Exception as e:
                            print("    Error parsing raw_json_full:", e)
        conn.close()
