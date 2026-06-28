import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect("raw_archive.db")
c = conn.cursor()

rows = c.execute("SELECT Ma_Hang, System_ID, Ngo_So_nha, Duong, Ma_Khang_Ngo_ID FROM listings").fetchall()
print(f"Total rows in SQLite listings table: {len(rows)}")

for idx, r in enumerate(rows, start=1):
    print(f"{idx:02d}. Ma_Hang='{r[0]}' | Sys_ID='{r[1]}' | Address='{r[2]} {r[3]}' | Ma_KN='{r[4]}'")

conn.close()
