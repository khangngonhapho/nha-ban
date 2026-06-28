import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for db_name in ['raw_archive.db', 'raw_archive_v2.db']:
    if os.path.exists(db_name):
        print(f"=== Database: {db_name} ===")
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in c.fetchall()]
        print("  Tables:", tables)
        for tbl in tables:
            c.execute(f"PRAGMA table_info({tbl})")
            cols = [r[1] for r in c.fetchall()]
            print(f"    Table '{tbl}': {cols[:15]}...")
            
            # Print row count
            c.execute(f"SELECT COUNT(*) FROM {tbl}")
            cnt = c.fetchone()[0]
            print(f"      Total rows: {cnt}")
            
            # If table is listings or listings_v2, see if any column has json or raw
            for col in cols:
                if 'json' in col.lower() or 'raw' in col.lower():
                    # check how many non-empty
                    c.execute(f"SELECT COUNT(*) FROM {tbl} WHERE `{col}` IS NOT NULL AND `{col}` != ''")
                    non_empty = c.fetchone()[0]
                    print(f"      Column '{col}' has {non_empty} non-empty rows")
                    if non_empty > 0:
                        c.execute(f"SELECT `{col}` FROM {tbl} WHERE `{col}` IS NOT NULL AND `{col}` != '' LIMIT 1")
                        sample = c.fetchone()[0]
                        print(f"        Sample: {str(sample)[:150]}...")
        conn.close()
