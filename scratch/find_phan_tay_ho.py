# -*- coding: utf-8 -*-
import sqlite3
import os
import sys

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    db_files = ["raw_archive.db", "raw_archive_v2.db"]
    for db in db_files:
        if not os.path.exists(db):
            print(f"Database {db} does not exist.")
            continue
        print(f"\n=== Database: {db} ===")
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        # Check tables
        tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print(f"Tables: {tables}")
        
        for table in ["listings", "listings_v2", "listings_custom_v2"]:
            if table in tables:
                # search for "Phan Tây Hồ" or "Phan Tay Ho" or "Phan Tây"
                query = f"SELECT tk_id, status, Ngo_So_nha, streetName, streetName FROM {table}"
                try:
                    # Let's get column names
                    cursor.execute(f"PRAGMA table_info({table})")
                    cols = [r[1] for r in cursor.fetchall()]
                    
                    # check which address columns exist
                    search_cols = []
                    for c in ["Duong", "Duong_Pho", "streetName", "Ngo_So_nha", "Dia_Chi_That", "Ten_Duong"]:
                        if c in cols:
                            search_cols.append(c)
                    
                    if not search_cols:
                        continue
                        
                    where_clause = " OR ".join([f"`{c}` LIKE '%Phan Tây Hồ%' OR `{c}` LIKE '%Phan Tay Ho%'" for c in search_cols])
                    sql = f"SELECT tk_id, System_ID, status FROM {table} WHERE {where_clause}"
                    rows = cursor.execute(sql).fetchall()
                    print(f"Table {table} matched rows: {rows}")
                except Exception as e:
                    print(f"Error querying {table}: {e}")
                    
        conn.close()

if __name__ == "__main__":
    main()
