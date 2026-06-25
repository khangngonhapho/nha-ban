import os
import sys
import json
import sqlite3
import time
from datetime import datetime

# Đảm bảo import được các hàm và cấu hình từ manager.py và pool_lego.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from manager import (
    load_config, get_google_credentials, DB_FILE, get_safe_col_name
)
from pool_lego import init_db, POOL_HEADERS

def restore_database():
    print("======================================================================")
    print("🔄 BẮT ĐẦU KHÔI PHỤC DATABASE SQLITE CỤC BỘ TỪ GOOGLE SHEETS POOL")
    print("👉 Hợp nhất dọn dẹp đôn ảnh nhà thật chuẩn US-055!")
    print("======================================================================")
    
    # 1. Khởi tạo database SQLite sạch sẽ với đầy đủ cấu hình cột
    print("[1/4] Khởi tạo cấu trúc database SQLite rỗng...")
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
            print("  - Đã dọn dẹp file SQLite 0KB cũ.")
        except Exception as e:
            print(f"  - Lỗi dọn dẹp file SQLite: {str(e)}")
            
    init_db()
    
    # 2. Kết nối Google Sheets và tải toàn bộ dữ liệu Pool & Source
    print("\n[2/4] Đang kết nối API và tải dữ liệu từ Google Sheets Pool và Source...")
    creds = get_google_credentials()
    cfg = load_config()
    sheet_id = cfg.get("sheet_id") or "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
    source_sheet_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
    
    if not creds:
        print("[❌ LỖI] Thiếu file credentials.json!")
        return
        
    try:
        import gspread
    except ImportError:
        print("[❌ LỖI] Chưa cài đặt thư viện gspread! Hãy cài đặt bằng lệnh: pip install gspread")
        return
        
    try:
        client = gspread.authorize(creds)
        
        # Đọc dữ liệu từ Pool sheet
        print("  - Đang đọc dữ liệu Google Sheets Pool...")
        spreadsheet = client.open_by_key(sheet_id)
        try:
            sheet = spreadsheet.worksheet("Pool")
        except Exception:
            sheet = spreadsheet.get_worksheet(0)
        all_values = sheet.get_all_values()
        
        # Đọc dữ liệu từ Source sheet
        print("  - Đang đọc dữ liệu Google Sheets Source...")
        try:
            source_spreadsheet = client.open_by_key(source_sheet_id)
            source_sheet = source_spreadsheet.worksheet("Source")
            source_values = source_sheet.get_all_values()
        except Exception as e:
            print(f"[⚠️ WARNING] Không thể đọc dữ liệu từ sheet Source, dữ liệu biên tập sẽ không được hợp nhất: {str(e)}")
            source_values = []
            
    except Exception as e:
        print(f"[❌ LỖI] Lỗi kết nối Google Sheets: {str(e)}")
        return
        
    if len(all_values) < 3:
        print("[-] Không tìm thấy dữ liệu hoặc Sheets Pool rỗng!")
        return
        
    data_rows = all_values[1:] # Dữ liệu bắt đầu từ dòng 2 (index 1)
    print(f"  - Đang phân tích {len(data_rows)} dòng dữ liệu từ Google Sheets Pool...")

    # Xây dựng dictionary từ sheet Source để merge
    source_dict = {}
    if len(source_values) >= 3:
        # Dữ liệu bắt đầu từ dòng 3 (index 2), dòng 2 (index 1) là header snake_case
        for s_row in source_values[2:]:
            # Cột 38 (index 37) là System ID
            if len(s_row) > 37:
                sys_id = s_row[37].strip()
                if sys_id:
                    source_dict[sys_id] = s_row
        print(f"  - Đang lập bản đồ map cho {len(source_dict)} căn đã biên tập từ Source...")

    # 3. Duyệt và ghi nhận vào SQLite cục bộ
    print("\n[3/4] Đang khôi phục dữ liệu vào SQLite và dọn dẹp hình ảnh...")
    
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    cursor = conn.cursor()
    
    restored_count = 0
    repaired_sheets_items = []
    seen_tk_ids = set()
    
    for idx, row_values in enumerate(data_rows, start=3):
        # Tránh các dòng rỗng hoàn toàn hoặc thiếu Mã Hàng
        if len(row_values) < 10 or not row_values[0]:
            continue
            
        # Đóng gói dữ liệu row_values khớp với POOL_HEADERS
        row_dict = {}
        for col_idx, header in enumerate(POOL_HEADERS):
            if col_idx < len(row_values):
                row_dict[header] = row_values[col_idx]
            else:
                row_dict[header] = ""
                
        # Trích xuất tk_id từ Link Gốc hoặc Mã Hàng
        link_goc = row_dict.get("Link Gốc", "")
        ma_hang = row_dict.get("Mã Hàng", "")
        
        tk_id = ""
        if link_goc:
            parts = link_goc.rstrip("/").split("/")
            if parts:
                tk_id = parts[-1].strip()
        if not tk_id and ma_hang:
            tk_id = ma_hang
            
        if not tk_id:
            continue
            
        if tk_id in seen_tk_ids:
            print(f"  - [⚠️ WARNING] Trùng tk_id '{tk_id}' ở dòng Pool {idx} (Mã Hàng: '{ma_hang}'). Bỏ qua dòng này để tránh lỗi UNIQUE constraint.")
            continue
        seen_tk_ids.add(tk_id)
            
        # 1. Đọc 5 ảnh sơ đồ thô/Cloudinary từ các cột sơ đồ
        sodo_imgs = []
        for i in range(1, 6):
            sodo_val = row_dict.get(f"Sơ đồ thửa đất {i}", "")
            if sodo_val and sodo_val.startswith("http"):
                sodo_imgs.append(sodo_val)
                
        # 2. Đọc 15 ảnh thường hiện tại trên Sheets (có nguy cơ lẫn sodo di cư ở đầu)
        interior_imgs = []
        for i in range(1, 16):
            img_val = row_dict.get(f"Ảnh {i}", "")
            if img_val and img_val.startswith("http"):
                interior_imgs.append(img_val)
                
        # Áp dụng thuật toán Zero-Comparison của anh Khang Ngô:
        # Số lượng sodo cào được của căn là N (độ dài sodo_imgs)
        sodo_count = len(sodo_imgs)
        
        # Cắt trực tiếp N hình đầu tiên khỏi cột Ảnh 1-15 trên Sheets (vì sodo bị gán nhầm lên đầu)
        if sodo_count > 0 and len(interior_imgs) >= sodo_count:
            clean_house_links = interior_imgs[sodo_count:]
        else:
            clean_house_links = list(interior_imgs)
            
        # Tạo mảng 15 ảnh thường mới sạch sẽ sau khi dồn
        new_interior_imgs = [""] * 15
        for i_idx, img in enumerate(clean_house_links):
            if i_idx < 15:
                new_interior_imgs[i_idx] = img
                
        # Kiểm tra xem mảng ảnh thường sau khi đôn sạch sodo có khác mảng cũ trên Sheets không
        has_difference = False
        for i in range(15):
            old_val = row_dict.get(f"Ảnh {i+1}", "")
            if old_val != new_interior_imgs[i]:
                has_difference = True
                break
                
        if has_difference:
            # Ghi nhận thay đổi để đồng bộ ngược lên Sheets Pool
            repaired_sheets_items.append({
                "row_idx": idx,
                "row_values": new_interior_imgs
            })
            # Cập nhật lại row_dict các cột Ảnh thường sạch
            for i in range(15):
                row_dict[f"Ảnh {i+1}"] = new_interior_imgs[i]
                
        # Chuẩn bị raw_drive_images đầy đủ cho SQLite (sơ đồ + ảnh sạch) để curation editor của client SPA hoạt động
        reconstructed_drive_images = sodo_imgs + clean_house_links
        
        # Mở rộng: Hợp nhất (Merge) dữ liệu đã biên tập từ sheet Source
        pool_sys_id = row_dict.get("System ID", "").strip()
        status = "raw_complete" # status mặc định
        
        if pool_sys_id and pool_sys_id in source_dict:
            status = "published"
            s_row = source_dict[pool_sys_id]
            
            # Map và ghi đè từ Source sheet sang row_dict
            SOURCE_TO_POOL_MAP = {
                "Mã Khang Ngô (ID)": 3,
                "Tiêu đề Public": 4,
                "DT Thực tế": 5,
                "Số Tầng": 6,
                "Mặt Tiền": 7,
                "Giá Public": 8,
                "Quận": 9,
                "Phường": 10,
                "Phân loại": 11,
                "Hướng": 12,
                "Phân loại Hẻm": 13,
                "Đường trước nhà (m)": 14,
                "Tình trạng nhà": 15,
                "Đánh giá (Admin)": 16,
                "Ngủ trệt (Admin)": 17,
                "CHDV (Admin)": 18,
                "Mô tả Public": 19,
                "Ảnh 1": 20,
                "Ảnh 2": 21,
                "Ảnh 3": 22,
                "Ảnh 4": 23,
                "Ảnh 5": 24,
                "Ảnh 6": 25,
                "Ảnh 7": 26,
                "Ảnh 8": 27,
                "Ảnh 9": 28,
                "Ảnh 10": 29,
                "Last Sync": 30,
                "Phường cũ (AI)": 31,
                "Số phòng ngủ": 32,
                "Số nhà vệ sinh": 33,
                "Đường": 34,
                "Trạng thái Public": 36,
                "System ID": 37,
                "Hình Mặt Tiền": 38
            }
            
            # Các cột văn bản đặc thù của curation, bắt buộc ghi đè
            curated_cols = ["Mã Khang Ngô (ID)", "Tiêu đề Public", "Mô tả Public", "Giá Public", "Trạng thái Public"]
            
            for header, s_col_idx in SOURCE_TO_POOL_MAP.items():
                if len(s_row) > s_col_idx:
                    s_val = s_row[s_col_idx].strip()
                    # Bỏ qua lỗi công thức của Google Sheets
                    if s_val.startswith("#") and s_val.endswith("!"):
                        continue
                        
                    if header in curated_cols:
                        row_dict[header] = s_val
                    elif s_val:
                        row_dict[header] = s_val
                        
        # Chuẩn bị câu lệnh insert vào SQLite
        columns = ["tk_id", "status", "raw_images_tk_json", "raw_drive_images_json"]
        placeholders = ["?", "?", "?", "?"]
        insert_vals = [tk_id, status, json.dumps(reconstructed_drive_images), json.dumps(reconstructed_drive_images)]
        
        for header in POOL_HEADERS:
            safe_col = get_safe_col_name(header)
            columns.append(f"`{safe_col}`")
            placeholders.append("?")
            insert_vals.append(str(row_dict[header]) if row_dict[header] is not None else "")
            
        insert_sql = f"INSERT INTO listings ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(insert_sql, insert_vals)
        restored_count += 1

    conn.commit()
    conn.close()
    print(f"  - [💾 SQLite Complete] Đã khôi phục thành công {restored_count} căn vào SQLite cục bộ!")

    # 4. Đồng bộ ngược lên Google Sheets Pool các cột ảnh thường đã dọn dẹp
    if repaired_sheets_items:
        print(f"\n[4/4] Phát hiện {len(repaired_sheets_items)} căn bị lẫn sơ đồ trong Ảnh 1. Bắt đầu đồng bộ hàng loạt lên Sheets...")
        batch_size = 100
        groups = [repaired_sheets_items[i:i + batch_size] for i in range(0, len(repaired_sheets_items), batch_size)]
        
        synced_count = 0
        for g_idx, group in enumerate(groups, start=1):
            print(f"  -> Đang đẩy Nhóm {g_idx}/{len(groups)} ({len(group)} dòng)...")
            batch_data = []
            for item in group:
                # Ghi đè duy nhất dải ô AO{R}:BC{R} (15 cột ảnh thường từ Ảnh 1 đến Ảnh 15)
                batch_data.append({
                    'range': f"AO{item['row_idx']}:BC{item['row_idx']}",
                    'values': [item['row_values']]
                })
            sheet.batch_update(batch_data, value_input_option='USER_ENTERED')
            synced_count += len(group)
            time.sleep(1.0)
            
        print(f"  - [✅ Sheets Success] Đã đồng bộ chép đè an toàn thành công {synced_count} căn lên Google Sheets Pool!")
    else:
        print("\n[4/4] Tuyệt vời! Không phát hiện căn nào bị lẫn sơ đồ trong Ảnh 1.")

    print("======================================================================")
    print(f"🏁 KHÔI PHỤC DATABASE THÀNH CÔNG: Đã tái tạo {restored_count} căn, sửa sạch {len(repaired_sheets_items)} căn bị lỗi.")
    print("======================================================================")

if __name__ == "__main__":
    restore_database()
