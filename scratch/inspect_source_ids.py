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
    
    print("--- SEARCH IN SOURCE ---")
    for idx, row in enumerate(source_rows[2:], start=3):
        # Join row values and check if any search term is inside
        row_str = " | ".join(row).lower()
        if "33.23" in row_str or "bbihbikv" in row_str or "sys-20262527-783" in row_str or "sys-20261929-135" in row_str:
            print(f"Row {idx} in Source: id={row[3]} | tieu_de={row[4]} | street={row[34]} | System ID={row[37]}")

if __name__ == "__main__":
    inspect()
