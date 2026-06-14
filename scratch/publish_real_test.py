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
    
    print(f"=== TIẾN HÀNH ĐỒNG BỘ CĂN {tk_id} LÊN GOOGLE SHEETS THỰC TẾ ===")
    
    get_google_credentials = manager.get_google_credentials
    load_config = manager.load_config
    add_log_message = print
    
    res = publish_listing(tk_id, get_google_credentials, load_config, add_log_message, db_file=db_file)
    print("\nKết quả đồng bộ:", json.dumps(res, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    main()
