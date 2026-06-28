import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect("raw_archive.db")
c = conn.cursor()

c.execute("PRAGMA table_info(listings)")
cols = c.fetchall()

print("=== Columns in listings table ===")
for col in cols:
    print(f"Col {col[0]}: Name='{col[1]}' | Type='{col[2]}'")
    
conn.close()
