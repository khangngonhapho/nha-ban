import gspread
import sys
import json

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
rows_to_inspect = [2, 8, 9, 10, 11, 12, 24]

for r_idx in rows_to_inspect:
    if r_idx <= len(pool_data):
        row = pool_data[r_idx - 1]
        print(f"\n=== Details for Row {r_idx} ===")
        for col_idx, (h, val) in enumerate(zip(headers, row)):
            # Print column header and value if value is not empty or if it's important
            if val.strip() or h in ["Mã Hàng", "Ngõ/Số nhà", "Đường", "Nội dung chính", "System ID"]:
                print(f"  {h}: {val}")
