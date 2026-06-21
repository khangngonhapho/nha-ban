# -*- coding: utf-8 -*-
import sqlite3
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    # We want to inspect listings table
    cursor.execute("PRAGMA table_info(listings);")
    cols = [col[1] for col in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM listings;")
    rows = cursor.fetchall()
    
    matching_listings = []
    for r in rows:
        r_dict = dict(zip(cols, r))
        
        # Parse JSON_UI
        json_ui_str = r_dict.get('JSON_UI') or '{}'
        try:
            json_ui = json.loads(json_ui_str)
        except Exception:
            json_ui = {}
            
        val = json_ui.get('Criteria_Duong_truoc_nha') or ''
        if 'Ngõ ngách (2 - 2.5m)' in val:
            matching_listings.append(r_dict)
            
    print(f"Total listings matching 'Ngõ ngách (2 - 2.5m)': {len(matching_listings)}")
    for m in matching_listings:
        print(f"ID: {m.get('Ma_Khang_Ngo_ID')} | Address: {m.get('Ngo_So_nha')} {m.get('Duong')} | District: {m.get('Quan')} | Phuong: {m.get('Phuong')} | Status: {m.get('status')} | Tinh_trang: {m.get('Tinh_trang_nha')}")
    conn.close()
else:
    print("Database does not exist")
