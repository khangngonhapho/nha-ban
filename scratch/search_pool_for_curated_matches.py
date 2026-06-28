import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

pool_sid = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"

try:
    gc = gspread.service_account(filename='credentials.json')
    pool_sh = gc.open_by_key(pool_sid)
    pool_sheet = pool_sh.worksheet("Pool")
    pool_data = pool_sheet.get_all_values()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

headers = pool_data[0]

# We want to check if these Ma_Hangs are on the Pool sheet (and at what row)
target_ma_hangs = [
    "TKVT84IT", # New Ma_Hang for Row 8 (TKT-4587) in SQLite
    "TK7UPXZI", # Row 9
    "TK7O6RYX", # Row 10
    "TK2L1LCP", # Row 12
    "TKQK1W9A", # Row 24
    "TKQLMB8Q", # New Ma_Hang for Row 2 (empty Ma_Hang)
    "MHIM4IADD", # New Ma_Hang for Row 11 (empty Ma_Hang)
]

print("=== Searching for Curation IDs on the Pool Sheet ===")
for mh in target_ma_hangs:
    found_rows = []
    # Search in Ma_Hang column (index 0)
    for idx, row in enumerate(pool_data[1:], start=2):
        if row and row[0].strip() == mh:
            found_rows.append((idx, "Mã Hàng"))
            
    # Also search in Mã TK Mới column (let's find index dynamically)
    ma_tk_moi_idx = -1
    for c_idx, h in enumerate(headers):
        if "mã tk mới" in h.lower():
            ma_tk_moi_idx = c_idx
            break
            
    if ma_tk_moi_idx != -1:
        for idx, row in enumerate(pool_data[1:], start=2):
            if len(row) > ma_tk_moi_idx and row[ma_tk_moi_idx].strip() == mh:
                found_rows.append((idx, "Mã TK Mới"))
                
    if found_rows:
        print(f"Ma_Hang '{mh}':")
        for r, col in found_rows:
            print(f"  -> Found at Row {r} in column '{col}'")
    else:
        print(f"Ma_Hang '{mh}': NOT found anywhere on Pool sheet.")
