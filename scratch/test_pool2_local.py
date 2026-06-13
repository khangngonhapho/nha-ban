# -*- coding: utf-8 -*-
"""
Script kiểm thử tự động cho CSDL và Cào thô Pool2 cục bộ (US-089A)
"""

import os
import sys
import json
import sqlite3

# Thêm đường dẫn thư mục cha để import pool_lego
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pool_lego
from pool_lego import init_db, save_raw_to_sqlite, get_db_file

def run_test():
    print("=== BẮT ĐẦU KIỂM THỬ CSDL CỤC BỘ POOL2 ===")
    
    # 1. Đảm bảo cấu hình active_pool_system đang là Pool2
    config_file = "../settings.json"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            if cfg.get("active_pool_system") != "Pool2":
                print("[!] Cảnh báo: settings.json không phải Pool2. Tiến hành tự chuyển đổi để test...")
                cfg["active_pool_system"] = "Pool2"
                with open(config_file, 'w', encoding='utf-8') as wf:
                    json.dump(cfg, wf, indent=4, ensure_ascii=False)
                    
    # 2. Khởi tạo DB mới
    db_file = "test_raw_archive_v2.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"[*] Đã xóa file DB test cũ: {db_file}")
        
    print(f"[*] Đang khởi tạo CSDL: {db_file}...")
    init_db(db_file)
    
    # Kiểm tra xem các bảng đã được tạo chưa
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"[+] Các bảng được tạo: {tables}")
    
    expected_tables = ["listings_v2", "listings_images", "listings_custom_v2"]
    for t in expected_tables:
        if t not in tables:
            print(f"[❌ FAIL] Thiếu bảng: {t}")
            conn.close()
            sys.exit(1)
        print(f"  - {t}: OK")
        
    # 3. Chạy thử save_raw_to_sqlite với dữ liệu giả lập
    tk_id = "test-uuid-listing-12345"
    mock_metadata = {
        "Quận": "Quận 10",
        "Phường": "Phường 12",
        "Đường": "Nguyễn Tri Phương",
        "Ngõ/Số nhà": "123/4",
        "Giá chào": "15.5",
        "DT Thực tế": "85",
        "DT Trên sổ": "80",
        "Số Tầng": "4",
        "Mặt Tiền": "4.5",
        "Hướng": "Đông Nam",
        "Sơ đồ thửa đất 1": "https://lh3.googleusercontent.com/d/sodo_file_id_1",
        "Sơ đồ thửa đất 2": "https://lh3.googleusercontent.com/d/sodo_file_id_2",
        "Criteria_Duong_truoc_nha": "Ngõ ba gác",
        "Criteria_Noi_that": "Cơ bản",
        "Criteria_Thang_may": "Không có"
    }
    mock_images = [
        "https://lh3.googleusercontent.com/d/img_file_id_1",
        "https://lh3.googleusercontent.com/d/img_file_id_2",
        "https://lh3.googleusercontent.com/d/img_file_id_3"
    ]
    
    print("\n[*] Đang chạy lưu trữ dữ liệu cào thô giả lập...")
    save_raw_to_sqlite(tk_id, mock_metadata, mock_images, db_file)
    
    # 4. Kiểm chứng dữ liệu trong listings_v2
    row_listing = cursor.execute("SELECT * FROM listings_v2 WHERE tk_id = ?", (tk_id,)).fetchone()
    if not row_listing:
        print("[❌ FAIL] Không tìm thấy dữ liệu trong listings_v2")
        conn.close()
        sys.exit(1)
        
    # Chuyển thành dict để verify
    cursor.execute("PRAGMA table_info(listings_v2)")
    cols = [r[1] for r in cursor.fetchall()]
    row_dict = dict(zip(cols, row_listing))
    
    print("[✅ PASS] listings_v2 lưu trữ thành công!")
    print(f"  - System ID tự sinh: {row_dict.get('System_ID')}")
    print(f"  - Mã Hàng tự sinh: {row_dict.get('Ma_Hang')}")
    print(f"  - Quận: {row_dict.get('Quan')}")
    print(f"  - Phường: {row_dict.get('Phuong')}")
    print(f"  - Criteria Đường: {row_dict.get('Criteria_Duong_truoc_nha')}")
    print(f"  - Criteria Thang máy: {row_dict.get('Criteria_Thang_may')}")
    
    # 5. Kiểm chứng dữ liệu trong listings_images
    rows_images = cursor.execute("SELECT * FROM listings_images WHERE tk_id = ?", (tk_id,)).fetchall()
    print(f"\n[+] Số lượng dòng hình ảnh đã lưu trong listings_images: {len(rows_images)} dòng (Kỳ vọng: 5 dòng)")
    
    if len(rows_images) != 5:
        print(f"[❌ FAIL] Số lượng dòng hình ảnh không đúng: {len(rows_images)}")
        conn.close()
        sys.exit(1)
        
    # Phân bổ vai trò
    roles = {}
    for r in rows_images:
        url, role = r[2], r[4]
        roles[role] = roles.get(role, 0) + 1
        print(f"  - URL: {url} | Role: {role}")
        
    if roles.get("diagram") != 2:
        print("[❌ FAIL] Số lượng ảnh sơ đồ (diagram) không đúng")
        conn.close()
        sys.exit(1)
        
    if roles.get("interior") != 3:
        print("[❌ FAIL] Số lượng ảnh nội thất (interior) không đúng")
        conn.close()
        sys.exit(1)
        
    print("[✅ PASS] Phân tách hình ảnh thô và sơ đồ thành dòng: OK")
    
    # 6. Kiểm thử lọc trùng khi quét lại (recrawl)
    print("\n[*] Đang chạy lưu trữ lại (giả lập quét lại)...")
    # Thêm 1 ảnh mới và sơ đồ mới vào metadata
    mock_metadata["Sơ đồ thửa đất 3"] = "https://lh3.googleusercontent.com/d/sodo_file_id_3"
    mock_images.append("https://lh3.googleusercontent.com/d/img_file_id_4")
    
    # In kiểm tra
    print(f"  - Mock images gửi đi: {mock_images}")
    
    save_raw_to_sqlite(tk_id, mock_metadata, mock_images, db_file)
    
    # In kiểm tra trong listings_images sau khi lưu
    db_images = cursor.execute("SELECT image_url, role FROM listings_images WHERE tk_id = ?", (tk_id,)).fetchall()
    print("  - Ảnh thực tế trong DB sau recrawl:")
    for r in db_images:
        print(f"    + {r[0]} ({r[1]})")
        
    rows_images_recrawl = cursor.execute("SELECT * FROM listings_images WHERE tk_id = ?", (tk_id,)).fetchall()
    print(f"[+] Số lượng ảnh sau khi cào lại: {len(rows_images_recrawl)} dòng (Kỳ vọng: 7 dòng)")
    
    if len(rows_images_recrawl) != 7:
        print("[❌ FAIL] Tránh trùng lặp ảnh thất bại.")
        conn.close()
        sys.exit(1)
        
    print("[✅ PASS] Cơ chế lọc trùng và cộng dồn ảnh hoạt động hoàn hảo!")
    
    conn.close()
    
    # Xóa DB test sau khi hoàn tất
    if os.path.exists(db_file):
        os.remove(db_file)
        
    print("\n=== HOÀN THÀNH TẤT CẢ KIỂM THỬ VỚI KẾT QUẢ: THÀNH CÔNG ===")

if __name__ == "__main__":
    run_test()
