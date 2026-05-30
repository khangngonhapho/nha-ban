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
        col_d_values = sheet.col_values(4) # Col D is id (Mã Khang Ngô)
        col_d_cleaned = [str(x).strip() for x in col_d_values]
        
        target = "AWOIZTIDQT"
        if target in col_d_cleaned:
            idx = col_d_cleaned.index(target) + 1
            row_vals = sheet.row_values(idx)
            print(f"Found Source row {idx} for {target}")
            print(f"Source columns:")
            for i, val in enumerate(row_vals):
                if val:
                    print(f"  Col {i}: {repr(val)}")
        else:
            print(f"Target {target} not found in Source sheet")
    except Exception as e:
        print("Error:")
        traceback.print_exc()
else:
    print("No credentials or sheet_id")
