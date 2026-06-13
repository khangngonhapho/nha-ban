import sqlite3
import sys

sys.stdout = open("scratch/kn_code_search_output.txt", "w", encoding="utf-8")

db_path = "raw_archive.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(listings);")
cols = [c[1] for c in cursor.fetchall()]

# Exact search for HWZOICBIMSIPDP in Ma_Khang_Ngo_ID
cursor.execute("SELECT * FROM listings WHERE Ma_Khang_Ngo_ID = ?;", ("HWZOICBIMSIPDP",))
rows = cursor.fetchall()
if rows:
    print("Found exact match in Ma_Khang_Ngo_ID:")
    for r in rows:
         print(dict(zip(cols, r)))
else:
    print("No exact match in Ma_Khang_Ngo_ID.")
    # Search across other columns
    for col in cols:
        cursor.execute(f"SELECT * FROM listings WHERE `{col}` = ?;", ("HWZOICBIMSIPDP",))
        rows = cursor.fetchall()
        if rows:
            print(f"Found match in {col}:")
            for r in rows:
                print(dict(zip(cols, r)))

conn.close()
sys.stdout.close()
