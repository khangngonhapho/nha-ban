import os
import sys
import gspread
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def normalize_address(ngo, duong):
    ngo = str(ngo).strip().lower().replace("/", ".").replace(" ", "")
    # Remove accents for street to match typos
    duong = str(duong).strip().lower().replace(" ", "")
    # Simple replacement of common characters
    return f"{ngo}@{duong}"

def inspect():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    pool_ss = client.open_by_key(POOL_SHEET_ID)
    pool_sheet = pool_ss.worksheet("Pool")
    pool_rows = pool_sheet.get_all_values()
    
    source_ss = client.open_by_key(SOURCE_SHEET_ID)
    source_sheet = source_ss.worksheet("Source")
    source_rows = source_sheet.get_all_values()
    
    # 1. Map Source entries by address and id (Mã Khang Ngô)
    source_address_map = {}
    for idx, row in enumerate(source_rows[2:], start=3):
        # Col 4 is id (Mã Khang Ngô), Col 11 is phuong, Col 35 is ten_duong.
        # But we don't have the original ngo_so_nha in Source easily, wait!
        # Col 2 is Cu_phap (contains address text!). Let's parse Cu_phap.
        # E.g. "40.78 trần quang diệu 38 3..." -> ngo = 40.78, duong = trần quang diệu
        cu_phap = row[1].strip() if len(row) > 1 else ""
        ma_kn = row[3].strip() if len(row) > 3 else ""
        sys_id = row[37].strip() if len(row) > 37 else ""
        
        if not ma_kn:
            continue
            
        # Try to parse ngo and duong from Cu_phap
        # Usually it starts with: "number street area..."
        match = re.match(r'^([\d\./\+]+)\s+([^\d]+)', cu_phap, re.I)
        if match:
            ngo = match.group(1).strip()
            duong_raw = match.group(2).strip()
            # remove trailing numbers or words like "m2" or "tỷ"
            duong = re.split(r'\s\d', duong_raw)[0].strip()
            addr_key = normalize_address(ngo, duong)
            source_address_map[addr_key] = (ma_kn, sys_id, cu_phap)
            
    print(f"Mapped {len(source_address_map)} Source listings by address.")

    # 2. Check Pool rows
    pool_headers = pool_rows[0]
    ngo_col = pool_headers.index("Ngõ/Số nhà")
    duong_col = pool_headers.index("Đường")
    ma_kn_col = pool_headers.index("Mã Khang Ngô (ID)")
    sys_id_col = pool_headers.index("System ID")
    ma_hang_col = pool_headers.index("Mã Hàng")
    
    updates = []
    mismatches = 0
    
    for idx, row in enumerate(pool_rows[2:], start=3):
        ngo = row[ngo_col].strip() if len(row) > ngo_col else ""
        duong = row[duong_col].strip() if len(row) > duong_col else ""
        ma_kn_pool = row[ma_kn_col].strip() if len(row) > ma_kn_col else ""
        sys_id = row[sys_id_col].strip() if len(row) > sys_id_col else ""
        ma_hang = row[ma_hang_col].strip() if len(row) > ma_hang_col else ""
        
        addr_key = normalize_address(ngo, duong)
        if addr_key in source_address_map:
            source_ma_kn, source_sys_id, cu_phap = source_address_map[addr_key]
            
            # If the Pool row has no Mã Khang Ngô, or it's different, let's update it!
            if not ma_kn_pool or ma_kn_pool != source_ma_kn:
                col_letter = gspread.utils.rowcol_to_a1(idx, ma_kn_col + 1).split(str(idx))[0]
                updates.append({
                    'range': f"{col_letter}{idx}:{col_letter}{idx}",
                    'values': [[source_ma_kn]]
                })
                mismatches += 1
                print(f"Match found by address '{ngo} {duong}': Pool Row {idx} (Mã Hàng: {ma_hang}, System ID: {sys_id}) has KN='{ma_kn_pool}' ➡️ Overwriting with Source KN='{source_ma_kn}' (System ID in Source: {source_sys_id})")

    print(f"\nFound {mismatches} address-based mismatches/empty KN IDs on Pool sheet.")

if __name__ == "__main__":
    inspect()
