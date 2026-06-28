import sqlite3
import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

sid = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"

try:
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open_by_key(sid)
    w = sh.worksheet("Source")
    data = w.get_all_values()
except Exception as e:
    print(f"Error loading sheet: {e}")
    sys.exit(1)

if len(data) < 3:
    print("No data rows")
    sys.exit(0)

# Connect to SQLite
conn = sqlite3.connect('raw_archive.db')
c = conn.cursor()

# Load all SQLite rows into a dict for O(1) lookups
print("Loading listings from SQLite...")
db_map = {}
for r in c.execute("SELECT System_ID, Ma_Hang, Link_Goc FROM listings").fetchall():
    sys_id, ma_hang, link_goc = r
    if sys_id:
        db_map[sys_id.strip()] = (ma_hang, link_goc)
conn.close()
print(f"Loaded {len(db_map)} listings from SQLite.")

headers = data[1]
sys_id_idx = headers.index("System ID") if "System ID" in headers else 37
ma_kn_idx = headers.index("id") if "id" in headers else 3

old_count = 0
new_count = 0
not_found_count = 0

print("\n=== Checking Source Sheet Rows against SQLite ===")
for idx, row in enumerate(data[2:], start=3):
    if len(row) <= sys_id_idx:
        continue
    sys_id = row[sys_id_idx].strip()
    ma_kn = row[ma_kn_idx].strip() if len(row) > ma_kn_idx else ""
    
    if not sys_id:
        continue
        
    db_row = db_map.get(sys_id)
    
    if db_row:
        ma_hang, link_goc = db_row
        is_old = False
        if ma_hang and ma_hang.startswith("TK-"):
            is_old = True
        elif link_goc and "data.thienkhoi.com" in link_goc:
            is_old = True
            
        if is_old:
            old_count += 1
            if old_count <= 5:
                print(f"  Row {idx}: KN_ID={ma_kn} | Sys_ID={sys_id} -> Old TK (Ma_Hang={ma_hang}, Link_Goc={link_goc})")
        else:
            new_count += 1
            if new_count <= 5:
                print(f"  Row {idx}: KN_ID={ma_kn} | Sys_ID={sys_id} -> New TK (Ma_Hang={ma_hang}, Link_Goc={link_goc})")
    else:
        not_found_count += 1
        if not_found_count <= 5:
            print(f"  Row {idx}: KN_ID={ma_kn} | Sys_ID={sys_id} -> NOT FOUND in sqlite!")

print(f"\nSummary:")
print(f"  Total records in Source sheet: {len(data) - 2}")
print(f"  Old TK listings in Source: {old_count}")
print(f"  New TK listings in Source: {new_count}")
print(f"  Not found in SQLite: {not_found_count}")
