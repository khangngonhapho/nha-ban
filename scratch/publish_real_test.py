# -*- coding: utf-8 -*-
"""
Script chạy đồng bộ thực tế một căn lên 3 file Google Sheets của PO
"""

import os
import sys
import json
import sqlite3

# Thêm thư mục cha để import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import manager
from pool_lego import publish_listing

def main():
    tk_id = "3d296527-12f8-4796-b759-c501ca421f6b"
    db_file = "raw_archive_v2.db"
    
    print(f"=== TIẾN HÀNH DI CƯ HÌNH ẢNH SANG R2 VÀ ĐỒNG BỘ CĂN {tk_id} ===")
    
    # Kích hoạt di cư hình ảnh sang R2 trước để cập nhật listings_images và listings_custom_v2
    manager.run_image_migration_thread(limit=1, cookie=None, target_tk_id=tk_id)
    
    print(f"\n=== TIẾN HÀNH ĐỒNG BỘ LÊN GOOGLE SHEETS THỰC TẾ CĂN {tk_id} ===")
    get_google_credentials = manager.get_google_credentials
    load_config = manager.load_config
    add_log_message = print
    
    res = publish_listing(tk_id, get_google_credentials, load_config, add_log_message, db_file=db_file)
    print("\nKết quả đồng bộ:", json.dumps(res, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    main()
