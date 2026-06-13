import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
conn = sqlite3.connect(db_file)
c = conn.cursor()

print("--- SEARCH BY MA_HANG ---")
rows = c.execute("SELECT tk_id, Ma_Hang, Duong, Ma_Khang_Ngo_ID, System_ID FROM listings WHERE Ma_Hang LIKE '%534B8B%'").fetchall()
for r in rows:
    print(r)

print("\n--- SEARCH BY TK_ID ---")
rows = c.execute("SELECT tk_id, Ma_Hang, Duong, Ma_Khang_Ngo_ID, System_ID FROM listings WHERE tk_id LIKE '%fihx7t%'").fetchall()
for r in rows:
    print(r)

conn.close()
