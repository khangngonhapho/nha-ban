import sqlite3
import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_file = "raw_archive.db"
backup_db_file = "Backup DB/raw_archive_pre_clean_tk.db"
pool_sid = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"

try:
    gc = gspread.service_account(filename='credentials.json')
    pool_sh = gc.open_by_key(pool_sid)
    pool_sheet = pool_sh.worksheet("Pool")
    pool_data = pool_sheet.get_all_values()
except Exception as e:
    print(f"Error loading sheet: {e}")
    sys.exit(1)

# 1. Find duplicates in Pool sheet
ma_hang_map = {}
duplicates = []
for idx, row in enumerate(pool_data[1:], start=2):
    if not row or len(row) == 0:
        continue
    ma_hang = row[0].strip()
    if ma_hang:
        if ma_hang in ma_hang_map:
            duplicates.append((ma_hang, ma_hang_map[ma_hang], idx))
        else:
            ma_hang_map[ma_hang] = idx

print("=== Duplicates in Pool Sheet ===")
for ma_hang, first_idx, dup_idx in duplicates:
    r1 = pool_data[first_idx - 1]
    r2 = pool_data[dup_idx - 1]
    print(f"Ma_Hang '{ma_hang}' duplicated at Row {first_idx} and Row {dup_idx}")
    print(f"  Row {first_idx}: Address='{r1[6]} {r1[5]}' | Link gốc='{r1[10] if len(r1) > 10 else ''}'")
    print(f"  Row {dup_idx}: Address='{r2[6]} {r2[5]}' | Link gốc='{r2[10] if len(r2) > 10 else ''}'")

# 2. Check the 5 missing Ma_Hangs in backup DB and current DB
missing_ma_hangs = ['TKT-4587', 'TK7UPXZI', 'TK7O6RYX', 'TK2L1LCP', 'TKQK1W9A']

def check_db_for_ma_hangs(db_path, name):
    print(f"\n=== Checking in DB: {name} ({db_path}) ===")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check if table exists
    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings'").fetchall()
    if not tables:
        print("Table 'listings' does not exist.")
        conn.close()
        return
        
    for mh in missing_ma_hangs:
        # Check by Ma_Hang
        row = c.execute("SELECT Ma_Hang, System_ID, Ngo_So_nha, Duong, tk_id, link_goc FROM listings WHERE Ma_Hang = ?", (mh,)).fetchone()
        if row:
            print(f"Found {mh} by Ma_Hang: System_ID='{row[1]}' | Address='{row[2]} {row[3]}' | tk_id='{row[4]}' | Link='{row[5]}'")
        else:
            # Let's search by prefix or similar
            # Wait, is there any listing with the same address?
            # Let's find by system ID from pool if possible
            pass
            
    conn.close()

check_db_for_ma_hangs(db_file, "Current DB")
check_db_for_ma_hangs(backup_db_file, "Backup DB")
