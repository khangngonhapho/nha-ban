import os
import sys
import time
import gspread
import unicodedata

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from curator_server import get_google_credentials

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

def remove_accents(input_str):
    if not input_str:
        return ""
    # Chuẩn hóa unicode và loại bỏ dấu tiếng Việt
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    # Thay thế đ/Đ thành d/D
    only_ascii = only_ascii.replace('đ', 'd').replace('Đ', 'D')
    return only_ascii

def normalize_address(ngo, duong):
    ngo_clean = remove_accents(str(ngo)).strip().lower().replace("/", ".").replace(" ", "")
    duong_clean = remove_accents(str(duong)).strip().lower().replace(" ", "")
    if not ngo_clean or not duong_clean:
        return None
    return f"{ngo_clean}@{duong_clean}"

def sync_by_address():
    print("======================================================================")
    print("🔄 BẮT ĐẦU ĐỒNG BỘ MÃ KHANG NGÔ TỪ SOURCE SANG POOL QUA ĐỊA CHỈ")
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
        print("[-] Dữ liệu trống!")
        return
        
    pool_headers = pool_rows[0]
    
    # 1. Định vị cột trên Pool sheet
    ngo_pool_idx = pool_headers.index("Ngõ/Số nhà")
    duong_pool_idx = pool_headers.index("Đường")
    sys_id_pool_idx = pool_headers.index("System ID")
    ma_kn_pool_idx = pool_headers.index("Mã Khang Ngô (ID)")
    ma_hang_pool_idx = pool_headers.index("Mã Hàng")
    
    # 2. Ánh xạ System ID -> (Ngõ, Đường) từ Pool sheet
    pool_sys_id_addr = {}
    for idx, row in enumerate(pool_rows[2:], start=3):
        sys_id = row[sys_id_pool_idx].strip() if len(row) > sys_id_pool_idx else ""
        ngo = row[ngo_pool_idx].strip() if len(row) > ngo_pool_idx else ""
        duong = row[duong_pool_idx].strip() if len(row) > duong_pool_idx else ""
        if sys_id and ngo and duong:
            pool_sys_id_addr[sys_id] = (ngo, duong)

    # 3. Tạo bản đồ địa chỉ đã chuẩn hóa -> Mã Khang Ngô
    # Lấy dữ liệu từ Source sheet làm chuẩn
    # Cột D (index 3) là id (Mã Khang Ngô), Cột AL (index 37) là System ID
    source_ma_kn_idx = 3
    source_sys_id_idx = 37
    
    address_kn_map = {}
    matched_from_source = 0
    
    for idx, row in enumerate(source_rows[2:], start=3):
        ma_kn = row[source_ma_kn_idx].strip() if len(row) > source_ma_kn_idx else ""
        sys_id = row[source_sys_id_idx].strip() if len(row) > source_sys_id_idx else ""
        
        if not ma_kn:
            continue
            
        # Tìm địa chỉ thật của System ID này từ Pool sheet
        if sys_id in pool_sys_id_addr:
            ngo, duong = pool_sys_id_addr[sys_id]
            addr_key = normalize_address(ngo, duong)
            if addr_key:
                address_kn_map[addr_key] = (ma_kn, sys_id, f"{ngo} {duong}")
                matched_from_source += 1

    print(f"  - Đã ánh xạ {matched_from_source} căn từ Source sang địa chỉ thực tế.")
    
    # 4. Quét Pool sheet lần 2, so khớp địa chỉ để tìm dòng cần cập nhật Mã Khang Ngô
    updates = []
    updates_detail = []
    
    for idx, row in enumerate(pool_rows[2:], start=3):
        sys_id = row[sys_id_pool_idx].strip() if len(row) > sys_id_pool_idx else ""
        ngo = row[ngo_pool_idx].strip() if len(row) > ngo_pool_idx else ""
        duong = row[duong_pool_idx].strip() if len(row) > duong_pool_idx else ""
        ma_kn_pool = row[ma_kn_pool_idx].strip() if len(row) > ma_kn_pool_idx else ""
        ma_hang = row[ma_hang_pool_idx].strip() if len(row) > ma_hang_pool_idx else ""
        
        addr_key = normalize_address(ngo, duong)
        if addr_key and addr_key in address_kn_map:
            target_ma_kn, source_sys_id, full_addr = address_kn_map[addr_key]
            
            # Nếu Mã Khang Ngô trong Pool trống hoặc khác biệt
            if not ma_kn_pool or ma_kn_pool != target_ma_kn:
                col_letter = gspread.utils.rowcol_to_a1(idx, ma_kn_pool_idx + 1).split(str(idx))[0]
                updates.append({
                    'range': f"{col_letter}{idx}:{col_letter}{idx}",
                    'values': [[target_ma_kn]]
                })
                updates_detail.append(
                    f"  [📍 Cập nhật] Dòng Pool {idx} (Địa chỉ: {ngo} {duong} | Mã Hàng: {ma_hang} | System ID: {sys_id}): "
                    f"Mã KN cũ '{ma_kn_pool}' ➡️ Mã KN mới '{target_ma_kn}' (Khớp từ Source qua System ID gốc: {source_sys_id})"
                )

    print(f"  - Tìm thấy {len(updates)} dòng Pool cần cập nhật/đồng bộ Mã Khang Ngô.")
    for detail in updates_detail:
        print(detail)
        
    if not updates:
        print("[✅] Không có dòng nào cần cập nhật. Tất cả địa chỉ trùng lặp trong Pool đã được đồng bộ Mã Khang Ngô khớp hoàn hảo!")
        return

    # 5. Tiến hành batch update
    print(f"\n[3/3] Bắt đầu batch update {len(updates)} dòng lên sheet Pool...")
    batch_size = 100
    groups = [updates[i:i + batch_size] for i in range(0, len(updates), batch_size)]
    
    for g_idx, group in enumerate(groups, start=1):
        print(f"  -> Đang đẩy Nhóm {g_idx}/{len(groups)} ({len(group)} dòng)...")
        pool_sheet.batch_update(group, value_input_option='USER_ENTERED')
        time.sleep(1.0)
        
    print("======================================================================")
    print(f"🏁 ĐÃ HOÀN TẤT: Đồng bộ thành công {len(updates)} Mã Khang Ngô theo địa chỉ!")
    print("======================================================================")

if __name__ == "__main__":
    sync_by_address()
