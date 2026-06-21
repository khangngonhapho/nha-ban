# -*- coding: utf-8 -*-
import sqlite3
import json

db_path = 'raw_archive.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get columns of table listings
cur.execute("PRAGMA table_info(listings)")
columns = [row[1] for row in cur.fetchall()]

# Search for any row containing 212.137 or Nguyễn Văn Nguyễn in any textual column or raw_json_full
rows = []
cur.execute("SELECT * FROM listings LIMIT 1")
first_row = cur.fetchone()
first_row_dict = {}
if first_row:
    for idx, col in enumerate(columns):
        first_row_dict[col] = first_row[idx]

# Let's search for "Nguyễn Văn Nguyễn" or "212.137" in any text columns
# Let's find out which columns have type TEXT
cur.execute("PRAGMA table_info(listings)")
text_cols = [row[1] for row in cur.fetchall() if row[2] == 'TEXT' or row[2] == '']

matched_rows = []
for col in columns:
    try:
        query = f"SELECT tk_id, Ma_Hang, JSON_UI, {col} FROM listings WHERE {col} LIKE '%Nguyễn Văn Nguyễn%' OR {col} LIKE '%212.137%'"
        found = cur.execute(query).fetchall()
        for f in found:
            matched_rows.append({
                "col_matched": col,
                "tk_id": f[0],
                "Ma_Hang": f[1],
                "JSON_UI": f[2],
                "matched_val": f[3]
            })
    except Exception as e:
        pass

output = {
    "columns": columns,
    "first_row_sample": first_row_dict,
    "matched_rows": matched_rows
}

with open('scratch/query_output.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Schema info and search completed. Matches: {len(matched_rows)}")
conn.close()
