import os
import sys
import time
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def merge_and_cleanup():
    print("======================================================================")
    print("🔄 BẮT ĐẦU GỘP TIN TRÙNG LẶP (THỦ CÔNG + CÀO) & DỌN DẸP POOL SHEET")
    print("======================================================================")
    
    creds = get_google_credentials()
    if not creds:
        print("[❌ LỖI] Không tìm thấy credentials.json!")
        return

    client = gspread.authorize(creds)
    
    try:
        print("[1/4] Kết nối các Google Sheets...")
        pool_ss = client.open_by_key(POOL_SHEET_ID)
        pool_sheet = pool_ss.worksheet("Pool")
        
        source_ss = client.open_by_key(SOURCE_SHEET_ID)
        source_sheet = source_ss.worksheet("Source")
    except Exception as e:
        print(f"[❌ LỖI] Không thể kết nối Google Sheets: {str(e)}")
        return

    # Định vị cột trên Pool sheet để update
    pool_headers = pool_sheet.row_values(1)
    ma_kn_pool_idx = pool_headers.index("Mã Khang Ngô (ID)") + 1 # 1-based
    sys_id_pool_idx = pool_headers.index("System ID") + 1 # 1-based
    
    # Định vị cột trên Source sheet để update (cột 38 - System ID, cột AL)
    # Cột D (4) là id (Mã Khang Ngô), Cột AL (38) là System ID
    sys_id_source_idx = 38 # 1-based (Cột AL)
    
    # ----------------------------------------------------
    # BƯỚC 2: Cập nhật thông tin dòng cào trong Pool & Source
    # ----------------------------------------------------
    print("\n[2/4] Đang cập nhật thông tin đồng bộ dòng cào...")

    # 1. Căn Vạn Kiếp (33.23 Vạn Kiếp)
    # - Cập nhật dòng cào Pool Row 4581: Mã KN -> 'BBIHBIKV', System ID -> 'SYS-20261929-135' (để khớp với Source Row 104)
    print("  - Cập nhật dòng cào Vạn Kiếp (Pool Row 4581)...")
    col_letter_kn = gspread.utils.rowcol_to_a1(4581, ma_kn_pool_idx).split("4581")[0]
    col_letter_sys = gspread.utils.rowcol_to_a1(4581, sys_id_pool_idx).split("4581")[0]
    
    pool_sheet.update(range_name=f"{col_letter_kn}4581", values=[["BBIHBIKV"]])
    pool_sheet.update(range_name=f"{col_letter_sys}4581", values=[["SYS-20261929-135"]])

    # 2. Căn Cô Bắc (20.69.37 Cô Bắc)
    # - Cập nhật dòng cào Pool Row 4557: Mã KN -> 'HWOISCIBZIBC'
    # - Cập nhật Source Row 90: System ID -> 'SYS-20263127-384' (của dòng cào)
    print("  - Cập nhật dòng cào Cô Bắc (Pool Row 4557 & Source Row 90)...")
    col_letter_kn_cb = gspread.utils.rowcol_to_a1(4557, ma_kn_pool_idx).split("4557")[0]
    pool_sheet.update(range_name=f"{col_letter_kn_cb}4557", values=[["HWOISCIBZIBC"]])
    
    col_letter_sys_source_cb = gspread.utils.rowcol_to_a1(90, sys_id_source_idx).split("90")[0]
    source_sheet.update(range_name=f"{col_letter_sys_source_cb}90", values=[["SYS-20263127-384"]])

    # 3. Căn Trần Huy Liệu (103.28 Trần Huy Liệu)
    # - Cập nhật dòng cào Pool Row 4677: Mã KN -> 'MWOBIHTILHT'
    # - Cập nhật Source Row 92: System ID -> 'SYS-20265927-526' (của dòng cào)
    print("  - Cập nhật dòng cào Trần Huy Liệu (Pool Row 4677 & Source Row 92)...")
    col_letter_kn_thl = gspread.utils.rowcol_to_a1(4677, ma_kn_pool_idx).split("4677")[0]
    pool_sheet.update(range_name=f"{col_letter_kn_thl}4677", values=[["MWOBIHTILHT"]])
    
    col_letter_sys_source_thl = gspread.utils.rowcol_to_a1(92, sys_id_source_idx).split("92")[0]
    source_sheet.update(range_name=f"{col_letter_sys_source_thl}92", values=[["SYS-20265927-526"]])
    
    print("[✅] Đã hoàn tất cập nhật các dòng cào và liên kết System ID.")
    time.sleep(2.0)

    # ----------------------------------------------------
    # BƯỚC 3: Xóa các dòng thủ công thừa trên Pool sheet
    # ----------------------------------------------------
    print("\n[3/4] Đang xóa các dòng tạo thủ công dư thừa trên Pool sheet...")
    # Phải xóa theo thứ tự giảm dần dòng để chỉ số dòng không bị lệch!
    # Dòng thủ công: Vạn Kiếp (5729), Trần Huy Liệu (159), Cô Bắc (158)
    
    print("  - Xóa dòng thủ công Vạn Kiếp (Row 5729)...")
    pool_sheet.delete_rows(5729)
    time.sleep(1.0)
    
    print("  - Xóa dòng thủ công Trần Huy Liệu (Row 159)...")
    pool_sheet.delete_rows(159)
    time.sleep(1.0)
    
    print("  - Xóa dòng thủ công Cô Bắc (Row 158)...")
    pool_sheet.delete_rows(158)
    time.sleep(1.0)
    
    print("[✅] Đã xóa thành công các dòng thủ công dư thừa.")

    # ----------------------------------------------------
    # BƯỚC 4: Hoàn tất
    # ----------------------------------------------------
    print("\n[4/4] Hoàn thành quá trình gộp và dọn dẹp!")
    print("======================================================================")
    print("🏁 ĐÃ HOÀN TẤT: Dọn dẹp thành công Pool sheet và đồng bộ liên kết Source!")
    print("👉 Hãy chạy restore_db_from_sheets.py để hoàn tất đồng bộ SQLite DB cục bộ.")
    print("======================================================================")

if __name__ == "__main__":
    merge_and_cleanup()
