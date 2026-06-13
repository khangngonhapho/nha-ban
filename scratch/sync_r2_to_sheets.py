import sys
import os
import sqlite3
import gspread
import time

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
import manager

def main():
    creds = manager.get_google_credentials()
    if not creds:
        print("[❌ LỖI] Không thể load Google Credentials.")
        return
        
    client = gspread.authorize(creds)
    source_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
    db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
    
    if not os.path.exists(db_file):
        print(f"[❌ LỖI] Không tìm thấy file Database SQLite tại: {db_file}")
        return
        
    print("[⚡] Kết nối SQLite và tải dữ liệu ảnh R2...")
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Load all rows from SQLite
    db_rows = cursor.execute("SELECT * FROM listings").fetchall()
    conn.close()
    
    # Build mapping dictionary by Ma_Khang_Ngo_ID and System_ID
    db_by_ma_kn = {}
    db_by_sys_id = {}
    for r in db_rows:
        d = dict(r)
        ma_kn = d.get("Ma_Khang_Ngo_ID")
        sys_id = d.get("System_ID")
        if ma_kn:
            db_by_ma_kn[ma_kn.strip()] = d
        if sys_id:
            db_by_sys_id[sys_id.strip()] = d
            
    print(f"[✅] Đã tải {len(db_rows)} bản ghi từ SQLite.")
    
    # 2. Open Google Sheets
    print(f"[⚡] Đang mở Google Sheet Source (v1) [ID: {source_id}]...")
    try:
        ss = client.open_by_key(source_id)
        sheet = ss.worksheet("Source")
        all_rows = sheet.get_all_values()
        print(f"[✅] Đã tải {len(all_rows)} dòng từ Google Sheets.")
    except Exception as e:
        print(f"[❌ LỖI] Không thể mở hoặc đọc sheet Source: {e}")
        return
        
    # Col indices (0-indexed)
    # Col 4 is index 3 (id / Ma_Khang_Ngo_ID)
    # Col 38 is index 37 (System_ID)
    # Col 21-30 are indices 20-29 (anh_1 to anh_10)
    # Col 39 is index 38 (Hinh_Mat_Tien / Hình Mặt Tiền)
    # Col 42-46 are indices 41-45 (anh_11 to anh_15)
    
    img_col_mapping = {
        20: "Anh_1",
        21: "Anh_2",
        22: "Anh_3",
        23: "Anh_4",
        24: "Anh_5",
        25: "Anh_6",
        26: "Anh_7",
        27: "Anh_8",
        28: "Anh_9",
        29: "Anh_10",
        38: "Hinh_Mat_Tien",
        41: "Anh_11",
        42: "Anh_12",
        43: "Anh_13",
        44: "Anh_14",
        45: "Anh_15"
    }
    
    cells_to_update = []
    skipped_count = 0
    updated_listings_count = 0
    
    print("[⚡] Bắt đầu so sánh và quét các ô ảnh cũ...")
    
    # Skip headers (rows 1 and 2, which are indices 0 and 1)
    for r_idx, row_vals in enumerate(all_rows[2:], start=3):
        if len(row_vals) < 4:
            continue
            
        ma_kn = row_vals[3].strip()
        sys_id = row_vals[37].strip() if len(row_vals) > 37 else ""
        
        # Look up in DB
        db_record = None
        if ma_kn and ma_kn in db_by_ma_kn:
            db_record = db_by_ma_kn[ma_kn]
        elif sys_id and sys_id in db_by_sys_id:
            db_record = db_by_sys_id[sys_id]
            
        if not db_record:
            skipped_count += 1
            continue
            
        listing_updated = False
        # Compare columns
        for sheet_col_idx, db_col_name in img_col_mapping.items():
            if sheet_col_idx >= len(row_vals):
                continue
                
            sheet_val = row_vals[sheet_col_idx].strip()
            db_val = db_record.get(db_col_name)
            
            # If spreadsheet has cloudinary and db has R2, we update
            if sheet_val and "cloudinary.com" in sheet_val:
                if db_val and "r2.dev" in db_val:
                    # Create cell update object (row is 1-indexed)
                    cell = gspread.Cell(r_idx, sheet_col_idx + 1, db_val)
                    cells_to_update.append(cell)
                    listing_updated = True
                    
        if listing_updated:
            updated_listings_count += 1
            
    print(f"[📊] Kết quả quét:")
    print(f"  - Số căn cần cập nhật ảnh R2: {updated_listings_count}")
    print(f"  - Tổng số ô ảnh cần cập nhật: {len(cells_to_update)}")
    print(f"  - Số dòng bỏ qua (không khớp mã hoặc không có ảnh R2): {skipped_count}")
    
    if not cells_to_update:
        print("[✅] Không có ô nào cần cập nhật.")
        return
        
    print(f"[⚡] Đang thực hiện ghi đè hàng loạt {len(cells_to_update)} ô lên Google Sheets...")
    
    # gspread batch update
    # Split into chunks of 500 cells to avoid API payload size limits
    chunk_size = 500
    for i in range(0, len(cells_to_update), chunk_size):
        chunk = cells_to_update[i:i + chunk_size]
        print(f"  -> Đang đẩy batch {i // chunk_size + 1} ({len(chunk)} ô)...")
        try:
            sheet.update_cells(chunk, value_input_option='USER_ENTERED')
            print("     [✅] Đã hoàn thành batch.")
            time.sleep(2)  # Avoid Google API quota limits
        except Exception as e:
            print(f"     [❌ LỖI] Thất bại khi ghi batch: {e}")
            
    print("\n[🏁 HOÀN TẤT] Đồng bộ Google Sheets Source (v1) hoàn tất!")

if __name__ == '__main__':
    main()
