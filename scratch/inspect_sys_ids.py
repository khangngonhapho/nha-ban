import sqlite3
import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_file = "raw_archive.db"
backup_db_file = "Backup DB/raw_archive_pre_clean_tk.db"
pool_sid = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
source_sid = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"

try:
    gc = gspread.service_account(filename='credentials.json')
    pool_sh = gc.open_by_key(pool_sid)
    pool_sheet = pool_sh.worksheet("Pool")
    pool_data = pool_sheet.get_all_values()
    
    source_sh = gc.open_by_key(source_sid)
    source_sheet = source_sh.worksheet("Source")
    source_data = source_sheet.get_all_values()
except Exception as e:
    print(f"Error loading sheets: {e}")
    sys.exit(1)

# List of missing listings from Pool comparison
# Row 8: TKT-4587 | SYS-20263803-400
# Row 9: TK7UPXZI | SYS-20265704-735
# Row 10: TK7O6RYX | SYS-20261304-536
# Row 12: TK2L1LCP | SYS-20260005-110
# Row 24: TKQK1W9A | SYS-20260611-812

missing_info = [
    {"row": 8, "ma_hang": "TKT-4587", "sys_id": "SYS-20263803-400", "addr": "A4 Cư xá Nguyễn Văn Trỗi"},
    {"row": 9, "ma_hang": "TK7UPXZI", "sys_id": "SYS-20265704-735", "addr": "48.17H Hồ Biểu Chánh"},
    {"row": 10, "ma_hang": "TK7O6RYX", "sys_id": "SYS-20261304-536", "addr": "29.30B Đoàn Thị Điểm"},
    {"row": 12, "ma_hang": "TK2L1LCP", "sys_id": "SYS-20260005-110", "addr": "622 - 624 Trường Sa"},
    {"row": 24, "ma_hang": "TKQK1W9A", "sys_id": "SYS-20260611-812", "addr": "28 Phan Tây Hồ"},
]

# 1. Search in Source sheet
print("=== Searching in Source Sheet ===")
source_headers = source_data[1]
sys_id_idx = source_headers.index("System ID") if "System ID" in source_headers else 37
ma_kn_idx = source_headers.index("id") if "id" in source_headers else 3

for info in missing_info:
    sys_id = info["sys_id"]
    found = False
    for r_idx, row in enumerate(source_data[2:], start=3):
        if len(row) > sys_id_idx and row[sys_id_idx].strip() == sys_id:
            found = True
            print(f"Found {sys_id} ({info['ma_hang']}) in Source at Row {r_idx}: id='{row[ma_kn_idx] if len(row) > ma_kn_idx else ''}' | Address='{row[6] if len(row) > 6 else ''} {row[5] if len(row) > 5 else ''}'")
            break
    if not found:
        print(f"NOT found {sys_id} ({info['ma_hang']}) in Source sheet.")

# 2. Search in SQLite databases by System_ID or Link_Goc or Address
def search_db_for_info(db_path, db_name):
    print(f"\n=== Searching in DB: {db_name} ({db_path}) ===")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Check table structure
    tables = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings'").fetchall()
    if not tables:
        print("Table 'listings' does not exist.")
        conn.close()
        return
        
    for info in missing_info:
        sys_id = info["sys_id"]
        # Search by System_ID
        row = c.execute("SELECT Ma_Hang, System_ID, Ngo_So_nha, Duong, Ma_Khang_Ngo_ID, link_goc FROM listings WHERE System_ID = ?", (sys_id,)).fetchone()
        if row:
            print(f"Found Sys_ID '{sys_id}' in listings: Ma_Hang='{row[0]}' | Address='{row[2]} {row[3]}' | Ma_KN='{row[4]}' | Link='{row[5]}'")
        else:
            # Search by Address (using like)
            addr_parts = info["addr"].split()
            # Try to match the house number
            house_num = addr_parts[0] if addr_parts else ""
            res = c.execute("SELECT Ma_Hang, System_ID, Ngo_So_nha, Duong, Ma_Khang_Ngo_ID FROM listings WHERE Ngo_So_nha LIKE ?", (f"%{house_num}%",)).fetchall()
            if res:
                print(f"NOT found Sys_ID '{sys_id}', but found matching house number '{house_num}':")
                for r in res:
                    print(f"  -> Ma_Hang='{r[0]}' | Sys_ID='{r[1]}' | Address='{r[2]} {r[3]}' | Ma_KN='{r[4]}'")
            else:
                print(f"NOT found Sys_ID '{sys_id}' or matching house number '{house_num}'")
    conn.close()

search_db_for_info(db_file, "Current DB")
search_db_for_info(backup_db_file, "Backup DB")

# 3. Analyze Pool sheet rows count vs unique Ma_Hang
print("\n=== Analyzing Pool Sheet Rows ===")
empty_ma_hang_rows = []
for idx, row in enumerate(pool_data[1:], start=2):
    if not row or len(row) == 0:
        continue
    ma_hang = row[0].strip()
    if not ma_hang:
        sys_id_val = ""
        for c_idx, h in enumerate(pool_data[0]):
            if "system id" in h.lower():
                sys_id_val = row[c_idx] if c_idx < len(row) else ""
                break
        empty_ma_hang_rows.append((idx, sys_id_val, row[6] if len(row) > 6 else ""))

print(f"Rows in Pool with EMPTY Ma_Hang: {len(empty_ma_hang_rows)}")
for idx, sys_id, addr in empty_ma_hang_rows:
    print(f"  Row {idx}: Sys_ID='{sys_id}' | Address='{addr}'")
