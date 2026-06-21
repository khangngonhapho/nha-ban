# -*- coding: utf-8 -*-
import sqlite3
import json
import os
import sys

db_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/inspect_nvn_details_out.txt", "w", encoding="utf-8") as out:
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table});")
                cols = [col[1] for col in cursor.fetchall()]
                
                # check if there's any row containing "HWMHIMBZINVN"
                where_clauses = []
                for col in cols:
                    where_clauses.append(f"CAST({col} AS TEXT) = ?")
                query = f"SELECT * FROM {table} WHERE " + " OR ".join(where_clauses)
                cursor.execute(query, tuple("HWMHIMBZINVN" for _ in cols))
                rows = cursor.fetchall()
                if rows:
                    out.write(f"\n================ TABLE: {table} ({len(rows)} rows) ================\n")
                    for row in rows:
                        r_dict = dict(zip(cols, row))
                        out.write(json.dumps(r_dict, ensure_ascii=False, indent=2) + "\n")
            conn.close()
        except Exception as e:
            out.write(f"SQLite error: {e}\n")
    else:
        out.write("DB file does not exist\n")
print("Done writing details to inspect_nvn_details_out.txt")
