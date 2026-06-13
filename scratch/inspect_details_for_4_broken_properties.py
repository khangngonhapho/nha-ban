import os
import sys
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def inspect_details():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    pool_ss = client.open_by_key(POOL_SHEET_ID)
    pool_sheet = pool_ss.worksheet("Pool")
    pool_rows = pool_sheet.get_all_values()
    
    source_ss = client.open_by_key(SOURCE_SHEET_ID)
    source_sheet = source_ss.worksheet("Source")
    source_rows = source_sheet.get_all_values()
    
    pool_headers = pool_rows[0]
    
    # Map headers to indices
    p_ngo_idx = pool_headers.index("Ngõ/Số nhà")
    p_duong_idx = pool_headers.index("Đường")
    p_dt_idx = pool_headers.index("DT Thực tế")
    p_tang_idx = pool_headers.index("Số Tầng")
    p_ngang_idx = pool_headers.index("Mặt Tiền")
    p_gia_idx = pool_headers.index("Giá Public")
    p_sys_idx = pool_headers.index("System ID")
    p_ma_kn_idx = pool_headers.index("Mã Khang Ngô (ID)")
    p_ma_hang_idx = pool_headers.index("Mã Hàng")

    print("=== DETAILS OF THE 4 BROKEN SOURCES ===")
    
    # 1. Trần Quang Diệu (Row 3)
    row_3 = source_rows[2] # Row 3 is index 2
    print(f"\n1. Source Row 3: id={row_3[3]} | System ID={row_3[37]} | Tiêu đề={row_3[4]} | DT={row_3[5]} | Tầng={row_3[6]} | Ngang={row_3[7]} | Giá={row_3[8]}")
    # Candidate Pool Row 143
    r_143 = pool_rows[142] # Row 143 is index 142
    print(f"   -> Candidate Pool Row 143: Mã Hàng={r_143[p_ma_hang_idx]} | Số nhà={r_143[p_ngo_idx]} | Đường={r_143[p_duong_idx]} | Mã KN={r_143[p_ma_kn_idx]} | System ID={r_143[p_sys_idx]} | DT={r_143[p_dt_idx]} | Tầng={r_143[p_tang_idx]} | Ngang={r_143[p_ngang_idx]} | Giá={r_143[p_gia_idx]}")

    # 2. Võ Văn Tần (Row 5)
    row_5 = source_rows[4] # Row 5 is index 4
    print(f"\n2. Source Row 5: id={row_5[3]} | System ID={row_5[37]} | Tiêu đề={row_5[4]} | DT={row_5[5]} | Tầng={row_5[6]} | Ngang={row_5[7]} | Giá={row_5[8]}")
    # Search all Pool rows for Võ Văn Tần with area 31m2
    for idx, r in enumerate(pool_rows[2:], start=3):
        if "võ văn tần" in r[p_duong_idx].lower() and r[p_dt_idx] == "31":
            print(f"   -> Candidate Pool Row {idx}: Mã Hàng={r[p_ma_hang_idx]} | Số nhà={r[p_ngo_idx]} | Đường={r[p_duong_idx]} | Mã KN={r[p_ma_kn_idx]} | System ID={r[p_sys_idx]} | DT={r[p_dt_idx]} | Tầng={r[p_tang_idx]} | Ngang={r[p_ngang_idx]} | Giá={r[p_gia_idx]}")

    # 3. Bàn Cờ (Row 99)
    row_99 = source_rows[98]
    print(f"\n3. Source Row 99: id={row_99[3]} | System ID={row_99[37]} | Tiêu đề={row_99[4]} | DT={row_99[5]} | Tầng={row_99[6]} | Ngang={row_99[7]} | Giá={row_99[8]}")
    # Candidate Pool Row 849
    r_849 = pool_rows[848]
    print(f"   -> Candidate Pool Row 849: Mã Hàng={r_849[p_ma_hang_idx]} | Số nhà={r_849[p_ngo_idx]} | Đường={r_849[p_duong_idx]} | Mã KN={r_849[p_ma_kn_idx]} | System ID={r_849[p_sys_idx]} | DT={r_849[p_dt_idx]} | Tầng={r_849[p_tang_idx]} | Ngang={r_849[p_ngang_idx]} | Giá={r_849[p_gia_idx]}")

    # 4. Huỳnh Văn Bánh (Row 100)
    row_100 = source_rows[99]
    print(f"\n4. Source Row 100: id={row_100[3]} | System ID={row_100[37]} | Tiêu đề={row_100[4]} | DT={row_100[5]} | Tầng={row_100[6]} | Ngang={row_100[7]} | Giá={row_100[8]}")
    # Candidate Pool Row 13
    r_13 = pool_rows[12]
    print(f"   -> Candidate Pool Row 13: Mã Hàng={r_13[p_ma_hang_idx]} | Số nhà={r_13[p_ngo_idx]} | Đường={r_13[p_duong_idx]} | Mã KN={r_13[p_ma_kn_idx]} | System ID={r_13[p_sys_idx]} | DT={r_13[p_dt_idx]} | Tầng={r_13[p_tang_idx]} | Ngang={r_13[p_ngang_idx]} | Giá={r_13[p_gia_idx]}")

if __name__ == "__main__":
    inspect_details()
