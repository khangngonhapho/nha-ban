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
    
    pool_ss = client.open_by_key(POOL_SHEET_ID)
    pool_sheet = pool_ss.worksheet("Pool")
    pool_rows = pool_sheet.get_all_values()
    
    source_ss = client.open_by_key(SOURCE_SHEET_ID)
    source_sheet = source_ss.worksheet("Source")
    source_rows = source_sheet.get_all_values()
    
    # 1. Search in Pool
    print("--- SEARCH IN POOL ---")
    pool_headers = pool_rows[0]
    sys_id_pool_col = pool_headers.index("System ID")
    ma_kn_pool_col = pool_headers.index("Mã Khang Ngô (ID)")
    ma_hang_pool_col = pool_headers.index("Mã Hàng")
    ngo_so_nha_pool_col = pool_headers.index("Ngõ/Số nhà")
    duong_pool_col = pool_headers.index("Đường")
    
    pool_found = []
    for idx, row in enumerate(pool_rows[2:], start=3):
        # check if row has address containing "vạn kiến" or "33.23"
        ngo = row[ngo_so_nha_pool_col].strip() if len(row) > ngo_so_nha_pool_col else ""
        duong = row[duong_pool_col].strip() if len(row) > duong_pool_col else ""
        ma_hang = row[ma_hang_pool_col].strip() if len(row) > ma_hang_pool_col else ""
        sys_id = row[sys_id_pool_col].strip() if len(row) > sys_id_pool_col else ""
        ma_kn = row[ma_kn_pool_col].strip() if len(row) > ma_kn_pool_col else ""
        
        if "vạn kiến" in duong.lower() or "33.23" in ngo:
            pool_found.append((idx, ma_hang, ngo, duong, ma_kn, sys_id))
            print(f"Row {idx} in Pool: Mã Hàng={ma_hang} | Số nhà={ngo} | Đường={duong} | Mã KN={ma_kn} | System ID={sys_id}")
            
    # 2. Search in Source
    print("\n--- SEARCH IN SOURCE ---")
    source_found = []
    # Source has 41 columns. Col 4 (index 3) is id (Mã Khang Ngô), Col 38 (index 37) is System ID.
    # Col 11 (index 10) is phuong, Col 35 (index 34) is ten_duong.
    for idx, row in enumerate(source_rows[2:], start=3):
        street = row[34].strip() if len(row) > 34 else ""
        ma_kn = row[3].strip() if len(row) > 3 else ""
        sys_id = row[37].strip() if len(row) > 37 else ""
        tieu_de = row[4].strip() if len(row) > 4 else ""
        
        if "vạn kiến" in street.lower() or "vạn kiến" in tieu_de.lower():
            source_found.append((idx, ma_kn, street, sys_id, tieu_de))
            print(f"Row {idx} in Source: id={ma_kn} | Đường={street} | System ID={sys_id} | Tiêu đề={tieu_de}")

if __name__ == "__main__":
    inspect()
