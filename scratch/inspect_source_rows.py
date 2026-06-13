import os
import sys
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def inspect():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    source_ss = client.open_by_key(SOURCE_SHEET_ID)
    source_sheet = source_ss.worksheet("Source")
    source_rows = source_sheet.get_all_values()
    
    print(f"Total Source rows: {len(source_rows)}")
    for i in range(min(5, len(source_rows))):
        print(f"\n--- ROW {i+1} ---")
        row = source_rows[i]
        for col_idx, val in enumerate(row):
            if val:
                print(f"  Col {col_idx+1}: {val}")

if __name__ == "__main__":
    inspect()
