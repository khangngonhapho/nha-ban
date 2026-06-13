import os
import sys
import gspread
import unicodedata
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'

def remove_accents(input_str):
    if not input_str:
        return ""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_ascii.replace('đ', 'd').replace('Đ', 'D')

def normalize_address(ngo, duong):
    ngo_clean = remove_accents(str(ngo)).strip().lower().replace("/", ".").replace(" ", "")
    duong_clean = remove_accents(str(duong)).strip().lower().replace(" ", "")
    if not ngo_clean or not duong_clean:
        return None
    return f"{ngo_clean}@{duong_clean}"

def inspect_duplicates():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    print("[1/2] Kết nối Google Sheets và tải Pool...")
    pool_ss = client.open_by_key(POOL_SHEET_ID)
    pool_sheet = pool_ss.worksheet("Pool")
    pool_rows = pool_sheet.get_all_values()
    
    pool_headers = pool_rows[0]
    ngo_idx = pool_headers.index("Ngõ/Số nhà")
    duong_idx = pool_headers.index("Đường")
    ma_kn_idx = pool_headers.index("Mã Khang Ngô (ID)")
    ma_hang_idx = pool_headers.index("Mã Hàng")
    sys_id_idx = pool_headers.index("System ID")
    
    # Gom nhóm theo địa chỉ
    address_groups = defaultdict(list)
    for idx, row in enumerate(pool_rows[2:], start=3):
        ngo = row[ngo_idx].strip() if len(row) > ngo_idx else ""
        duong = row[duong_idx].strip() if len(row) > duong_idx else ""
        ma_kn = row[ma_kn_idx].strip() if len(row) > ma_kn_idx else ""
        ma_hang = row[ma_hang_idx].strip() if len(row) > ma_hang_idx else ""
        sys_id = row[sys_id_idx].strip() if len(row) > sys_id_idx else ""
        
        addr_key = normalize_address(ngo, duong)
        if addr_key:
            address_groups[addr_key].append({
                "row_idx": idx,
                "ngo": ngo,
                "duong": duong,
                "ma_kn": ma_kn,
                "ma_hang": ma_hang,
                "sys_id": sys_id
            })
            
    print("\n--- PHÁT HIỆN TRÙNG LẶP ĐỊA CHỈ TRONG POOL ---")
    dup_count = 0
    for addr_key, items in address_groups.items():
        if len(items) > 1:
            # Kiểm tra xem có thực sự là các dòng dư thừa cần gộp không
            # Ví dụ: một dòng có Mã Hàng (crawler), dòng kia không có Mã Hàng nhưng có Mã Khang Ngô
            has_crawler = any(x["ma_hang"] for x in items)
            has_manual = any(not x["ma_hang"] and x["ma_kn"] for x in items)
            
            dup_count += 1
            print(f"\nTrùng lặp #{dup_count} (Địa chỉ: {items[0]['ngo']} {items[0]['duong']}):")
            for item in items:
                print(f"  - Dòng Pool {item['row_idx']}: Mã Hàng={item['ma_hang']} | Mã KN={item['ma_kn']} | System ID={item['sys_id']}")

    print(f"\nTổng cộng tìm thấy {dup_count} địa chỉ bị trùng lặp dòng trong Pool.")

if __name__ == "__main__":
    inspect_duplicates()
