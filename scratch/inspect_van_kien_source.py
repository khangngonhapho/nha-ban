import os
import sys
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def inspect_source():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    source_ss = client.open_by_key(SOURCE_SHEET_ID)
    source_sheet = source_ss.worksheet("Source")
    source_rows = source_sheet.get_all_values()
    
    headers = source_rows[0]
    print("Source columns:", headers)
    
    print("\n--- SEARCH IN SOURCE ---")
    for idx, row in enumerate(source_rows[2:], start=3):
        row_str = " | ".join(row).lower()
        if "bbihbikv" in row_str or "33.23" in row_str or "vạn kiếp" in row_str or "vạn kiến" in row_str:
            print(f"Row {idx} match:")
            for col_idx, val in enumerate(row):
                if val.strip():
                    print(f"  Col {col_idx} ({headers[col_idx] if col_idx < len(headers) else '?'}) = {val}")

if __name__ == "__main__":
    inspect_source()
