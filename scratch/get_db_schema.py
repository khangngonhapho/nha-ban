import sqlite3
import sys

sys.stdout = open("scratch/db_schema.txt", "w", encoding="utf-8")

db_path = "raw_archive.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]
print("Tables:", tables)

for t in tables:
    print(f"\nSchema for table {t}:")
    cursor.execute(f"PRAGMA table_info({t});")
    for col in cursor.fetchall():
        print(col)

conn.close()
sys.stdout.close()
