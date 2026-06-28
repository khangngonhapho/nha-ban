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
sys_id_idx = -1
for idx, h in enumerate(headers):
    if "system id" in h.lower():
        sys_id_idx = idx
        break

print("=== Checking Current Pool Sheet Rows ===")
for r_idx, row in enumerate(pool_data[1:], start=2):
    ma_hang = row[0].strip()
    sys_id = row[sys_id_idx].strip() if sys_id_idx != -1 and len(row) > sys_id_idx else ""
    addr = f"{row[6]} {row[5]}" if len(row) > 6 else ""
    
    # Check if target
    if ma_hang in ["TKT-4587", "TK7UPXZI", "TK7O6RYX", "TK2L1LCP", "TKQK1W9A"] or sys_id in ["SYS-20261929-300", "SYS-20261929-136"]:
        print(f"Row {r_idx}: Mã Hàng='{ma_hang}' | Sys_ID='{sys_id}' | Address='{addr}'")
