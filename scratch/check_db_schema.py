import sqlite3
import os

db_path = "raw_archive.db"
if not os.path.exists(db_path):
    print("raw_archive.db not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get list of tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("Tables in database:", tables)

for table in tables:
    if "listings" in table:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cursor.fetchall()]
        print(f"\nColumns in '{table}':")
        # Print date or time related columns
        date_cols = [c for c in cols if any(x in c.lower() for x in ["date", "time", "crawl", "sync", "create", "update", "ngay", "gio", "niem"])]
        print("Date/Time columns:", date_cols)
        print("First 20 columns:", cols[:20])

conn.close()
