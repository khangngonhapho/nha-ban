import sqlite3
import json

try:
    conn = sqlite3.connect('raw_archive.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM listings WHERE System_ID LIKE '%MP752%' OR Ma_Khang_Ngo_ID LIKE '%TQD%' OR Noi_dung_chinh LIKE '%Quang Diệu%' OR Noi_dung_chinh LIKE '%Trần Quang Diệu%' OR tk_id LIKE '%fihx7t%';")
    rows = cursor.fetchall()
    
    cursor.execute("PRAGMA table_info(listings);")
    cols = cursor.fetchall()
    col_names = [c[1] for c in cols]
    
    out = open('matching_db_listings.txt', 'w', encoding='utf-8')
    out.write(f"Matches found: {len(rows)}\n\n")
    
    for idx, row in enumerate(rows):
        out.write(f"=== MATCH {idx+1} ===\n")
        for c_idx, col_name in enumerate(col_names):
            val = row[c_idx] if c_idx < len(row) else ""
            out.write(f"{col_name}: {val}\n")
        out.write("\n")
    out.close()
    print("Done! Wrote to matching_db_listings.txt")
except Exception as e:
    print("Error:", e)
