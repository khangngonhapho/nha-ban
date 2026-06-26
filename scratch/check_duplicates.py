import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for db in ['raw_archive.db', 'Backup DB/raw_archiveJun25.db']:
    if os.path.exists(db):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in c.fetchall()]
        if 'listings' in tables:
            print(f"=== DB: {db} ===")
            c.execute("SELECT tk_id, Ma_Khang_Ngo_ID, Ngo_So_nha, Duong, raw_images_tk_json FROM listings WHERE Ma_Khang_Ngo_ID IN ('AWACICHIHVS', 'MWOOIKPN')")
            rows = c.fetchall()
            for r in rows:
                print(f"  tk_id: {r[0]}")
                print(f"  Ma_Khang_Ngo_ID: {r[1]}")
                print(f"  Address: {r[2]} {r[3]}")
                print(f"  raw_images_tk_json: {str(r[4])[:150]}...")
        conn.close()
