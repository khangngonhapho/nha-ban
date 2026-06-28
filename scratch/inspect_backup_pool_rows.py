import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

pool_sid = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"

try:
    gc = gspread.service_account(filename='credentials.json')
    pool_sh = gc.open_by_key(pool_sid)
    backup_pool_sheet = pool_sh.worksheet("Backup_Pool_Old_TK")
    backup_pool_data = backup_pool_sheet.get_all_values()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

headers = backup_pool_data[0]

# Let's search by System_ID in the backup pool data
target_sys_ids = [
    "SYS-20261929-300", # Row 2 in current Pool
    "SYS-20263803-400", # Row 8
    "SYS-20265704-735", # Row 9
    "SYS-20261304-536", # Row 10
    "SYS-20261929-136", # Row 11
    "SYS-20260005-110", # Row 12
    "SYS-20260611-812", # Row 24
]

print("=== Inspecting Pre-Cleaned Pool (Backup_Pool_Old_TK) ===")
sys_id_idx = -1
for idx, h in enumerate(headers):
    if "system id" in h.lower():
        sys_id_idx = idx
        break
        
if sys_id_idx == -1:
    print("Could not find System ID column in headers.")
    sys.exit(1)

for sys_id in target_sys_ids:
    found = False
    for r_idx, row in enumerate(backup_pool_data[1:], start=2):
        if len(row) > sys_id_idx and row[sys_id_idx].strip() == sys_id:
            found = True
            print(f"\nFound System ID '{sys_id}' in Backup Pool at Row {r_idx}:")
            # Print Ma_Hang, Address, and Link Gốc
            ma_hang = row[0].strip() if row else ""
            addr = f"{row[6]} {row[5]}" if len(row) > 6 else ""
            link_goc_idx = -1
            for c_idx, h in enumerate(headers):
                if "link" in h.lower():
                    link_goc_idx = c_idx
                    break
            link_goc = row[link_goc_idx].strip() if (link_goc_idx != -1 and len(row) > link_goc_idx) else ""
            print(f"  Mã Hàng: '{ma_hang}'")
            print(f"  Address: '{addr}'")
            print(f"  Link Gốc: '{link_goc}'")
            # Print any column named "Mã TK Mới"
            ma_tk_moi_idx = -1
            for c_idx, h in enumerate(headers):
                if "mã tk mới" in h.lower():
                    ma_tk_moi_idx = c_idx
                    break
            if ma_tk_moi_idx != -1:
                print(f"  Mã TK Mới: '{row[ma_tk_moi_idx]}'")
            break
            
    if not found:
        print(f"\nNOT found System ID '{sys_id}' in Backup Pool.")
