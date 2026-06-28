import os
import sys
import sqlite3
import gspread

# Ensure imports work from the parent directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from manager import get_google_credentials, load_config

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("======================================================================")
    print("🔄 BẮT ĐẦU ĐỒNG BỘ HƯỚNG TỪ POOL SANG SOURCE CHO CÁC CĂN HIỆN CÓ")
    print("======================================================================")
    
    # 1. Kết nối Google Sheets
    print("[1/3] Đang kết nối Google Sheets...")
    creds = get_google_credentials()
    cfg = load_config()
    
    pool_sheet_id = cfg.get("sheet_id") or "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
    source_sheet_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
    
    client = gspread.authorize(creds)
    
    print("  - Đang đọc dữ liệu từ sheet Pool...")
    pool_spreadsheet = client.open_by_key(pool_sheet_id)
    sheet_pool = pool_spreadsheet.worksheet("Pool")
    pool_rows = sheet_pool.get_all_values()
    
    print("  - Đang đọc dữ liệu từ sheet Source...")
    source_spreadsheet = client.open_by_key(source_sheet_id)
    sheet_source = source_spreadsheet.worksheet("Source")
    source_rows = sheet_source.get_all_values()
    
    if len(pool_rows) < 2 or len(source_rows) < 2:
        print("[❌ LỖI] Bảng dữ liệu trống.")
        sys.exit(1)
        
    # Map System_ID (index 72) và raw_id (index 55) -> Hướng gốc (Pool cột R - index 17)
    pool_key_to_huong = {}
    for row in pool_rows[1:]:
        if len(row) > 17:
            huong = row[17].strip()
            if huong and huong != '-':
                # Key by System_ID (index 72)
                if len(row) > 72 and row[72].strip():
                    pool_key_to_huong[row[72].strip()] = huong
                # Key by raw ID (index 55)
                if len(row) > 55 and row[55].strip():
                    pool_key_to_huong[row[55].strip()] = huong
                # Key by Ma_Hang (index 0)
                if row[0].strip():
                    pool_key_to_huong[row[0].strip()] = huong
                
    print(f"  - Tìm thấy {len(pool_key_to_huong)} khóa khớp trong sheet Pool.")

    # 2. Quét sheet Source để tìm các căn cần cập nhật
    print("[2/3] Quét các dòng trong sheet Source để tìm Hướng trống...")
    updates_sheets = [] # Danh sách các dict: {'range': ..., 'values': ...}
    updates_sqlite = [] # Danh sách các tuple: (huong, tk_id, ma_hang)
    
    for idx, row in enumerate(source_rows[1:], start=2):
        if len(row) > 12:
            huong_source = row[12].strip()
            
            # Nếu Hướng ở Source trống, "-" hoặc "Chưa xác định"
            if not huong_source or huong_source in ['-', '', 'Chưa xác định']:
                # Lấy khóa liên kết
                raw_id = row[3].strip() if len(row) > 3 else ""
                system_id = row[37].strip() if len(row) > 37 else ""
                ma_hang = row[0].strip()
                
                huong_pool = None
                if system_id and system_id in pool_key_to_huong:
                    huong_pool = pool_key_to_huong[system_id]
                elif raw_id and raw_id in pool_key_to_huong:
                    huong_pool = pool_key_to_huong[raw_id]
                elif ma_hang and ma_hang in pool_key_to_huong:
                    huong_pool = pool_key_to_huong[ma_hang]
                    
                if huong_pool:
                    print(f"  -> Căn ở dòng {idx} (Mã gốc: {raw_id}, System ID: {system_id}): Hướng Source đang trống. Cập nhật thành: {huong_pool}")
                    updates_sheets.append({
                        'range': f'M{idx}',
                        'values': [[huong_pool]]
                    })
                    updates_sqlite.append((huong_pool, raw_id, ma_hang))
                    
    # 3. Cập nhật Google Sheets và SQLite
    if updates_sheets:
        print(f"[3/3] Thực hiện cập nhật {len(updates_sheets)} căn...")
        
        # Cập nhật Google Sheets
        chunk_size = 100
        for i in range(0, len(updates_sheets), chunk_size):
            chunk = updates_sheets[i:i+chunk_size]
            sheet_source.batch_update(chunk, value_input_option='USER_ENTERED')
            print(f"  - Đã cập nhật thành công {len(chunk)} căn trên Google Sheet Source.")
            
        # Cập nhật SQLite
        conn = sqlite3.connect('raw_archive.db')
        cursor = conn.cursor()
        for huong, raw_id, ma_hang in updates_sqlite:
            cursor.execute("""
                UPDATE listings 
                SET custom_huong = ? 
                WHERE tk_id = ? OR Ma_Hang = ?
            """, (huong, raw_id, ma_hang))
        conn.commit()
        conn.close()
        print("  - Đã cập nhật thành công custom_huong vào cơ sở dữ liệu SQLite.")
        
        print("======================================================================")
        print(f"🏁 HOÀN TẤT: Đã cập nhật hướng thành công cho {len(updates_sqlite)} căn trên Source!")
        print("======================================================================")
    else:
        print("[3/3] Không tìm thấy căn nào cần cập nhật.")

if __name__ == '__main__':
    main()
