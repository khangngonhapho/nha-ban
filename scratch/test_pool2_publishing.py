# -*- coding: utf-8 -*-
"""
Script kiểm thử tự động cho Luồng Xuất bản Pool2 sang 3 Sheets (US-089B)
"""

import os
import sys
import json
import sqlite3
import random
from datetime import datetime
from unittest.mock import MagicMock

# Thêm thư mục cha để import pool_lego
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --------------------------------------------------
# MOCK GSPREAD & GOOGLE API
# --------------------------------------------------
class MockWorksheet:
    def __init__(self, title, values=None):
        self.title = title
        self.values = values or []

    def get_all_values(self):
        return [list(row) for row in self.values]

    def col_values(self, col_idx):
        vals = []
        for r in self.values:
            if col_idx - 1 < len(r):
                vals.append(r[col_idx - 1])
            else:
                vals.append("")
        return vals

    def insert_row(self, row_data, index=1, value_input_option='USER_ENTERED'):
        if index - 1 <= len(self.values):
            self.values.insert(index - 1, list(row_data))
        else:
            self.values.append(list(row_data))

    def append_row(self, row_data, value_input_option='USER_ENTERED'):
        self.values.append(list(row_data))

    def update(self, range_name, values, value_input_option='USER_ENTERED'):
        import re
        match = re.search(r'\d+', range_name)
        if match:
            row_idx = int(match.group(0)) - 1
            if row_idx < len(self.values):
                self.values[row_idx] = list(values[0])

    def add_cols(self, num):
        pass

    def insert_cols(self, col_data, col=1):
        # Mock insert column header at first row
        header = col_data[0][0]
        if self.values:
            self.values[0].insert(col - 1, header)
            for r in self.values[1:]:
                r.insert(col - 1, "")

    def update_cell(self, row, col, val):
        while len(self.values) < row:
            self.values.append([])
        while len(self.values[row - 1]) < col:
            self.values[row - 1].append("")
        self.values[row - 1][col - 1] = str(val)

    def update_title(self, new_title):
        self.title = new_title

class MockSpreadsheet:
    def __init__(self, key):
        self.key = key
        self.worksheets_dict = {}

    def worksheet(self, title):
        if title not in self.worksheets_dict:
            self.worksheets_dict[title] = MockWorksheet(title)
        return self.worksheets_dict[title]

    def get_worksheet(self, idx):
        title = f"Sheet{idx+1}"
        if title not in self.worksheets_dict:
            self.worksheets_dict[title] = MockWorksheet(title)
        return self.worksheets_dict[title]

class MockGspreadClient:
    def __init__(self):
        self.spreadsheets = {}

    def open_by_key(self, key):
        if key not in self.spreadsheets:
            self.spreadsheets[key] = MockSpreadsheet(key)
        return self.spreadsheets[key]

# Khởi tạo client giả lập
mock_client = MockGspreadClient()

gspread_mock = MagicMock()
gspread_mock.authorize.return_value = mock_client
gspread_mock.utils = MagicMock()

def mock_rowcol_to_a1(row, col):
    letters = ""
    temp = col
    while temp > 0:
        temp, remainder = divmod(temp - 1, 26)
        letters = chr(65 + remainder) + letters
    return f"{letters}{row}"

gspread_mock.utils.rowcol_to_a1 = mock_rowcol_to_a1
sys.modules['gspread'] = gspread_mock

# --------------------------------------------------
# IMPORT LOGIC SAU KHI MOCK GSPREAD
# --------------------------------------------------
import pool_lego
from pool_lego import init_db, save_raw_to_sqlite, publish_listing

def run_test():
    print("=== BẮT ĐẦU KIỂM THỬ XUẤT BẢN POOL2 SANG 3 SHEETS ===")
    
    # DB test
    db_file = "test_raw_archive_v2.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        
    init_db(db_file)
    
    # 1. Thao tác cào thô và lưu SQLite
    tk_id = "test-uuid-listing-12345"
    mock_metadata = {
        "Quận": "Quận 10",
        "Phường": "Phường 12",
        "Đường": "Tô Hiến Thành",
        "Ngõ/Số nhà": "163/24",
        "Giá chào": "12.5 Tỷ",
        "DT Thực tế": "50",
        "DT Trên sổ": "48",
        "Số Tầng": "3",
        "Mặt Tiền": "4.2",
        "Chiều dài": "12",
        "Hướng": "Đông",
        "Sơ đồ thửa đất 1": "https://cloudinary.com/sodo_1.jpg",
        "Hình Mặt Tiền": "https://cloudinary.com/facade_1.jpg",
        "Hình Hẻm 1": "https://cloudinary.com/alley_1.jpg",
        "Ảnh 1": "https://cloudinary.com/interior_1.jpg",
        "Ảnh 2": "https://cloudinary.com/interior_2.jpg",
        "Criteria_Duong_truoc_nha": "Hẻm ba gác",
        "Criteria_Noi_that": "Đẹp",
        "Criteria_Thang_may": "Không",
        "Dien_thoai_1": "0901234567" # Thông tin PII nhạy cảm
    }
    mock_images = [
        "https://cloudinary.com/sodo_1.jpg",
        "https://cloudinary.com/facade_1.jpg",
        "https://cloudinary.com/alley_1.jpg",
        "https://cloudinary.com/interior_1.jpg",
        "https://cloudinary.com/interior_2.jpg"
    ]
    
    # Thiết lập mock role cho các ảnh cào được
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    print("[*] Ghi dữ liệu thô vào SQLite...")
    save_raw_to_sqlite(tk_id, mock_metadata, mock_images, db_file)
    
    # Gán nhãn vai trò chi tiết cho các hình ảnh trong listings_images để kiểm thử
    cursor.execute("UPDATE listings_images SET role = 'diagram' WHERE image_url = 'https://cloudinary.com/sodo_1.jpg'")
    cursor.execute("UPDATE listings_images SET role = 'facade' WHERE image_url = 'https://cloudinary.com/facade_1.jpg'")
    cursor.execute("UPDATE listings_images SET role = 'alley' WHERE image_url = 'https://cloudinary.com/alley_1.jpg'")
    cursor.execute("UPDATE listings_images SET role = 'interior' WHERE image_url = 'https://cloudinary.com/interior_1.jpg'")
    cursor.execute("UPDATE listings_images SET role = 'interior' WHERE image_url = 'https://cloudinary.com/interior_2.jpg'")
    conn.commit()
    conn.close()

    # Callback giả lập
    get_google_credentials = lambda: MagicMock()
    load_config = lambda: {
        "pool2_raw_sheet_id": "mock_raw_id",
        "pool2_custom_sheet_id": "mock_custom_id",
        "pool2_public_sheet_id": "mock_public_id"
    }
    logs = []
    add_log_message = lambda msg: logs.append(msg)
    
    # 2. Xuất bản lần đầu (Lúc này listings_custom_v2 chưa có dòng cho căn này)
    print("[*] Gọi publish_listing lần đầu (Tự khởi tạo Custom)...")
    res = publish_listing(tk_id, get_google_credentials, load_config, add_log_message, db_file)
    
    if res.get("status") != "success":
        print(f"[❌ FAIL] Xuất bản thất bại: {res.get('message')}")
        print("\nLogs:")
        for log in logs:
            print(f"  {log}")
        sys.exit(1)
        
    print("[✅ PASS] Xuất bản thành công!")
    
    # 3. Kiểm chứng File 1 Raw
    raw_sheet = mock_client.open_by_key("mock_raw_id").worksheet("Listings")
    raw_rows = raw_sheet.get_all_values()
    print(f"[+] File 1 Raw có {len(raw_rows)} dòng (bao gồm header).")
    raw_headers = raw_rows[0]
    raw_data = raw_rows[1]
    
    # Kiểm tra cột curated_config_json tồn tại trên File 1
    if "curated_config_json" not in raw_headers:
        print("[❌ FAIL] Không tìm thấy cột curated_config_json trên File 1 Raw")
        sys.exit(1)
        
    print("  - File 1 Raw: OK")
    
    # 4. Kiểm chứng File 2 Custom
    custom_sheet = mock_client.open_by_key("mock_custom_id").worksheet("Custom")
    custom_rows = custom_sheet.get_all_values()
    custom_headers = custom_rows[0]
    custom_data = custom_rows[1]
    
    # Lấy System_ID của căn nhà
    sys_id_idx = custom_headers.index("System_ID")
    system_id = custom_data[sys_id_idx]
    print(f"  - System ID sinh ra: {system_id}")
    
    # Kiểm tra cột images_metadata_json có chứa ảnh an toàn
    img_meta_idx = custom_headers.index("images_metadata_json")
    img_meta_str = custom_data[img_meta_idx]
    safe_imgs = json.loads(img_meta_str)
    print(f"  - Số lượng ảnh an toàn được lọc mặc định: {len(safe_imgs)}")
    
    # Kiểm tra xem ảnh mặt tiền và sơ đồ có bị loại bỏ khỏi images_metadata_json không
    for img in safe_imgs:
        if "sodo_1.jpg" in img["url"] or "facade_1.jpg" in img["url"]:
            print(f"[❌ FAIL] Rò rỉ ảnh nhạy cảm vào images_metadata_json: {img}")
            sys.exit(1)
            
    print("  - Lọc ảnh an toàn Custom: OK (Đã loại trừ facade & diagram)")
    
    # 5. Kiểm chứng File 3 Public (Sạch PII, rã ảnh, Last updated trước ảnh)
    public_sheet = mock_client.open_by_key("mock_public_id").worksheet("Public")
    public_rows = public_sheet.get_all_values()
    public_headers = public_rows[0]
    public_data = public_rows[1]
    
    # Xác nhận không có cột nhạy cảm trong whitelist Public
    forbidden_cols = ["Dia_Chi_That", "So_Nha", "Dien_thoai_1", "Dien_thoai_Dau_Chu", "Note_Noi_Bo"]
    for col in forbidden_cols:
        if col in public_headers:
            print(f"[❌ FAIL] Cột cấm '{col}' xuất hiện trong sheet Public!")
            sys.exit(1)
            
    print("  - Whitelist bảo mật Public: OK (Không chứa số nhà/SĐT/note nội bộ)")
    
    # Kiểm tra thứ tự: Last updated đứng trước các cột ảnh
    last_updated_idx = public_headers.index("Last updated")
    for idx, header in enumerate(public_headers):
        if header.startswith("Ảnh ") and idx < last_updated_idx:
            print("[❌ FAIL] Phát hiện cột ảnh đứng trước cột 'Last updated'!")
            sys.exit(1)
            
    print("  - Vị trí cột 'Last updated': OK (Đứng trước toàn bộ cột ảnh)")
    
    # Kiểm tra rã ảnh
    img_1_idx = public_headers.index("Ảnh 1")
    img_2_idx = public_headers.index("Ảnh 2")
    img_3_idx = public_headers.index("Ảnh 3")
    
    print(f"  - Ảnh 1: {public_data[img_1_idx]}")
    print(f"  - Ảnh 2: {public_data[img_2_idx]}")
    print(f"  - Ảnh 3: {public_data[img_3_idx]}")
    
    if "alley_1.jpg" not in public_data[img_1_idx] and "interior_1.jpg" not in public_data[img_1_idx]:
        print("[❌ FAIL] Ảnh rã cột Public bị sai hoặc rỗng!")
        sys.exit(1)
        
    print("  - Rã cột ảnh Public: OK")
    
    # 6. Kiểm thử chép đè & Mở rộng cột động (Thêm ảnh thứ 4)
    # Giả lập Admin chỉnh sửa trong listings_custom_v2: thêm 2 tấm ảnh mới (Tổng cộng 5 tấm ảnh an toàn)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    updated_safe_images = [
        {"url": "https://cloudinary.com/alley_1.jpg", "role": "alley"},
        {"url": "https://cloudinary.com/interior_1.jpg", "role": "interior"},
        {"url": "https://cloudinary.com/interior_2.jpg", "role": "interior"},
        {"url": "https://cloudinary.com/interior_new_3.jpg", "role": "interior"},
        {"url": "https://cloudinary.com/interior_new_4.jpg", "role": "interior"}
    ]
    cursor.execute(
        "UPDATE listings_custom_v2 SET images_metadata_json = ?, Gia_Public = '12.0 Tỷ' WHERE System_ID = ?",
        (json.dumps(updated_safe_images), system_id)
    )
    conn.commit()
    conn.close()
    
    print("\n[*] Gọi publish_listing lần hai để kiểm tra cập nhật chép đè và mở rộng cột...")
    logs_v2 = []
    res_v2 = publish_listing(tk_id, get_google_credentials, load_config, lambda m: logs_v2.append(m), db_file)
    
    if res_v2.get("status") != "success":
        print(f"[❌ FAIL] Cập nhật lần 2 thất bại: {res_v2.get('message')}")
        sys.exit(1)
        
    # Đọc lại File 3 Public
    public_rows_v2 = public_sheet.get_all_values()
    public_headers_v2 = public_rows_v2[0]
    public_data_v2 = public_rows_v2[1]
    
    print(f"[+] Số dòng trên sheet Public sau khi update: {len(public_rows_v2)} (Không được tăng dòng, vẫn phải là 2)")
    if len(public_rows_v2) != 2:
        print("[❌ FAIL] Cập nhật chép đè bị sai, gây tăng dòng lặp trong sheet Public!")
        sys.exit(1)
        
    # Kiểm tra xem tiêu đề cột tự động giãn thêm Ảnh 4 và Ảnh 5 ở đuôi sheet
    print(f"[+] Tiêu đề sheet Public sau cập nhật: {public_headers_v2[-5:]}")
    if "Ảnh 4" not in public_headers_v2 or "Ảnh 5" not in public_headers_v2:
        print("[❌ FAIL] Hệ thống không tự động mở rộng cột ảnh thiếu ở đuôi sheet Public!")
        sys.exit(1)
        
    # Kiểm tra giá trị ảnh mới được dàn phẳng
    img_4_idx = public_headers_v2.index("Ảnh 4")
    img_5_idx = public_headers_v2.index("Ảnh 5")
    print(f"  - Ảnh 4: {public_data_v2[img_4_idx]}")
    print(f"  - Ảnh 5: {public_data_v2[img_5_idx]}")
    
    if "interior_new_3.jpg" not in public_data_v2[img_4_idx] or "interior_new_4.jpg" not in public_data_v2[img_5_idx]:
        print("[❌ FAIL] Dữ liệu ảnh mới rã cột bị sai hoặc rỗng!")
        sys.exit(1)
        
    print("[✅ PASS] Cập nhật chép đè & Mở rộng cột ảnh tự động thành công!")
    
    # Dọn dẹp DB test
    if os.path.exists(db_file):
        os.remove(db_file)
        
    print("\n=== TẤT CẢ UNIT TEST GREEN PASS! ===")

if __name__ == '__main__':
    run_test()
