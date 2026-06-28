import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect("raw_archive.db")
c = conn.cursor()

tables = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("=== Tables in raw_archive.db ===")
for t in tables:
    t_name = t[0]
    count = c.execute(f"SELECT COUNT(*) FROM `{t_name}`").fetchone()[0]
    print(f"Table '{t_name}': {count} rows")
    
conn.close()
