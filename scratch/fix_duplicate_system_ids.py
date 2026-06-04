import os
import sys
import random
import time
import gspread
from datetime import datetime

# Add root folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials, load_config

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def generate_unique_sys_id(existing_ids):
    while True:
        # Format: SYS-YYYYMMDD-RANDOM (e.g. SYS-20260603-942)
        new_id = f"SYS-{datetime.now().strftime('%Y%m%d').upper()}-{random.randint(100, 999)}"
        if new_id not in existing_ids:
            existing_ids.add(new_id)
            return new_id

def fix_duplicates():
    print("======================================================================")
    # Reconfigure stdout for utf-8 output in Windows
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass
            
    print("🧹 BẮT ĐẦU SỬA TRÙNG LẶP SYSTEM ID TRÊN GOOGLE SHEETS POOL & SOURCE")
    print("======================================================================")
    
    creds = get_google_credentials()
    if not creds:
        print("[❌ LỖI] Không tìm thấy credentials.json!")
        return

    client = gspread.authorize(creds)
    
    # 1. Mở các bảng tính
    print("[1/4] Kết nối với Google Sheets...")
    try:
        pool_spreadsheet = client.open_by_key(POOL_SHEET_ID)
        pool_sheet = pool_spreadsheet.worksheet("Pool")
        
        source_spreadsheet = client.open_by_key(SOURCE_SHEET_ID)
        source_sheet = source_spreadsheet.worksheet("Source")
    except Exception as e:
        print(f"[❌ LỖI] Không kết nối được Google Sheets: {str(e)}")
        return

    # 2. Đọc toàn bộ dữ liệu
    print("[2/4] Đang tải toàn bộ dữ liệu từ Pool và Source...")
    pool_rows = pool_sheet.get_all_values()
    source_rows = source_sheet.get_all_values()
    
    if len(pool_rows) < 2:
        print("[-] Sheet Pool trống!")
        return
        
    # Headers
    pool_headers = pool_rows[0]
    source_headers = source_rows[0]
    
    sys_id_pool_col = pool_headers.index("System ID") + 1  # 1-based
    ma_hang_pool_col = pool_headers.index("Mã Hàng") + 1    # 1-based
    ma_kn_pool_col = pool_headers.index("Mã Khang Ngô (ID)") + 1
    
    sys_id_source_col = 38 # Column AL (1-based)
    ma_kn_source_col = 4   # Column D (1-based)
    
    print(f"  - Số dòng trong Pool: {len(pool_rows)}")
    print(f"  - Số dòng trong Source: {len(source_rows)}")
    
    # Gom tất cả các System ID hiện tại để chống trùng khi sinh mới
    existing_sys_ids = set()
    for row in pool_rows[2:]: # Dữ liệu thực tế từ dòng 3 (index 2)
        if len(row) > sys_id_pool_col - 1:
            sys_id = row[sys_id_pool_col - 1].strip()
            if sys_id:
                existing_sys_ids.add(sys_id)
                
    for row in source_rows[1:]: # Dữ liệu thực tế từ dòng 2 (index 1)
        if len(row) > sys_id_source_col - 1:
            sys_id = row[sys_id_source_col - 1].strip()
            if sys_id:
                existing_sys_ids.add(sys_id)

    # 3. Phân tích trùng lặp trên Pool sheet
    print("\n[3/4] Đang phân tích trùng lặp và trống System ID trên Pool...")
    
    sys_id_to_rows = {}
    rows_to_fix = [] # Danh sách chứa: (row_number, ma_hang, ma_kn, old_sys_id)
    
    for idx, row in enumerate(pool_rows[2:], start=3):
        ma_hang = row[ma_hang_pool_col - 1].strip() if len(row) > ma_hang_pool_col - 1 else ""
        ma_kn = row[ma_kn_pool_col - 1].strip() if len(row) > ma_kn_pool_col - 1 else ""
        sys_id = row[sys_id_pool_col - 1].strip() if len(row) > sys_id_pool_col - 1 else ""
        
        if not ma_hang:
            continue
            
        if not sys_id:
            # Trống thì bắt buộc phải sửa
            rows_to_fix.append((idx, ma_hang, ma_kn, ""))
        else:
            if sys_id not in sys_id_to_rows:
                sys_id_to_rows[sys_id] = []
            sys_id_to_rows[sys_id].append((idx, ma_hang, ma_kn))
            
    # Lọc ra các ID bị trùng lặp (giữ lại dòng đầu tiên, đổi mã các dòng sau)
    duplicate_count = 0
    blank_count = len([r for r in rows_to_fix if r[3] == ""])
    
    for sys_id, r_list in sys_id_to_rows.items():
        if len(r_list) > 1:
            duplicate_count += len(r_list) - 1
            # Giữ nguyên dòng đầu (r_list[0]), sửa các dòng sau (r_list[1:])
            for duplicate_row in r_list[1:]:
                rows_to_fix.append((duplicate_row[0], duplicate_row[1], duplicate_row[2], sys_id))
                
    print(f"  - Phát hiện trùng lặp: {duplicate_count} dòng")
    print(f"  - Phát hiện trống ID: {blank_count} dòng")
    
    if not rows_to_fix:
        print("[✅] Dữ liệu sạch sẽ! Không phát hiện trùng lặp hay trống System ID nào cần sửa.")
        return
        
    print(f"  ➡️ Tổng số dòng cần xử lý sửa mã: {len(rows_to_fix)}")

    # Tạo bản đồ Map từ Mã Khang Ngô sang hàng của Source để cập nhật đồng bộ
    source_ma_kn_to_row = {}
    for idx, row in enumerate(source_rows[1:], start=2):
        if len(row) > ma_kn_source_col - 1:
            ma_kn = row[ma_kn_source_col - 1].strip()
            if ma_kn:
                source_ma_kn_to_row[ma_kn] = idx

    # 4. Thực hiện cập nhật hàng loạt lên Sheets
    print("\n[4/4] Bắt đầu đồng bộ và cập nhật System ID mới lên Google Sheets...")
    
    pool_batch_updates = []
    source_batch_updates = []
    
    fixed_count = 0
    source_sync_count = 0
    
    for row_num, ma_hang, ma_kn, old_sys_id in rows_to_fix:
        new_sys_id = generate_unique_sys_id(existing_sys_ids)
        
        # Thêm cập nhật Pool: Cột BU (Column 73)
        pool_batch_updates.append({
            'range': f"BU{row_num}:BU{row_num}",
            'values': [[new_sys_id]]
        })
        fixed_count += 1
        
        # Nếu có Mã Khang Ngô và căn này đã được đồng bộ lên Source
        if ma_kn and ma_kn in source_ma_kn_to_row:
            source_row_num = source_ma_kn_to_row[ma_kn]
            # Cập nhật Source: Cột AL (Column 38)
            source_batch_updates.append({
                'range': f"AL{source_row_num}:AL{source_row_num}",
                'values': [[new_sys_id]]
            })
            source_sync_count += 1
            print(f"  [🔄 Sync Source] Căn #{ma_hang} ({ma_kn}): Đổi System ID '{old_sys_id}' ➡️ '{new_sys_id}' (Dòng Source: {source_row_num})")
        else:
            print(f"  [🛠️ Pool Only] Căn #{ma_hang}: Đổi System ID '{old_sys_id}' ➡️ '{new_sys_id}'")

    # Đẩy batch update lên Pool
    if pool_batch_updates:
        print(f"\n⚡ Đang ghi đè hàng loạt {len(pool_batch_updates)} System ID mới lên sheet Pool...")
        pool_sheet.batch_update(pool_batch_updates, value_input_option='USER_ENTERED')
        
    # Đẩy batch update lên Source
    if source_batch_updates:
        print(f"⚡ Đang ghi đè hàng loạt {len(source_batch_updates)} System ID mới lên sheet Source...")
        source_sheet.batch_update(source_batch_updates, value_input_option='USER_ENTERED')

    print("\n======================================================================")
    print(f"🏁 ĐÃ HOÀN TẤT: Sửa thành công {fixed_count} dòng trên Pool, đồng bộ khớp {source_sync_count} dòng sang Source.")
    print("======================================================================")

if __name__ == "__main__":
    fix_duplicates()
