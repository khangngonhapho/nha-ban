import sqlite3
import gspread
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

db_file = "raw_archive.db"
temp_db_file = "raw_archive_temp_read.db"
pool_sid = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"

# 1. Connect to Google Sheets and delete the 6 rows
try:
    gc = gspread.service_account(filename='credentials.json')
    pool_sh = gc.open_by_key(pool_sid)
    pool_sheet = pool_sh.worksheet("Pool")
except Exception as e:
    print(f"[❌ ERROR] Loading sheet: {e}")
    sys.exit(1)

# Descending order of current row numbers to prevent index shift during deletion
rows_to_delete = [23, 11, 10, 9, 8, 2]

print("=== DELETING 6 ROWS FROM GOOGLE SHEET POOL ===")
for r_idx in rows_to_delete:
    # Double check row details before deletion
    row_val = pool_sheet.row_values(r_idx)
    ma_hang = row_val[0] if row_val else ""
    addr = f"{row_val[6]} {row_val[5]}" if len(row_val) > 6 else ""
    print(f"Deleting Row {r_idx}: Mã Hàng='{ma_hang}' | Address='{addr}'")
    pool_sheet.delete_rows(r_idx)

print("[✅ SUCCESS] Deleted 6 rows from Google Sheet Pool.")

# 2. Delete the 6 listings from SQLite
def delete_from_db(db_path, name):
    if not os.path.exists(db_path):
        return
    print(f"\n=== DELETING FROM DB: {name} ({db_path}) ===")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if table listings exists
    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings'").fetchall()
    if not tables:
        print("  Table 'listings' not found.")
        conn.close()
        return
        
    c.execute("""
        DELETE FROM listings 
        WHERE tk_id IN (
            '0ceb7a3b-206b-422e-8548-5e0f1e7a3310', 
            '19e78de2-069a-4084-92ac-45c2a1649271', 
            '49a99cdb-cb05-47da-b5d5-0d8a3556b697', 
            '3d296527-12f8-4796-b759-c501ca421f6b', 
            '4f92db9e-de71-4df3-91f6-cc198e84d1d3', 
            'TKF0G0W3'
        )
    """)
    deleted_count = c.rowcount
    conn.commit()
    c.execute("VACUUM")
    conn.close()
    print(f"  [✅ SUCCESS] Deleted {deleted_count} rows from listings table and vacuumed.")

delete_from_db(db_file, "Current DB")
delete_from_db(temp_db_file, "Temp DB")

print("\n=== DELETION COMPLETED SUCCESSFULLY ===")
