import sqlite3
import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

sid_source = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"

try:
    gc = gspread.service_account(filename='credentials.json')
    sh = gc.open_by_key(sid_source)
    w = sh.worksheet("Source")
    data = w.get_all_values()
except Exception as e:
    print(f"Error loading sheets: {e}")
    sys.exit(1)

# Find row 164
headers = data[1]
row_164 = data[163] # row 164 is index 163

print("=== Source Row 164 Details ===")
for i, val in enumerate(row_164):
    if val:
        print(f"  Col {i} ('{headers[i]}'): {val}")

# Query SQLite
conn = sqlite3.connect('raw_archive.db')
c = conn.cursor()

db_row = c.execute("SELECT Ngo_So_nha, Duong, Quan, Ma_Khang_Ngo_ID, System_ID, Ma_Hang, Link_Goc FROM listings WHERE System_ID = 'SYS-20264021-712'").fetchone()

print("\n=== SQLite Row Details for SYS-20264021-712 ===")
if db_row:
    print(f"  Ngo_So_nha     : {db_row[0]}")
    print(f"  Duong          : {db_row[1]}")
    print(f"  Quan           : {db_row[2]}")
    print(f"  Ma_Khang_Ngo_ID: {db_row[3]}")
    print(f"  System_ID      : {db_row[4]}")
    print(f"  Ma_Hang        : {db_row[5]}")
    print(f"  Link_Goc       : {db_row[6]}")
else:
    print("  Not found in SQLite!")

# Let's test gen_id_khang_ngo_python
from pool_lego import gen_id_khang_ngo_python
if db_row:
    test_id = gen_id_khang_ngo_python(db_row[0], db_row[1], db_row[2])
    print(f"\n  gen_id_khang_ngo_python output: {test_id}")

conn.close()
