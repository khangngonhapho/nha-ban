import sqlite3
import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_file = "raw_archive.db"
pool_sid = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"

try:
    gc = gspread.service_account(filename='credentials.json')
    pool_sh = gc.open_by_key(pool_sid)
    pool_sheet = pool_sh.worksheet("Pool")
    pool_data = pool_sheet.get_all_values()
except Exception as e:
    print(f"Error loading sheet: {e}")
    sys.exit(1)

# Connect to SQLite
conn = sqlite3.connect(db_file)
c = conn.cursor()

# SQLite listings Ma_Hang
db_listings = c.execute("SELECT Ma_Hang, System_ID, Ngo_So_nha, Duong, tk_id FROM listings").fetchall()
db_ma_hangs = {row[0].strip() for row in db_listings if row[0]}
db_map = {row[0].strip(): row for row in db_listings if row[0]}
conn.close()

print(f"Total listings in SQLite: {len(db_listings)}")
print(f"Total rows in Pool sheet: {len(pool_data)}")

pool_headers = pool_data[0]
print(f"Pool Headers: {pool_headers[:10]}")

pool_ma_hangs = set()
pool_list = []

# Collect Pool Ma_Hangs (excluding header)
for idx, row in enumerate(pool_data[1:], start=2):
    if not row or len(row) == 0:
        continue
    ma_hang = row[0].strip()
    if ma_hang:
        pool_ma_hangs.add(ma_hang)
        pool_list.append((idx, row))

print(f"Unique Ma_Hangs in Pool sheet: {len(pool_ma_hangs)}")

# Find listings in Pool but NOT in SQLite
pool_only = []
for idx, row in pool_list:
    ma_hang = row[0].strip()
    if ma_hang not in db_ma_hangs:
        pool_only.append((idx, row))

print(f"\n=== Listings in Pool Sheet but NOT in SQLite ({len(pool_only)} rows) ===")
for idx, row in pool_only:
    # Print index, Ma_Hang, System_ID (index 73 in Pool? Let's find dynamically)
    sys_id_val = ""
    for c_idx, h in enumerate(pool_headers):
        if "system id" in h.lower():
            sys_id_val = row[c_idx] if c_idx < len(row) else ""
            break
    print(f"  Row {idx} in Pool: Ma_Hang='{row[0]}' | Sys_ID='{sys_id_val}' | Address='{row[6] if len(row) > 6 else ''} {row[5] if len(row) > 5 else ''}'")

# Find listings in SQLite but NOT in Pool
sqlite_only = []
for row in db_listings:
    ma_hang = row[0].strip()
    if ma_hang not in pool_ma_hangs:
        sqlite_only.append(row)

print(f"\n=== Listings in SQLite but NOT in Pool Sheet ({len(sqlite_only)} rows) ===")
for row in sqlite_only:
    print(f"  SQLite: Ma_Hang='{row[0]}' | Sys_ID='{row[1]}' | Address='{row[2]} {row[3]}'")
