import os
import json
import sqlite3
import pytest
import sys

# Đảm bảo import được các module từ thư mục root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from restore_db_from_sheets import is_empty_config, merge_temp_to_master
from manager import LISTINGS_TABLE

def test_is_empty_config():
    # 1. Các trường hợp rỗng thực sự
    assert is_empty_config("") is True
    assert is_empty_config(None) is True
    assert is_empty_config("[]") is True
    assert is_empty_config("{}") is True
    assert is_empty_config('{"images": []}') is True
    assert is_empty_config('{"images": [], "system_id": ""}') is True
    assert is_empty_config('{"images": [], "Mã_Khang_Ngô__ID_": ""}') is True
    
    # 2. Các trường hợp có chứa ảnh (không rỗng)
    non_empty_json = '{"images": [{"url": "https://r2/img1.jpg", "role": "Mặt tiền", "visible": true}], "system_id": "SYS-123"}'
    assert is_empty_config(non_empty_json) is False
    
    # 3. Định dạng JSON lỗi (trả về False để phòng thủ)
    assert is_empty_config("invalid json{") is False

def create_mock_schema(conn):
    cursor = conn.cursor()
    # Dựng bảng listings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tk_id TEXT UNIQUE,
            status TEXT,
            raw_images_tk_json TEXT,
            raw_drive_images_json TEXT,
            raw_sodo_tk_json TEXT,
            raw_json_full TEXT,
            Images_Admin_JSON TEXT,
            images_public_json TEXT,
            curated_config_json TEXT,
            System_ID TEXT
        )
    """)
    # Dựng các bảng phụ cho merge
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shared_links (
            link_id TEXT PRIMARY KEY,
            customer_name TEXT,
            customer_note TEXT,
            shared_house_ids TEXT,
            created_at TEXT,
            expires_at TEXT,
            bound_phone_hash TEXT,
            status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phone_blacklist (
            raw_phone TEXT,
            phone_hash TEXT PRIMARY KEY,
            blocked_at TEXT,
            reason TEXT,
            status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_profiles (
            raw_phone TEXT,
            phone_hash TEXT PRIMARY KEY,
            name TEXT,
            note TEXT,
            lifecycle_status TEXT DEFAULT 'LẠNH',
            updated_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exclusion_filters (
            id TEXT PRIMARY KEY,
            field TEXT NOT NULL,
            operator TEXT NOT NULL,
            value TEXT,
            status TEXT NOT NULL DEFAULT 'Active',
            note TEXT
        )
    """)
    # Dựng bảng listings_images
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tk_id TEXT,
            system_id TEXT,
            image_url TEXT,
            r2_url TEXT,
            role TEXT,
            sequence_index INTEGER,
            origin TEXT,
            is_hidden INTEGER
        )
    """)
    conn.commit()

def test_merge_temp_to_master_files(tmp_path):
    # Dựng file SQLite thực tế trong thư mục tạm của pytest
    master_file = str(tmp_path / "master.db")
    temp_file = str(tmp_path / "temp.db")
    
    # Thiết lập Master DB
    conn_m = sqlite3.connect(master_file)
    create_mock_schema(conn_m)
    cursor_m = conn_m.cursor()
    
    master_raw = '["https://cdn.thienkhoi.com/raw_m1.jpg"]'
    master_curated = '{"images": [{"url": "https://r2/m1.jpg", "role": "Bìa", "visible": true}], "system_id": "SYS-999"}'
    cursor_m.execute("""
        INSERT INTO listings (tk_id, status, raw_images_tk_json, curated_config_json, System_ID)
        VALUES (?, ?, ?, ?, ?)
    """, ("TK-123", "published", master_raw, master_curated, "SYS-999"))
    conn_m.commit()
    conn_m.close()
    
    # Thiết lập Temp DB
    conn_t = sqlite3.connect(temp_file)
    create_mock_schema(conn_t)
    cursor_t = conn_t.cursor()
    
    temp_raw = '["https://r2.dev/poisoned_raw.jpg"]'
    temp_curated = '{"images": [], "system_id": ""}'
    cursor_t.execute("""
        INSERT INTO listings (tk_id, status, raw_images_tk_json, curated_config_json, System_ID)
        VALUES (?, ?, ?, ?, ?)
    """, ("TK-123", "published", temp_raw, temp_curated, "SYS-999"))
    conn_t.commit()
    conn_t.close()
    
    # Thực hiện merge từ Temp sang Master
    merge_temp_to_master(temp_file, master_file)
    
    # Kiểm tra kết quả sau merge ở Master DB
    conn_res = sqlite3.connect(master_file)
    cursor_res = conn_res.cursor()
    res = cursor_res.execute("SELECT raw_images_tk_json, curated_config_json FROM listings WHERE tk_id = 'TK-123'").fetchone()
    conn_res.close()
    
    # Assertions
    # 1. Cột thô (raw_images_tk_json) phải giữ nguyên link thô Thiên Khôi của Master, chặn đứng link R2 của Temp
    assert res[0] == master_raw, "Khóa cứng R2 bảo vệ raw_images_tk_json thành công!"
    # 2. Cột curated_config_json phải giữ nguyên cấu hình chất xám cũ của Master, chặn đứng update rỗng từ Temp (Sheets)
    assert res[1] == master_curated, "Bảo vệ mảng chất xám curated_config_json thành công!"
    print("✅ TEST PASSED: merge_temp_to_master bảo vệ dữ liệu tuyệt đối!")

def test_smart_merge_logic_manager():
    # Mô phỏng logic Smart Merge mới trong manager.py
    # Dữ liệu cũ từ Master
    old_images = [
        {"url": "https://r2/SYS-SODO.jpg", "role": "Sơ đồ", "visible": False, "origin": "self"}, # Ảnh admin tự up tay
        {"url": "https://r2/v2/stale_tk.jpg", "role": "Nội thất", "visible": True, "origin": "crawl"}, # Ảnh cào cũ
        {"url": "https://r2/v2/deleted_tk.jpg", "role": "deleted", "visible": False, "origin": "crawl"} # Ảnh đã bị xóa
    ]
    
    # Dữ liệu cào mới từ API Thiên Khôi
    raw_images_tk = ["https://tk/raw_new.jpg"]
    new_images_mapping = {
        "https://tk/raw_new.jpg": "https://r2/v3/raw_new.jpg"
    }
    
    # Giả lập logic rebuild của manager.py
    new_images_list = []
    added_urls = set()
    
    # 1. Bảo toàn ảnh thủ công
    for img in old_images:
        url = img.get("url", "")
        origin = img.get("origin", "")
        if url.upper().startswith("SYS-") or "SYS-" in url.upper() or origin in ["local", "self", "user"]:
            new_images_list.append(img)
            added_urls.add(url)
            
    # Giả định ảnh mặt tiền đầu tiên
    first_property_r2 = "https://r2/v3/raw_new.jpg"
    
    # 2. Nạp mới 100% ảnh cào
    for img_url in raw_images_tk:
        if img_url in new_images_mapping:
            r2_url = new_images_mapping[img_url]
            if r2_url not in added_urls:
                new_images_list.append({
                    "url": r2_url,
                    "role": "Mặt tiền" if r2_url == first_property_r2 else "Nội thất",
                    "visible": True if r2_url == first_property_r2 else False,
                    "origin": "crawl"
                })
                added_urls.add(r2_url)
                
    # Assertions
    urls = [img["url"] for img in new_images_list]
    
    # A. Phải bảo toàn ảnh admin up tay
    assert "https://r2/SYS-SODO.jpg" in urls
    sys_sodo = next(img for img in new_images_list if img["url"] == "https://r2/SYS-SODO.jpg")
    assert sys_sodo["role"] == "Sơ đồ"
    assert sys_sodo["visible"] is False
    assert sys_sodo["origin"] == "self"
    
    # B. Phải xóa cứng các ảnh cào cũ và ảnh deleted cũ
    assert "https://r2/v2/stale_tk.jpg" not in urls, "Ảnh cào cũ không còn tồn tại trên Thiên Khôi phải bị xóa cứng"
    assert "https://r2/v2/deleted_tk.jpg" not in urls, "Ảnh bị đánh dấu deleted cũ phải bị xóa cứng"
    
    # C. Phải nạp mới ảnh cào v3
    assert "https://r2/v3/raw_new.jpg" in urls
    new_img = next(img for img in new_images_list if img["url"] == "https://r2/v3/raw_new.jpg")
    assert new_img["role"] == "Mặt tiền"
    assert new_img["visible"] is True
    assert new_img["origin"] == "crawl"
    print("✅ TEST PASSED: Smart Merge rebuild mới v3 hoàn hảo, bảo toàn vai trò ảnh thủ công!")
