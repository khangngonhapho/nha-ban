import sqlite3
import os

DB_FILE = "raw_archive.db"
if not os.path.exists(DB_FILE):
    print("Database file does not exist!")
else:
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check total rows
        total = cursor.execute("SELECT COUNT(*) FROM listings").fetchone()[0]
        print(f"Total rows in listings: {total}")
        
        # Check by status
        cursor.execute("SELECT status, COUNT(*) FROM listings GROUP BY status")
        rows = cursor.fetchall()
        print("\nRows by status:")
        for r in rows:
            print(f"- {r[0]}: {r[1]}")
            
        conn.close()
    except Exception as e:
        print(f"Error querying database: {e}")
