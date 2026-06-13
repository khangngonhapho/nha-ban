import os
import sys
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def inspect():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    print("--- POOL HEADERS ---")
    pool_ss = client.open_by_key(POOL_SHEET_ID)
    pool_sheet = pool_ss.worksheet("Pool")
    pool_rows = pool_sheet.get_all_values()
    print("Number of Pool rows:", len(pool_rows))
    if pool_rows:
        headers = pool_rows[0]
        for idx, h in enumerate(headers):
            print(f"  Col {idx+1}: {h}")
            
    print("\n--- SOURCE HEADERS ---")
    source_ss = client.open_by_key(SOURCE_SHEET_ID)
    source_sheet = source_ss.worksheet("Source")
    source_rows = source_sheet.get_all_values()
    print("Number of Source rows:", len(source_rows))
    if source_rows:
        headers = source_rows[0]
        for idx, h in enumerate(headers):
            print(f"  Col {idx+1}: {h}")

if __name__ == "__main__":
    inspect()
