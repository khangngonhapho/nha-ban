import sys
import os
import gspread

# Reconfigure stdout to use utf-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Import helper functions from curator_server
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from curator_server import get_google_credentials, load_config

houses = [
    "Bùi Đình Tuý",
    "Phạm Văn Hai",
    "Đào Duy Anh",
    "Hoà Hưng",
    "Nhiêu Tứ",
    "Vạn Kiếp"
]

def main():
    creds = get_google_credentials()
    if not creds:
        print("Could not load credentials.")
        return
        
    client = gspread.authorize(creds)
    
    # Try opening Pool Sheet
    pool_rows = []
    print("\nConnecting to Pool Sheet (1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw)...")
    try:
        pool_spreadsheet = client.open_by_key('1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw')
        pool_sheet = pool_spreadsheet.worksheet("Pool")
        pool_rows = pool_sheet.get_all_values()
        print(f"Loaded {len(pool_rows)} rows from Pool.")
    except Exception as e:
        print(f"Failed to connect to Pool Sheet: {e}")

    # Try opening Source Sheet
    source_rows = []
    print("\nConnecting to Source Sheet (1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE)...")
    try:
        source_spreadsheet = client.open_by_key('1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE')
        source_sheet = source_spreadsheet.worksheet("Source")
        source_rows = source_sheet.get_all_values()
        print(f"Loaded {len(source_rows)} rows from Source.")
    except Exception as e:
        print(f"Failed to connect to Source Sheet: {e}")

    # Search in Source sheet
    if source_rows:
        print("\n=== SEARCHING IN SOURCE SHEET ===")
        for house in houses:
            print(f"\nSearching for: {house}")
            found = False
            for idx, row in enumerate(source_rows):
                row_str = " | ".join(row)
                if house.lower() in row_str.lower():
                    row_id = row[3] if len(row) > 3 else ""
                    row_title = row[4] if len(row) > 4 else ""
                    row_q = row[9] if len(row) > 9 else ""
                    row_phuong = row[10] if len(row) > 10 else ""
                    row_gia = row[8] if len(row) > 8 else ""
                    row_sys = row[37] if len(row) > 37 else ""
                    row_status = row[15] if len(row) > 15 else ""
                    print(f"  Row {idx+1}: ID={row_id} | Title={row_title} | Address={row_q} - {row_phuong} | Price={row_gia} | SystemID={row_sys} | Status={row_status}")
                    found = True
            if not found:
                print("  Not found in Source sheet")

    # Search in Pool sheet
    if pool_rows:
        print("\n=== SEARCHING IN POOL SHEET ===")
        for house in houses:
            print(f"\nSearching for: {house}")
            found = False
            for idx, row in enumerate(pool_rows):
                row_str = " | ".join(row)
                if house.lower() in row_str.lower():
                    row_id = row[55] if len(row)>55 else ''
                    row_no = row[6] if len(row)>6 else ''
                    row_st = row[5] if len(row)>5 else ''
                    row_gia = row[11] if len(row)>11 else ''
                    row_sys = row[72] if len(row)>72 else ''
                    # Let's print out some columns related to public status or curation
                    # We can print columns 55 (id), 56 (tieu_de_public), 57 (mo_ta_public), 72 (system_id), 77 (duyet_public)
                    row_duyet = row[77] if len(row) > 77 else ""
                    print(f"  Row {idx+1}: ID={row_id} | Address={row_no} {row_st} | Price={row_gia} | SystemID={row_sys} | Duyet={row_duyet}")
                    found = True
            if not found:
                print("  Not found in Pool sheet")

if __name__ == '__main__':
    main()
