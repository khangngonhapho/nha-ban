import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect("raw_archive.db")
c = conn.cursor()

# Search for TKVT84IT in listings
row = c.execute("SELECT * FROM listings WHERE Ma_Hang = ?", ("TKVT84IT",)).fetchone()
if row:
    # Print column names and values
    col_names = [description[0] for description in c.description]
    print("=== Details for TKVT84IT in SQLite ===")
    for name, val in zip(col_names, row):
        if val:
            print(f"  {name}: {val}")
else:
    print("NOT found TKVT84IT in SQLite.")

conn.close()
