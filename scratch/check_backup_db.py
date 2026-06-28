import sqlite3
import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

backup_db = "Backup DB/raw_archiveJun25.db"
if os.path.exists(backup_db):
    print(f"=== Database: {backup_db} ===")
    conn = sqlite3.connect(backup_db)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print("  Tables:", tables)
    if 'listings' in tables:
        c.execute("PRAGMA table_info(listings)")
        cols = [r[1] for r in c.fetchall()]
        print("  Columns:", cols[:15])
        
        c.execute("SELECT COUNT(*) FROM listings")
        total = c.fetchone()[0]
        print(f"  Total listings: {total}")
        
        if 'raw_json_full' in cols:
            c.execute("SELECT COUNT(*) FROM listings WHERE raw_json_full IS NOT NULL AND raw_json_full != ''")
            non_empty = c.fetchone()[0]
            print(f"  Column 'raw_json_full' has {non_empty} non-empty rows")
            if non_empty > 0:
                c.execute("SELECT tk_id, raw_json_full FROM listings WHERE raw_json_full IS NOT NULL AND raw_json_full != '' LIMIT 1")
                row = c.fetchone()
                print(f"    Sample tk_id: {row[0]}")
                print(f"    Sample raw_json_full length: {len(row[1])}")
                try:
                    data = json.loads(row[1])
                    print("      Keys in JSON:", list(data.keys()))
                    media = data.get('media', [])
                    print(f"      Media count: {len(media)}")
                    if media:
                        print("      First media item:", media[0])
                except Exception as e:
                    print("      Error parsing JSON:", e)
    conn.close()
else:
    print(f"=== {backup_db} not found ===")
