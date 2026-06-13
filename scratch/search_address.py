import sqlite3
import sys

sys.stdout = open("scratch/address_search_output.txt", "w", encoding="utf-8")

db_path = "raw_archive.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(listings);")
cols = [c[1] for c in cursor.fetchall()]

# Search terms
search_terms = ["270.93.16", "270/93/16"]

for term in search_terms:
    print(f"=== Searching for term: '{term}' ===")
    for col in cols:
        cursor.execute(f"SELECT id, tk_id, Ma_Hang, Ma_Khang_Ngo_ID, System_ID, Ngo_So_nha, Duong, Quan, Phuong FROM listings WHERE `{col}` LIKE ?;", (f"%{term}%",))
        rows = cursor.fetchall()
        if rows:
            print(f"Match found in column '{col}':")
            for r in rows:
                print(r)

conn.close()
sys.stdout.close()
