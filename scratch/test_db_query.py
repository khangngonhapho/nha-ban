import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db')
cursor = conn.cursor()
r = cursor.execute("SELECT tk_id, Ma_Hang, Ma_Khang_Ngo_ID, System_ID FROM listings WHERE Ma_Hang LIKE '%534B8B%' OR tk_id LIKE '%fihx7t%'").fetchall()
print('Partial matches:', r)
conn.close()
