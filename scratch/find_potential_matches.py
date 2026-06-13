import os
import sys
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'

def find_matches():
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    pool_ss = client.open_by_key(POOL_SHEET_ID)
    pool_sheet = pool_ss.worksheet("Pool")
    pool_rows = pool_sheet.get_all_values()
    
    pool_headers = pool_rows[0]
    p_ngo_idx = pool_headers.index("Ngõ/Số nhà")
    p_duong_idx = pool_headers.index("Đường")
    p_dt_idx = pool_headers.index("DT Thực tế")
    p_tang_idx = pool_headers.index("Số Tầng")
    p_ngang_idx = pool_headers.index("Mặt Tiền")
    p_gia_idx = pool_headers.index("Giá Public")
    p_sys_idx = pool_headers.index("System ID")
    p_ma_kn_idx = pool_headers.index("Mã Khang Ngô (ID)")
    p_ma_hang_idx = pool_headers.index("Mã Hàng")

    # Define targets to search with tolerance
    targets = [
        {"name": "Trần Quang Diệu", "street": "trần quang diệu", "dt": 38, "gia": 8.75},
        {"name": "Võ Văn Tần", "street": "võ văn tần", "dt": 31, "gia": 7.6},
        {"name": "Bàn Cờ", "street": "bàn cờ", "dt": 86, "gia": 18.0}
    ]

    print("=== SEARCHING WITH TOLERANCE IN POOL SHEET ===")
    
    for t in targets:
        print(f"\n🔍 Tìm kiếm căn: {t['name']} (DT khoảng {t['dt']}m2, Giá khoảng {t['gia']} tỷ)")
        found = 0
        for idx, r in enumerate(pool_rows[2:], start=3):
            duong = r[p_duong_idx].strip().lower()
            if t["street"] in duong:
                # Parse area and price safely
                try:
                    dt_val = float(r[p_dt_idx].replace(",", ".").strip())
                except:
                    dt_val = 0.0
                try:
                    # public price is in millions or formatted with commas
                    gia_str = r[p_gia_idx].replace(",", "").replace(".", "").strip()
                    gia_val = float(gia_str) / 1000.0 if float(gia_str) > 1000 else float(gia_str)
                except:
                    gia_val = 0.0
                
                # Check tolerance
                dt_diff = abs(dt_val - t["dt"])
                # Compare
                if dt_diff <= 5: # Sai số diện tích tối đa 5m2
                    found += 1
                    print(f"  - Dòng Pool {idx}: Mã Hàng={r[p_ma_hang_idx]} | Số nhà='{r[p_ngo_idx]}' | Đường='{r[p_duong_idx]}' | DT={r[p_dt_idx]} (diff={dt_diff:.1f}) | Tầng={r[p_tang_idx]} | Ngang={r[p_ngang_idx]} | Giá={r[p_gia_idx]} | System ID={r[p_sys_idx]}")
                    
        if found == 0:
            print("  -> Không tìm thấy căn nào tương ứng trong Pool!")

if __name__ == "__main__":
    find_matches()
