import sqlite3
import sys

sys.stdout = open("scratch/fast_search_output_v2.txt", "w", encoding="utf-8")

db_path = "raw_archive.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query by Ma_Hang or tk_id or other fields
search_term = "270.93.16"

cursor.execute("PRAGMA table_info(listings);")
cols = [c[1] for c in cursor.fetchall()]

# Let's perform exact or prefix queries instead of LIKE '%...%' across all columns
# to make it run instantly
columns_to_query = ["tk_id", "Ma_Hang", "Ma_Khang_Ngo_ID", "System_ID"]
for col in columns_to_query:
    if col in cols:
        print(f"--- Querying {col} = '{search_term}' ---")
        cursor.execute(f"SELECT * FROM listings WHERE `{col}` = ?;", (search_term,))
        rows = cursor.fetchall()
        for r in rows:
            print(dict(zip(cols, r)))

        print(f"--- Querying {col} LIKE '%{search_term}%' ---")
        cursor.execute(f"SELECT * FROM listings WHERE `{col}` LIKE ?;", (f"%{search_term}%",))
        rows = cursor.fetchall()
        for r in rows:
            print(dict(zip(cols, r)))

conn.close()
sys.stdout.close()
