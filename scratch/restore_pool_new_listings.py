import gspread
import sys

sys.stdout.reconfigure(encoding='utf-8')

pool_sid = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"

try:
    gc = gspread.service_account(filename='credentials.json')
    pool_sh = gc.open_by_key(pool_sid)
    print(f"Opened spreadsheet: {pool_sh.title}")
    
    # Read from Backup tab
    backup_sheet = pool_sh.worksheet("Backup_Pool_Old_TK")
    backup_data = backup_sheet.get_all_values()
    print(f"Loaded {len(backup_data)} rows from 'Backup_Pool_Old_TK'")
    
    pool_headers = backup_data[0]
    link_goc_idx = -1
    for idx, h in enumerate(pool_headers):
        if "link" in h.lower():
            link_goc_idx = idx
            break
            
    filtered_rows = [pool_headers]
    deleted_count = 0
    
    for r_idx, row in enumerate(backup_data[1:], start=2):
        if not row or len(row) == 0:
            continue
        ma_hang = row[0].strip()
        link_goc = row[link_goc_idx].strip() if (link_goc_idx != -1 and len(row) > link_goc_idx) else ""
        
        is_old = ma_hang.startswith("TK-") or "data.thienkhoi.com" in link_goc
        if is_old:
            deleted_count += 1
        else:
            filtered_rows.append(row)
            
    print(f"Filtered: Keeping {len(filtered_rows)} rows. Removing {deleted_count} old rows.")
    
    # Overwrite the live Pool sheet
    pool_sheet = pool_sh.worksheet("Pool")
    pool_sheet.clear()
    # Use ZZ range
    pool_sheet.update(range_name=f"A1:ZZ{len(filtered_rows)}", values=filtered_rows, value_input_option='USER_ENTERED')
    print("Successfully restored new listings to live 'Pool' sheet!")
    
except Exception as e:
    print(f"[❌ ERROR] Restoring Pool sheet failed: {e}")
    sys.exit(1)
