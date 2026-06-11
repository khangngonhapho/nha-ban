# -*- coding: utf-8 -*-
import os
import sys
import json
import sqlite3
from datetime import datetime
import random

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pool_lego

def run_test():
    db_file = "test_schema_v2.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        
    print("[*] Simulating settings.json configuration loading to force active_pool_system = Pool2...")
    original_exists = os.path.exists
    def mock_exists(path):
        if path == "settings.json":
            return True
        return original_exists(path)
        
    original_open = open
    def mock_open(path, *args, **kwargs):
        if path == "settings.json":
            import io
            return io.StringIO('{"active_pool_system": "Pool2"}')
        return original_open(path, *args, **kwargs)
        
    os.path.exists = mock_exists
    # Override open inside pool_lego temporarily
    pool_lego.open = mock_open
    
    # 1. Initialize DB
    print("[*] Initializing database...")
    pool_lego.init_db(db_file)
    
    # Restore overrides
    os.path.exists = original_exists
    del pool_lego.open

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 2. Check table listings_v2 columns
    cursor.execute("PRAGMA table_info(listings_v2)")
    columns = {row[1] for row in cursor.fetchall()}
    
    # Flat image columns MUST NOT exist in listings_v2
    image_cols = ["Anh_1", "Anh_25", "Hinh_Hem_1", "Hinh_Hem_10", "Hinh_Mat_Tien", "So_do_thua_dat_1", "So_do_thua_dat_5"]
    for col in image_cols:
        assert col not in columns, f"[❌ FAILED] Found flat image column {col} in listings_v2!"
    print("[✅] Passed: Flat image columns are not present in listings_v2.")
    
    # Rich columns MUST exist in listings_v2
    rich_cols = [
        "isSigned", "status_nguon", "commissionAgent", "ownerSideUserId", "certificateSeries",
        "latitude", "longitude", "placeName", "streetName", "bedrooms", "restrooms",
        "balconies", "sidewalk", "behindOpenSpace", "sideOpenSpace", "minimumRoadWidth",
        "createdAt", "updatedAt", "commissionType", "commissionValue", "isDispute",
        "createdAtSigned", "CCCD_Dau_Chu", "Kenh_tin_TK", "The_tags_TK"
    ]
    for col in rich_cols:
        assert col in columns, f"[❌ FAILED] Missing rich column {col} in listings_v2!"
    print("[✅] Passed: All rich contract and technical metadata columns exist in listings_v2.")
    
    # 3. Simulate saving crawled raw data
    print("[*] Saving mock crawled listing...")
    tk_id = "test-uuid-12345"
    mock_metadata = {
        "Mã Hàng": "TK-XYZ",
        "Tỉnh": "TP Hồ Chí Minh",
        "Quận": "Quận 10",
        "Phường": "Phường 12",
        "Đường": "Nguyễn Tri Phương",
        "Ngõ/Số nhà": "123",
        "Phân loại": "Nhà phố",
        "Nội dung chính": "Nội dung chính",
        "Mô tả chi tiết": "Mô tả chi tiết",
        "Giá chào": "10",
        "Giá Public": "10",
        "DT Thực tế": "50",
        "DT Trên sổ": "50",
        "Số Tầng": "3",
        "Mặt Tiền": "4",
        "Chieu_dai": "12.5",
        "Số phòng ngủ": "3",
        "Số nhà vệ sinh": "3",
        "Hướng": "Đông",
        "Đường trước nhà (m)": "5",
        "Tình trạng nhà": "Mới",
        "Trạng thái": "selling",
        "Tên Chủ Nhà": "Nguyen Van A",
        "Điện thoại 1": "0901234567",
        "Điện thoại Đầu Chủ": "0987654321",
        "Tên Đầu Chủ (Hợp đồng)": "Nguyen Van B",
        "Điểm Facebook": "http://facebook.com/123",
        "Link Gốc": "http://goc",
        "System ID": "SYS-12345",
        "Last Crawl": "11/06/2026",
        
        # English compatibility mapping
        "bedrooms": "3",
        "restrooms": "3",
        "minimumRoadWidth": "5",
        
        # Rich cào fields
        "isSigned": "1",
        "status_nguon": "selling",
        "commissionAgent": "3%",
        "ownerSideUserId": "usr-123",
        "certificateSeries": "cert-123",
        "latitude": "10.77",
        "longitude": "106.68",
        "placeName": "Chung cư",
        "streetName": "Nguyễn Tri Phương",
        "balconies": "1",
        "sidewalk": "2",
        "behindOpenSpace": "1",
        "sideOpenSpace": "0",
        "createdAt": "2026-06-11",
        "updatedAt": "2026-06-11",
        "commissionType": "percent",
        "commissionValue": "3",
        "isDispute": "0",
        "createdAtSigned": "2026-06-11",
        "CCCD_Dau_Chu": "123456789",
        "Kenh_tin_TK": "Zalo",
        "The_tags_TK": "vip, hot",
        
        # Sơ đồ thửa đất
        "Sơ đồ thửa đất 1": "http://sodo1",
        "Sơ đồ thửa đất 2": "http://sodo2",
        
        # Flat image key that is NOT in listings_v2 database (testing the dynamic column filter)
        "Anh_1": "http://flatimage1",
        "Anh_2": "http://flatimage2"
    }
    
    mock_images = ["http://img1", "http://img2"]
    
    # Save listing
    pool_lego.save_raw_to_sqlite(tk_id, mock_metadata, mock_images, db_file)
    
    # 4. Verify saved data
    row = cursor.execute("SELECT * FROM listings_v2 WHERE tk_id = ?", (tk_id,)).fetchone()
    assert row is not None, "[❌ FAILED] Row not saved in listings_v2!"
    
    d_row = dict(row)
    print("\n[*] Verifying listings_v2 saved attributes:")
    print(f"  - System_ID: {d_row['System_ID']} (Expected: SYS-12345)")
    print(f"  - isSigned: {d_row['isSigned']} (Expected: 1)")
    print(f"  - CCCD_Dau_Chu: {d_row['CCCD_Dau_Chu']} (Expected: 123456789)")
    print(f"  - Kenh_tin_TK: {d_row['Kenh_tin_TK']} (Expected: Zalo)")
    print(f"  - The_tags_TK: {d_row['The_tags_TK']} (Expected: vip, hot)")
    print(f"  - bedrooms: {d_row['bedrooms']} (Expected: 3)")
    print(f"  - Chieu_dai: {d_row['Chieu_dai']} (Expected: 12.5)")
    
    assert d_row['System_ID'] == 'SYS-12345'
    assert d_row['isSigned'] == '1'
    assert d_row['CCCD_Dau_Chu'] == '123456789'
    assert d_row['Kenh_tin_TK'] == 'Zalo'
    assert d_row['The_tags_TK'] == 'vip, hot'
    assert d_row['bedrooms'] == '3'
    assert d_row['Chieu_dai'] == '12.5'
    
    # 5. Check listings_images table
    print("\n[*] Verifying listings_images saved images:")
    images = cursor.execute("SELECT * FROM listings_images WHERE tk_id = ? ORDER BY sequence_index", (tk_id,)).fetchall()
    for img in images:
        print(f"  - Image: {img['image_url']} | Role: {img['role']} | Sequence: {img['sequence_index']}")
        
    assert len(images) == 4, f"[❌ FAILED] Expected 4 images in listings_images, found {len(images)}"
    assert images[0]['role'] == 'interior', "First image role should be interior"
    assert images[1]['role'] == 'interior', "Second image role should be interior"
    assert images[2]['role'] == 'diagram', "Third image role should be diagram"
    assert images[3]['role'] == 'diagram', "Fourth image role should be diagram"
    
    print("\n[✅ SUCCESS] All schema v2 and dynamic column filtering test assertions passed successfully!")
    conn.close()
    
    # Cleanup
    if os.path.exists(db_file):
        os.remove(db_file)

if __name__ == "__main__":
    run_test()
