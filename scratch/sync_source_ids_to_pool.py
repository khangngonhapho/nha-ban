import os
import sys
import time
import gspread

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def sync_ids():
    print("======================================================================")
    print("🔄 BẮT ĐẦU ĐỒNG BỘ MÃ KHANG NGÔ TỪ SOURCE SANG POOL QUA SYSTEM ID")
    print("======================================================================")
    
    creds = get_google_credentials()
    if not creds:
        print("[❌ LỖI] Không tìm thấy credentials.json!")
        return

    client = gspread.authorize(creds)
    
    try:
        print("[1/3] Kết nối Google Sheets...")
        pool_ss = client.open_by_key(POOL_SHEET_ID)
        pool_sheet = pool_ss.worksheet("Pool")
        
        source_ss = client.open_by_key(SOURCE_SHEET_ID)
        source_sheet = source_ss.worksheet("Source")
    except Exception as e:
        print(f"[❌ LỖI] Không thể kết nối Google Sheets: {str(e)}")
        return

    print("[2/3] Đang tải dữ liệu từ cả 2 sheet...")
    pool_rows = pool_sheet.get_all_values()
    source_rows = source_sheet.get_all_values()
    
    if len(pool_rows) < 3 or len(source_rows) < 3:
        print("[-] Dữ liệu một trong hai sheet trống rỗng!")
        return
        
    pool_headers = pool_rows[0]
    source_headers = source_rows[1] # Dòng thứ 2 chứa tiêu đề thực tế snake_case
    
    sys_id_pool_col = pool_headers.index("System ID") + 1  # 1-based (Cột BU / 73)
    ma_kn_pool_col = pool_headers.index("Mã Khang Ngô (ID)") + 1  # 1-based (Cột BD / 56)
    
    # Ở Source: Cột D (4) là id (Mã Khang Ngô), Cột AL (38) là System ID
    sys_id_source_idx = 37 # 0-based
    ma_kn_source_idx = 3  # 0-based
    
    print(f"  - System ID Pool Col: {sys_id_pool_col} | Mã Khang Ngô Pool Col: {ma_kn_pool_col}")
    
    # Lập bản đồ System ID -> Mã Khang Ngô từ Source sheet
    source_map = {}
    for idx, row in enumerate(source_rows[2:], start=3):
        if len(row) > sys_id_source_idx:
            sys_id = row[sys_id_source_idx].strip()
            ma_kn = row[ma_kn_source_idx].strip() if len(row) > ma_kn_source_idx else ""
            if sys_id and ma_kn:
                source_map[sys_id] = ma_kn
                
    print(f"  - Tìm thấy {len(source_map)} mã Khang Ngô hợp lệ trên Source sheet.")
    
    # Quét Pool sheet để tìm các dòng trống hoặc khác mã Khang Ngô
    updates = []
    for idx, row in enumerate(pool_rows[2:], start=3):
        sys_id = row[sys_id_pool_col - 1].strip() if len(row) > sys_id_pool_col - 1 else ""
        ma_kn_pool = row[ma_kn_pool_col - 1].strip() if len(row) > ma_kn_pool_col - 1 else ""
        
        if sys_id and sys_id in source_map:
            source_ma_kn = source_map[sys_id]
            # Nếu trống hoặc khác biệt
            if not ma_kn_pool or ma_kn_pool != source_ma_kn:
                # Chuyển đổi ma_kn_pool_col sang Column Letter (BD = Col 56)
                # BD56 -> range
                col_letter = gspread.utils.rowcol_to_a1(idx, ma_kn_pool_col).split(str(idx))[0]
                updates.append({
                    'range': f"{col_letter}{idx}:{col_letter}{idx}",
                    'values': [[source_ma_kn]]
                })
                print(f"  [📍 Cần đồng bộ] Dòng Pool {idx} (System ID: {sys_id}): Cập nhật Mã Khang Ngô '{ma_kn_pool}' ➡️ '{source_ma_kn}'")

    print(f"\n[3/3] Bắt đầu cập nhật {len(updates)} dòng lên sheet Pool...")
    
    if not updates:
        print("[✅] Không có dòng nào cần đồng bộ. Tất cả Mã Khang Ngô trên Pool và Source đã khớp hoàn hảo!")
        return
        
    # batch update lên Pool
    batch_size = 100
    groups = [updates[i:i + batch_size] for i in range(0, len(updates), batch_size)]
    
    for g_idx, group in enumerate(groups, start=1):
        print(f"  -> Đang đẩy Nhóm {g_idx}/{len(groups)} ({len(group)} dòng)...")
        pool_sheet.batch_update(group, value_input_option='USER_ENTERED')
        time.sleep(1.0)
        
    print("======================================================================")
    print(f"🏁 ĐÃ HOÀN TẤT: Đồng bộ thành công {len(updates)} Mã Khang Ngô sang sheet Pool!")
    print("======================================================================")

if __name__ == "__main__":
    sync_ids()
