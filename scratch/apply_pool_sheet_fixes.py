import gspread
import sys
import random
import string

sys.stdout.reconfigure(encoding='utf-8')

pool_sid = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"

try:
    gc = gspread.service_account(filename='credentials.json')
    pool_sh = gc.open_by_key(pool_sid)
    pool_sheet = pool_sh.worksheet("Pool")
    pool_data = pool_sheet.get_all_values()
except Exception as e:
    print(f"Error loading sheet: {e}")
    sys.exit(1)

# Collect all existing Ma_Hangs to prevent collision
existing_ma_hangs = set()
for row in pool_data[1:]:
    if row and row[0].strip():
        existing_ma_hangs.add(row[0].strip().upper())

# 1. Update Row 2 Mã Hàng to TKQLMB8Q
print("[Step 1] Updating Row 2 Mã Hàng to 'TKQLMB8Q'...")
pool_sheet.update_cell(2, 1, "TKQLMB8Q")

# 2. Generate a unique Mã Hàng for Row 11
print("[Step 2] Generating a unique Mã Hàng for Row 11...")
def generate_unique_ma_hang():
    while True:
        # Format: TK + 6 uppercase letters/digits
        chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        code = f"TK{chars}"
        if code not in existing_ma_hangs:
            return code

new_mh_row11 = generate_unique_ma_hang()
print(f"  Generated Code for Row 11: {new_mh_row11}")
pool_sheet.update_cell(11, 1, new_mh_row11)

# 3. Delete Row 8 (duplicate TKT-4587)
print("[Step 3] Deleting Row 8 (duplicate TKT-4587)...")
pool_sheet.delete_rows(8)

print("[SUCCESS] Live Pool sheet has been updated!")
