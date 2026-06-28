import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

source_sid = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"

try:
    gc = gspread.service_account(filename='credentials.json')
    source_sh = gc.open_by_key(source_sid)
    source_sheet = source_sh.worksheet("Source")
    source_data = source_sheet.get_all_values()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

source_headers = source_data[1]
sys_id_idx = source_headers.index("System ID") if "System ID" in source_headers else 37

target_sys_ids = [
    'SYS-20261929-300', # Row 2 (TKQLMB8Q)
    'SYS-20263803-400', # Row 8 (TKT-4587)
    'SYS-20265704-735', # Row 9 (TK7UPXZI)
    'SYS-20261304-536', # Row 10 (TK7O6RYX)
    'SYS-20261929-136', # Row 11 (TKF0G0W3)
    'SYS-20260005-110', # Row 12 (TK2L1LCP)
    'SYS-20260611-812'  # Row 24 (TKQK1W9A)
]

target_ma_hangs = ["TKT-4587", "TK7UPXZI", "TK7O6RYX", "TKF0G0W3", "TK2L1LCP", "TKQK1W9A", "TKQLMB8Q"]

print("=== Scanning Source Sheet for Deleted Listings ===")

# 1. Search by System ID
found_sys_ids = []
for sys_id in target_sys_ids:
    for idx, row in enumerate(source_data[2:], start=3):
        if len(row) > sys_id_idx and row[sys_id_idx].strip() == sys_id:
            found_sys_ids.append((idx, sys_id))
            
if found_sys_ids:
    print("Found matching System IDs:")
    for r, sid in found_sys_ids:
        print(f"  Row {r}: {sid}")
else:
    print("No matching System IDs found.")

# 2. Search by Ma Hàng
# In Source sheet, which column is Ma Hàng?
# Usually column index 0 is "Mã Hàng" or similar? Let's check headers
ma_hang_idx = -1
for idx, h in enumerate(source_headers):
    if "mã" in h.lower() and "hàng" in h.lower():
        ma_hang_idx = idx
        break
        
found_ma_hangs = []
if ma_hang_idx != -1:
    for mh in target_ma_hangs:
        for idx, row in enumerate(source_data[2:], start=3):
            if len(row) > ma_hang_idx and row[ma_hang_idx].strip() == mh:
                found_ma_hangs.append((idx, mh))
                
if found_ma_hangs:
    print("\nFound matching Mã Hàng:")
    for r, mh in found_ma_hangs:
        print(f"  Row {r}: {mh}")
else:
    print("\nNo matching Mã Hàng found.")
    
# 3. Search by Address (Ngõ/Số nhà)
# Let's search by house number to catch any other format
house_nums = ["9.36A", "A4", "48.17H", "29.30B", "12.14", "622", "28"]
found_addresses = []
# Ngo/So nha is usually column 6 (index 6) or similar
so_nha_idx = -1
for idx, h in enumerate(source_headers):
    if "số nhà" in h.lower() or "ngõ" in h.lower():
        so_nha_idx = idx
        break
        
if so_nha_idx != -1:
    for num in house_nums:
        for idx, row in enumerate(source_data[2:], start=3):
            if len(row) > so_nha_idx and num in row[so_nha_idx].strip():
                found_addresses.append((idx, num, row[so_nha_idx]))
                
if found_addresses:
    print("\nFound potentially matching addresses:")
    for r, num, full_val in found_addresses:
        print(f"  Row {r}: query='{num}' | Found='{full_val}' | System ID='{row[sys_id_idx] if len(row) > sys_id_idx else ''}'")
else:
    print("\nNo matching addresses found.")
