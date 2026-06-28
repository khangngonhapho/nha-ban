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

target_sys_ids = ['SYS-20261929-300', 'SYS-20261929-136']

print("=== Searching for empty Ma_Hang System IDs in Source Sheet ===")
for sys_id in target_sys_ids:
    found = False
    for r_idx, row in enumerate(source_data[2:], start=3):
        if len(row) > sys_id_idx and row[sys_id_idx].strip() == sys_id:
            found = True
            print(f"Found {sys_id} in Source at Row {r_idx}!")
            # print first 10 columns
            print(f"  Row details: {row[:10]}")
            break
    if not found:
        print(f"NOT found {sys_id} in Source sheet.")
