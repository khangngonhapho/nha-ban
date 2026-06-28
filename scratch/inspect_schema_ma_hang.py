import sqlite3
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('raw_archive.db')
c = conn.cursor()

# Get 5 sample rows where Ma_Hang starting with TK-
rows = c.execute("SELECT id, tk_id, Ma_Hang, Link_Goc, status FROM listings WHERE Ma_Hang LIKE 'TK-%' LIMIT 5").fetchall()

print("=== Samples from Listings ===")
for r in rows:
    print(f"ID: {r[0]}")
    print(f"  tk_id   : {r[1]}")
    print(f"  Ma_Hang : {r[2]}")
    print(f"  Link_Goc: {r[3]}")
    print(f"  status  : {r[4]}")
    print("-" * 40)

conn.close()
