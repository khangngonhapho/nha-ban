import os
import sys
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def inspect_3_sources():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    source_ss = client.open_by_key(SOURCE_SHEET_ID)
    source_sheet = source_ss.worksheet("Source")
    source_rows = source_sheet.get_all_values()
    
    target_ids = {'HWOISCIBZIBC', 'MWOBIHTILHT', 'BBIHBIKV'}
    
    print("--- SEARCH IN SOURCE SHEET ---")
    for idx, row in enumerate(source_rows[2:], start=3):
        ma_kn = row[3].strip() if len(row) > 3 else ""
        if ma_kn in target_ids:
            sys_id = row[37].strip() if len(row) > 37 else ""
            tieu_de = row[4].strip() if len(row) > 4 else ""
            print(f"Row {idx} in Source: id={ma_kn} | System ID={sys_id} | Tiêu đề={tieu_de}")

if __name__ == "__main__":
    inspect_3_sources()
