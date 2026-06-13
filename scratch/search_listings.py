import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
conn = sqlite3.connect(db_file)
c = conn.cursor()

print("--- SEARCH BY STREET ---")
rows = c.execute("SELECT tk_id, Gia_chao, Duong, Ma_Khang_Ngo_ID, System_ID FROM listings WHERE Duong LIKE '%Quang Diệu%' OR Duong LIKE '%quang diệu%'").fetchall()
for r in rows:
    print(r)

print("--- SEARCH BY MA_KHANG_NGO_ID ---")
rows = c.execute("SELECT tk_id, Gia_chao, Duong, Ma_Khang_Ngo_ID, System_ID FROM listings WHERE UPPER(Ma_Khang_Ngo_ID) = 'AWOIZTIDQT' OR UPPER(System_ID) = 'SYS-MP752STS-B3'").fetchall()
for r in rows:
    print(r)

print("\n--- SEARCH BY PRICE 8.75 ---")
rows = c.execute("SELECT tk_id, Gia_chao, Duong, Ma_Khang_Ngo_ID, System_ID FROM listings WHERE Gia_chao LIKE '8,75%' OR Gia_chao LIKE '8.75%'").fetchall()
for r in rows:
    print(r)

conn.close()
