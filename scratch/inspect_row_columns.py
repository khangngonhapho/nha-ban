import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

tk_id = "36644ec1-c501-45aa-81af-5f9268352d87"
db_path = "Backup DB/raw_archiveJun25.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(listings)")
    cols = [r[1] for r in c.fetchall()]
    c.execute("SELECT * FROM listings WHERE tk_id = ?", (tk_id,))
    row = c.fetchone()
    if row:
        row_dict = dict(zip(cols, row))
        print("=== Non-empty columns in backup listings for 100 Nguyễn Phi Khanh ===")
        for k, v in row_dict.items():
            if v is not None and str(v).strip() != "" and str(v).strip() != "[]":
                print(f"  {k}: {str(v)[:150]}")
    conn.close()
else:
    print("Database not found")
