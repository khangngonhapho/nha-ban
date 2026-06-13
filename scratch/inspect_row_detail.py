import sys
import os
import gspread

# Reconfigure stdout to use utf-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Import helper functions from curator_server
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from curator_server import get_google_credentials
from crawl_pipeline import POOL_HEADERS

rows_to_inspect = [1419, 282, 4471, 5728, 5736, 5729]

def main():
    creds = get_google_credentials()
    if not creds:
        print("Could not load credentials.")
        return
        
    client = gspread.authorize(creds)
    
    print("Connecting to Pool Sheet...")
    pool_spreadsheet = client.open_by_key('1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw')
    pool_sheet = pool_spreadsheet.worksheet("Pool")
    
    for r_idx in rows_to_inspect:
        print(f"\n==========================================")
        print(f"INSPECTING ROW {r_idx} IN POOL SHEET")
        print(f"==========================================")
        row_vals = pool_sheet.row_values(r_idx)
        for i, val in enumerate(row_vals):
            header = POOL_HEADERS[i] if i < len(POOL_HEADERS) else f"COL_{i}"
            if val:
                print(f"  {i} - {header}: {val}")

if __name__ == '__main__':
    main()
