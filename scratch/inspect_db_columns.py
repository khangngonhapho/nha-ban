import sqlite3
import os

DB_FILE = "raw_archive.db"
if os.path.exists(DB_FILE):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(listings)")
        cols = cursor.fetchall()
        print("Listings Columns:")
        for c in cols:
            print(f"- {c[1]} ({c[2]})")
        conn.close()
    except Exception as e:
        print("Error:", e)
else:
    print("Database does not exist.")
