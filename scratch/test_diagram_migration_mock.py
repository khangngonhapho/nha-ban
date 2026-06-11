# -*- coding: utf-8 -*-
import sqlite3
import json
import os
import sys

# Ensure PYTHONPATH is set to project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pool_lego
import manager

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    print("=== STARTING MOCK DIAGRAM MIGRATION TEST ===")
    
    # 1. Initialize mock database
    db_file = "test_raw_archive_v2.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        
    # Set settings.json and mock DB_FILE in manager
    manager.DB_FILE = db_file
    pool_lego.get_db_file = lambda: db_file
    
    pool_lego.init_db(db_file=db_file)
    
    tk_id = "mock-tk-id"
    
    # Create mock crawled data
    crawled_data = {
        "System_ID": "SYS-MOCK-123",
        "Ma_Hang": "TK-MOCK",
        "Noi_dung_chinh": "Mock House detail",
        "Mo_ta_chi_tiet": "Mock detail description",
        "Gia_chao": "12.5",
        "DT_Thuc_te": "60",
        "DT_Tren_so": "60",
        "So_Tang": "4",
        "Mat_Tien": "4.0",
        "Chieu_dai": "15.0",
        "Sơ đồ thửa đất 1": "http://partner-tk.com/sodo1.jpg",
        "Sơ đồ thửa đất 2": "http://partner-tk.com/sodo2.jpg",
        "Last_Crawl": "12/06/2026 01:30:00",
        "status": "raw_text",
        "raw_images_tk_ordered": [
            "http://partner-tk.com/sodo1.jpg",
            "http://partner-tk.com/interior1.jpg",
            "http://partner-tk.com/sodo2.jpg",
            "http://partner-tk.com/interior2.jpg",
            "http://partner-tk.com/interior3.jpg"
        ]
    }
    
    interior_images = [
        "http://partner-tk.com/interior1.jpg",
        "http://partner-tk.com/interior2.jpg",
        "http://partner-tk.com/interior3.jpg"
    ]
    
    # 2. Save raw to sqlite
    print("[*] Saving mock raw data and images...")
    pool_lego.save_raw_to_sqlite(tk_id, crawled_data, interior_images, db_file=db_file)
    
    # Verify raw listings_images state
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    raw_images = cursor.execute("SELECT image_url, role, sequence_index, cloudinary_url FROM listings_images WHERE tk_id = ? ORDER BY sequence_index", (tk_id,)).fetchall()
    print("[+] Raw images in listings_images before migration (ordered by sequence_index):")
    for img, role, seq, cld in raw_images:
        print(f"  - Seq: {seq} | URL: {img} | Role: {role} | Cloudinary: {cld}")
    conn.close()
    
    # 3. Mock download and upload functions
    manager.download_image_with_retry = lambda url, headers: b"dummy_image_data"
    manager.upload_image_to_cloudinary = lambda data, filename, cloud_name, api_key, api_secret, folder: f"https://res.cloudinary.com/{cloud_name}/image/upload/{filename}"
    manager.load_config = lambda: {
        "cloudinary_cloud_name": "test_cloud",
        "cloudinary_api_key": "test_key",
        "cloudinary_api_secret": "test_secret"
    }
    
    # 4. Run image migration
    print("\n[*] Running image migration thread...")
    manager.run_image_migration_thread(limit=None, cookie="dummy", target_tk_id=tk_id)
    
    # 5. Verify listings_images after migration
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    migrated_images = cursor.execute("SELECT image_url, role, sequence_index, cloudinary_url FROM listings_images WHERE tk_id = ? ORDER BY sequence_index", (tk_id,)).fetchall()
    
    print("\n[+] Migrated images in listings_images after migration (ordered by sequence_index):")
    diagram_migrated = []
    interior_migrated = []
    ordered_check = []
    for img, role, seq, cld in migrated_images:
        print(f"  - Seq: {seq} | URL: {img} | Role: {role} | Cloudinary: {cld}")
        ordered_check.append(img)
        if role == "diagram":
            diagram_migrated.append(cld)
        elif role == "interior":
            interior_migrated.append(cld)
            
    # Verify listings_v2 table state
    row = cursor.execute("SELECT status, raw_drive_images_json, raw_images_tk_json FROM listings_v2 WHERE tk_id = ?", (tk_id,)).fetchone()
    status, drive_json, raw_tk_json = row
    drive_links = json.loads(drive_json)
    raw_tk_list = json.loads(raw_tk_json)
    
    print("\n[+] listings_v2 table state:")
    print(f"  - status: {status}")
    print(f"  - raw_drive_images_json: {drive_json}")
    print(f"  - raw_images_tk_json: {raw_tk_json}")
    
    conn.close()
    
    # Assertions
    # Grouped expectation: interiors first, then diagrams
    expected_order = [
        "http://partner-tk.com/interior1.jpg",
        "http://partner-tk.com/interior2.jpg",
        "http://partner-tk.com/interior3.jpg",
        "http://partner-tk.com/sodo1.jpg",
        "http://partner-tk.com/sodo2.jpg"
    ]
    assert ordered_check == expected_order, f"The sequence in listings_images must match grouped order: {expected_order}"
    assert raw_tk_list == expected_order, f"raw_images_tk_json must match grouped order: {expected_order}"
    
    assert len(diagram_migrated) == 2, "Should have 2 diagram images"
    assert all(cld is not None and cld.startswith("https://res.cloudinary.com") for cld in diagram_migrated), "All diagrams must have cloudinary links"
    assert len(interior_migrated) == 3, "Should have 3 interior images"
    assert all(cld is not None and cld.startswith("https://res.cloudinary.com") for cld in interior_migrated), "All interior images must have cloudinary links"
    assert status == "raw_complete", "Status should be raw_complete"
    assert len(drive_links) == 5, "raw_drive_images_json should contain all 5 migrated images (both diagram and interior)"
    
    print("\n[✅ SUCCESS] Mock Diagram Migration Test (including grouped sequence check) passed successfully!")
    
    # Clean up test DB with garbage collection to release file handles on Windows
    import gc
    gc.collect()
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
        except PermissionError as e:
            print(f"[⚠️ WARNING] Could not remove test DB file due to Windows file lock: {e}")

if __name__ == "__main__":
    main()
