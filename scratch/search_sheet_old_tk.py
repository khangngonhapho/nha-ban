import gspread
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

# Sheet IDs to check
sheet_ids = {
    "settings_sheet_id": "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw",
    "pool2_raw_sheet_id": "1fwMeR_UyfABoZ-IWRDYwEU9rlbPXZENOgXaiEw2cbmg",
    "pool2_custom_sheet_id": "11BZxVYP7Xsv6JVvWMK9VpPipT91Ue5wfNuhO3rbZe7U",
    "pool2_public_sheet_id": "1U2lEH07GIyiO3YY3_jzCk_09DErd9a6r8cjZhioE_5g",
    "sot_sheet_id": "1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0"
}

try:
    gc = gspread.service_account(filename='credentials.json')
    print("Google Sheets Authenticated Successfully")
except Exception as e:
    print(f"Auth failed: {e}")
    sys.exit(1)

for name, sid in sheet_ids.items():
    print(f"\nChecking Sheet: {name} (ID: {sid})")
    try:
        sh = gc.open_by_key(sid)
        print(f"  Title: {sh.title}")
        worksheets = sh.worksheets()
        print(f"  Tabs: {[w.title for w in worksheets]}")
        
        for w in worksheets:
            # Let's read values
            data = w.get_all_values()
            if not data:
                print(f"    Tab '{w.title}': Empty")
                continue
            
            total_rows = len(data)
            # Find occurrences of TK- or thienkhoi
            tk_code_count = 0
            old_link_count = 0
            for r_idx, row in enumerate(data):
                row_str = " ".join(str(cell) for cell in row)
                # Count if 'TK-' in first cell or in row
                if len(row) > 0 and str(row[0]).startswith("TK-"):
                    tk_code_count += 1
                if "data.thienkhoi.com" in row_str:
                    old_link_count += 1
                    
            print(f"    Tab '{w.title}': {total_rows} rows, {tk_code_count} rows starting with 'TK-', {old_link_count} rows containing old Link_Goc")
            
    except Exception as e:
        print(f"  Error opening sheet {name} ({sid}): {e}")
