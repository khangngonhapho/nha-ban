import sqlite3
import sys

# Redirect stdout to a file with utf-8 encoding
sys.stdout = open("scratch/fast_search_output.txt", "w", encoding="utf-8")

db_path = "raw_archive.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(listings);")
    cols = [c[1] for c in cursor.fetchall()]
    print("listings columns:", cols)
    
    # Search for "270.93.16" in table listings
    for col in cols:
        cursor.execute(f"SELECT * FROM listings WHERE `{col}` LIKE '%270.93.16%';")
        rows = cursor.fetchall()
        if rows:
            print(f"Match found in listings.{col}:")
            for r in rows:
                print(dict(zip(cols, r)))
except Exception as e:
    print("Error querying listings table:", e)

# Also check other tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]
print("All tables:", tables)

conn.close()
sys.stdout.close()
