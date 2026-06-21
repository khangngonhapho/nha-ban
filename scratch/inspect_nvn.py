# -*- coding: utf-8 -*-
import sqlite3
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
json_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/sheet_data.json"

print("--- SEARCHING IN SQLITE ---")
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Find table names first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print("Tables:", tables)
        
        for table in tables:
            # Let's search for "Nguyễn Văn Nguyễn" in any column
            cursor.execute(f"PRAGMA table_info({table});")
            cols = [col[1] for col in cursor.fetchall()]
            
            # build query to check if any text column contains "Nguyễn Văn Nguyễn"
            where_clauses = []
            for col in cols:
                where_clauses.append(f"CAST({col} AS TEXT) LIKE ?")
            query = f"SELECT * FROM {table} WHERE " + " OR ".join(where_clauses)
            cursor.execute(query, tuple(f"%Nguyễn Văn Nguyễn%" for _ in cols))
            rows = cursor.fetchall()
            if rows:
                print(f"Found in {table}: {len(rows)} rows")
                for r in rows[:3]:
                    # Print cols with values
                    r_dict = dict(zip(cols, r))
                    print(json.dumps(r_dict, ensure_ascii=False, indent=2))
        conn.close()
    except Exception as e:
        print("SQLite error:", e)
else:
    print("DB file does not exist")

print("\n--- SEARCHING IN JSON SHEET DATA ---")
if os.path.exists(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("JSON structure type:", type(data))
        # Find if it is a list or dictionary
        if isinstance(data, list):
            found = []
            for item in data:
                item_str = json.dumps(item, ensure_ascii=False)
                if "Nguyễn Văn Nguyễn" in item_str or "HWMHIMBZINVN" in item_str:
                    found.append(item)
            print(f"Found in JSON list: {len(found)} items")
            for item in found:
                print(json.dumps(item, ensure_ascii=False, indent=2))
        elif isinstance(data, dict):
            # Maybe it has keys like "values" or similar
            for key, val in data.items():
                print(f"Key: {key}, Type: {type(val)}")
                if isinstance(val, list):
                    found = []
                    for item in val:
                        item_str = json.dumps(item, ensure_ascii=False)
                        if "Nguyễn Văn Nguyễn" in item_str or "HWMHIMBZINVN" in item_str:
                            found.append(item)
                    print(f"Found in key '{key}': {len(found)}")
                    for item in found[:2]:
                        print(json.dumps(item, ensure_ascii=False, indent=2))
    except Exception as e:
        print("JSON error:", e)
else:
    print("JSON file does not exist")
