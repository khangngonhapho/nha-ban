# -*- coding: utf-8 -*-
"""
Script phụ trợ Bước 4: Làm sạch hoàn toàn Google Sheets Production BDS KhangNgo (US-152) - v5
Làm sạch và co ngắn cả 2 tab 'Pool' và 'Pool_Images' về kích thước tối thiểu (frozen_rows + 1) để chuẩn bị rebuild.
"""

import os
import sys
import json

# Thêm thư mục root dự án vào sys.path để import các module local
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manager

def clear_worksheet_safely(spreadsheet, sheet_name):
    try:
        sheet = spreadsheet.worksheet(sheet_name)
        print(f"  - Đang làm sạch worksheet '{sheet_name}'...")
        
        # 1. Phát hiện số hàng đóng băng (frozen rows) thực tế của sheet
        frozen_rows = sheet.frozen_row_count
        if not frozen_rows or frozen_rows == 0:
            frozen_rows = 1  # Mặc định là dòng 1 chứa Header
            
        print(f"    * Số hàng đóng băng (Header): {frozen_rows}")
        
        # Đọc thử dòng đầu tiên để xác nhận cấu trúc sơ bộ
        first_row = sheet.row_values(1)
        print(f"    * Header hiện tại: {first_row[:5]}...")
        
        # Kích thước tối thiểu của sheet phải là frozen_rows + 1 dòng
        target_rows = frozen_rows + 1
        
        # 2. Resize sheet về đúng target_rows dòng để xóa sạch toàn bộ các dòng khác bên dưới
        print(f"    * Đang co ngắn sheet về đúng {target_rows} dòng...")
        sheet.resize(rows=target_rows)
        
        # 3. Clear sạch dòng trống cuối cùng để an toàn tuyệt đối
        print(f"    * Đang làm sạch ô dữ liệu dòng {target_rows}...")
        sheet.batch_clear([f"A{target_rows}:DZ{target_rows}"])
        
        print(f"  [✅] Đã làm sạch hoàn toàn worksheet '{sheet_name}'.")
    except Exception as e:
        print(f"  [❌] LỖI khi làm sạch worksheet '{sheet_name}': {str(e)}")
        raise e

def clear_production_sheets():
    print("[+] KHỞI ĐỘNG BƯỚC 4: LÀM SẠCH GOOGLE SHEETS PRODUCTION (CẢ TAB POOL & POOL_IMAGES)...")
    
    cfg = manager.load_config()
    sheet_id = cfg.get("sheet_id")
    if not sheet_id:
        print("[-] LỖI: Chưa cấu hình sheet_id trong settings.json")
        sys.exit(1)
        
    print(f"  - Sheet ID Production: {sheet_id}")
    
    creds = manager.get_google_credentials()
    if not creds:
        print("[-] LỖI: Không tìm thấy Google Credentials.")
        sys.exit(1)
        
    try:
        import gspread
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        
        # Làm sạch tab Pool
        clear_worksheet_safely(spreadsheet, "Pool")
        
        # Làm sạch tab Pool_Images
        clear_worksheet_safely(spreadsheet, "Pool_Images")
        
        print("[✅] BƯỚC 4 HOÀN THÀNH XUẤT SẮC! CẢ 2 TAB POOL & POOL_IMAGES ĐÃ SẠCH 100% CẤU HÌNH.")
    except Exception as e:
        print(f"[-] LỖI: Không thể làm sạch Google Sheets: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    clear_production_sheets()
