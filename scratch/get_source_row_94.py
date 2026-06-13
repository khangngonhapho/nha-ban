import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout = open("scratch/get_source_row_94_output.txt", "w", encoding="utf-8")

import gspread
import traceback
from curator_server import get_google_credentials

creds = get_google_credentials()
sheet_id = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

if creds and sheet_id:
    try:
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.worksheet("Source")
        
        # Read all rows of Column D (Mã Khang Ngô)
        col_d_values = sheet.col_values(4)
        col_d_cleaned = [str(x).strip() for x in col_d_values]
        
        target = "HWZOICBIMSIPDP"
        if target in col_d_cleaned:
            idx = col_d_cleaned.index(target) + 1
            row_vals = sheet.row_values(idx)
            print(f"Found Source row {idx} for target {target}")
            print(f"Number of columns: {len(row_vals)}")
            for i, val in enumerate(row_vals):
                print(f"  Col {i+1} (Index {i}): {repr(val)}")
        else:
            print(f"Target {target} not found in Column D of Source sheet.")
            # Search other columns or print the first 10 values
            print("First 10 values in Column D:")
            for i, val in enumerate(col_d_cleaned[:10]):
                print(f"  Row {i+1}: {repr(val)}")
                
    except Exception as e:
        print("Error:")
        traceback.print_exc()
else:
    print("No credentials or sheet_id")

sys.stdout.close()
