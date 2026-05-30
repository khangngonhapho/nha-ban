import json
import sqlite3
import os

print("--- Checking sheet_data.json ---")
sheet_data_path = 'sheet_data.json'
if os.path.exists(sheet_data_path):
    try:
        with open(sheet_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("Keys in sheet_data.json:", list(data.keys()) if isinstance(data, dict) else type(data))
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, list):
                    print(f"Key: {k}, length: {len(v)}")
                    if len(v) > 0:
                        print("Sample item:", v[0])
                else:
                    print(f"Key: {k}, type: {type(v)}")
    except Exception as e:
        print("Error reading sheet_data.json:", e)
else:
    print("sheet_data.json does not exist")

print("\n--- Checking SQLite Database (raw_archive.db) ---")
db_path = 'raw_archive.db'
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:", tables)
        for table in tables:
            tname = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {tname};")
            cnt = cursor.fetchone()[0]
            print(f"Table: {tname}, rows: {cnt}")
            # print schema
            cursor.execute(f"PRAGMA table_info({tname});")
            cols = cursor.fetchall()
            col_names = [col[1] for col in cols]
            print(f"  Columns: {col_names[:10]} ...")
        conn.close()
    except Exception as e:
        print("Error reading database:", e)
else:
    print("raw_archive.db does not exist")
