# -*- coding: utf-8 -*-
"""
Script kiểm tra nhanh dữ liệu trên Google Sheets cả 2 tab 'Pool' và 'Pool_Images' (US-152)
"""

import os
import sys
import json

# Thêm thư mục root dự án vào sys.path để import các module local
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manager

def check_sheets_data():
    print("[+] KHỞI ĐỘNG KIỂM TRA DỮ LIỆU GOOGLE SHEETS...")
    
    cfg = manager.load_config()
    sheet_id = cfg.get("sheet_id")
    if not sheet_id:
        print("[-] LỖI: Chưa cấu hình sheet_id trong settings.json")
        sys.exit(1)
        
    creds = manager.get_google_credentials()
    if not creds:
        print("[-] LỖI: Không tìm thấy credentials.")
        sys.exit(1)
        
    try:
        import gspread
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        
        # 1. Kiểm tra tab Pool
        sheet_pool = spreadsheet.worksheet("Pool")
        pool_rows = sheet_pool.get_all_values()
        print(f"\n📊 Tab 'Pool' (Tổng số dòng: {len(pool_rows)}):")
        headers = pool_rows[0]
        important_cols = ["Mã Hàng", "System ID", "Mã Khang Ngô (ID)", "Đường", "Giá chào", "Last Sync"]
        col_indices = {}
        for col_name in important_cols:
            if col_name in headers:
                col_indices[col_name] = headers.index(col_name)
                
        for idx in range(min(5, len(pool_rows))):
            row = pool_rows[idx]
            print(f"  [Dòng {idx+1}]")
            for col_name, col_idx in col_indices.items():
                val = row[col_idx] if col_idx < len(row) else ""
                print(f"    - {col_name}: {val}")
                
        # 2. Kiểm tra tab Pool_Images
        sheet_img = spreadsheet.worksheet("Pool_Images")
        img_rows = sheet_img.get_all_values()
        print(f"\n📸 Tab 'Pool_Images' (Tổng số dòng: {len(img_rows)}):")
        
        for idx in range(min(5, len(img_rows))):
            row = img_rows[idx]
            # In ngắn gọn 4 cột đầu
            parts = row[:5]
            print(f"  [Dòng {idx+1}] {parts}")
            
        print("\n[✅] ĐÃ HOÀN THÀNH ĐỐI CHIẾU THÀNH CÔNG.")
    except Exception as e:
        print(f"[-] LỖI: Không thể kiểm tra Sheets: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    check_sheets_data()
