import sqlite3
import os
import json

project_root = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"

def inspect_db(db_name):
    db_path = os.path.join(project_root, db_name)
    if not os.path.exists(db_path):
        print(f"[-] Database {db_name} does not exist.")
        return
        
    print(f"\n[+] Inspecting Database: {db_name}")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check tables
        tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print("    Tables:", tables)
        
        for table in tables:
            count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"    Table '{table}' row count: {count}")
            if count > 0:
                # Get last inserted row
                # Let's see what columns are in the table
                columns = [col[1] for col in cursor.execute(f"PRAGMA table_info({table})").fetchall()]
                print(f"    Columns in '{table}': {columns[:10]} ... ({len(columns)} columns)")
                
                # Check if there is a primary key or rowid
                last_row = cursor.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT 1").fetchone()
                if last_row:
                    row_dict = dict(last_row)
                    # Print summary of the last row
                    print(f"    Last Row in '{table}':")
                    for k, v in row_dict.items():
                        # Truncate long values
                        v_str = str(v)
                        if len(v_str) > 100:
                            v_str = v_str[:100] + "..."
                        print(f"      {k}: {v_str}")
        conn.close()
    except Exception as e:
        print(f"    [-] Error inspecting {db_name}: {e}")

inspect_db("raw_archive.db")
inspect_db("raw_archive_v2.db")
inspect_db("raw_archive_temp.db")
