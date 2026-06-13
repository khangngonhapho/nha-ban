import os
import sys
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def check_missing():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    print("[1/2] Đang kết nối và tải dữ liệu...")
    pool_ss = client.open_by_key(POOL_SHEET_ID)
    pool_sheet = pool_ss.worksheet("Pool")
    pool_rows = pool_sheet.get_all_values()
    
    source_ss = client.open_by_key(SOURCE_SHEET_ID)
    source_sheet = source_ss.worksheet("Source")
    source_rows = source_sheet.get_all_values()
    
    pool_headers = pool_rows[0]
    sys_id_pool_idx = pool_headers.index("System ID")
    ma_kn_pool_idx = pool_headers.index("Mã Khang Ngô (ID)")
    ma_hang_pool_idx = pool_headers.index("Mã Hàng")
    ngo_pool_idx = pool_headers.index("Ngõ/Số nhà")
    duong_pool_idx = pool_headers.index("Đường")
    
    # Bản đồ System ID -> Mã Khang Ngô trong Pool
    pool_map = {}
    for idx, row in enumerate(pool_rows[2:], start=3):
        sys_id = row[sys_id_pool_idx].strip() if len(row) > sys_id_pool_idx else ""
        ma_kn = row[ma_kn_pool_idx].strip() if len(row) > ma_kn_pool_idx else ""
        ngo = row[ngo_pool_idx].strip() if len(row) > ngo_pool_idx else ""
        duong = row[duong_pool_idx].strip() if len(row) > duong_pool_idx else ""
        ma_hang = row[ma_hang_pool_idx].strip() if len(row) > ma_hang_pool_idx else ""
        if sys_id:
            pool_map[sys_id] = {
                "row_idx": idx,
                "ma_kn": ma_kn,
                "ngo": ngo,
                "duong": duong,
                "ma_hang": ma_hang
            }
            
    # Duyệt Source
    # Cột D (index 3) là id (Mã Khang Ngô), Cột AL (index 37) is System ID
    source_ma_kn_idx = 3
    source_sys_id_idx = 37
    
    missing_count = 0
    print("\n--- CÁC CĂN SOURCE CÓ MÃ KN NHƯNG TRONG POOL BỊ TRỐNG ---")
    for idx, row in enumerate(source_rows[2:], start=3):
        ma_kn_source = row[source_ma_kn_idx].strip() if len(row) > source_ma_kn_idx else ""
        sys_id_source = row[source_sys_id_idx].strip() if len(row) > source_sys_id_idx else ""
        tieu_de = row[4].strip() if len(row) > 4 else ""
        
        if not ma_kn_source:
            continue
            
        if not sys_id_source:
            print(f"[⚠️ KHÔNG CÓ SYSTEM ID TRÊN SOURCE] Dòng Source {idx}: Mã KN={ma_kn_source} | Tiêu đề={tieu_de}")
            continue
            
        if sys_id_source in pool_map:
            pool_item = pool_map[sys_id_source]
            if not pool_item["ma_kn"]:
                missing_count += 1
                print(f"Lệch #{missing_count}: Dòng Source {idx} (Mã KN: {ma_kn_source}) ➡️ Dòng Pool {pool_item['row_idx']} (System ID: {sys_id_source} | Mã Hàng: {pool_item['ma_hang']} | Địa chỉ: {pool_item['ngo']} {pool_item['duong']}) đang trống Mã KN!")
        else:
            print(f"[⚠️ KHÔNG TÌM THẤY SYSTEM ID TRONG POOL] Dòng Source {idx}: Mã KN={ma_kn_source} | System ID={sys_id_source} | Tiêu đề={tieu_de}")

    print(f"\nTổng cộng có {missing_count} căn trong Source có Mã KN nhưng trong Pool bị trống Mã KN (so khớp qua System ID).")

if __name__ == "__main__":
    check_missing()
