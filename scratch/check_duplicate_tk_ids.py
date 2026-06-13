import os
import sys
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'

def check_duplicates():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    ss = client.open_by_key(POOL_SHEET_ID)
    sheet = ss.worksheet("Pool")
    all_values = sheet.get_all_values()
    
    data_rows = all_values[2:]
    print("Total rows:", len(data_rows))
    
    tk_id_to_rows = {}
    
    # Headers to find "Link Gốc" or "Mã Hàng"
    headers = all_values[0]
    link_goc_idx = headers.index("Link Gốc")
    ma_hang_idx = headers.index("Mã Hàng")
    
    for idx, row in enumerate(data_rows, start=3):
        if len(row) < 10 or not row[0]:
            continue
            
        link_goc = row[link_goc_idx].strip() if len(row) > link_goc_idx else ""
        ma_hang = row[ma_hang_idx].strip() if len(row) > ma_hang_idx else ""
        
        tk_id = ""
        if link_goc:
            parts = link_goc.rstrip("/").split("/")
            if parts:
                tk_id = parts[-1].strip()
        if not tk_id and ma_hang:
            tk_id = ma_hang
            
        if not tk_id:
            continue
            
        if tk_id not in tk_id_to_rows:
            tk_id_to_rows[tk_id] = []
        tk_id_to_rows[tk_id].append((idx, ma_hang))
        
    duplicates = {k: v for k, v in tk_id_to_rows.items() if len(v) > 1}
    print("Duplicate count:", len(duplicates))
    for k, v in list(duplicates.items())[:10]:
        print(f"tk_id: {k} appears in rows: {v}")

if __name__ == "__main__":
    check_duplicates()
