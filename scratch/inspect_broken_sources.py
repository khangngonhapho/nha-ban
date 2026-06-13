import os
import sys
import gspread
import unicodedata

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'

def remove_accents(input_str):
    if not input_str:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_ascii.replace('đ', 'd').replace('Đ', 'D').lower().strip()

def inspect_broken():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    print("[1/2] Kết nối và tải Pool...")
    pool_ss = client.open_by_key(POOL_SHEET_ID)
    pool_sheet = pool_ss.worksheet("Pool")
    pool_rows = pool_sheet.get_all_values()
    
    pool_headers = pool_rows[0]
    ngo_idx = pool_headers.index("Ngõ/Số nhà")
    duong_idx = pool_headers.index("Đường")
    sys_id_idx = pool_headers.index("System ID")
    ma_kn_idx = pool_headers.index("Mã Khang Ngô (ID)")
    ma_hang_idx = pool_headers.index("Mã Hàng")
    
    # Danh sách 4 căn bị lệch ở Source cần tìm trong Pool
    targets = [
        {"name": "Trần Quang Diệu", "street": "trần quang diệu", "desc": "Trần Quang Diệu - 38m2"},
        {"name": "Võ Văn Tần", "street": "võ văn tần", "desc": "Võ Văn Tần - 31m2"},
        {"name": "Bàn Cờ", "street": "bàn cờ", "desc": "Bàn Cờ - 86m2"},
        {"name": "Huỳnh Văn Bánh", "street": "huỳnh văn bánh", "desc": "Huỳnh Văn Bánh - 38m2"}
    ]
    
    print("\n--- KẾT QUẢ TÌM KIẾM TRONG POOL SHEET ---")
    for t in targets:
        print(f"\n🔍 Tìm kiếm: {t['desc']}")
        found_count = 0
        normalized_target_street = remove_accents(t["street"])
        
        for idx, row in enumerate(pool_rows[2:], start=3):
            ngo = row[ngo_idx].strip() if len(row) > ngo_idx else ""
            duong = row[duong_idx].strip() if len(row) > duong_idx else ""
            sys_id = row[sys_id_idx].strip() if len(row) > sys_id_idx else ""
            ma_kn = row[ma_kn_idx].strip() if len(row) > ma_kn_idx else ""
            ma_hang = row[ma_hang_idx].strip() if len(row) > ma_hang_idx else ""
            
            normalized_db_street = remove_accents(duong)
            if normalized_target_street in normalized_db_street:
                found_count += 1
                print(f"  - Dòng Pool {idx}: Số nhà='{ngo}' | Đường='{duong}' | Mã KN='{ma_kn}' | System ID='{sys_id}' | Mã Hàng='{ma_hang}'")
                
        if found_count == 0:
            print("  -> Không tìm thấy căn nào tương ứng trong Pool!")

if __name__ == "__main__":
    inspect_broken()
