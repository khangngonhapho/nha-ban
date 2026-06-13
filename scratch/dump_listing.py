# -*- coding: utf-8 -*-
import sqlite3
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('raw_archive_v2.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
row = cursor.execute("SELECT * FROM listings_v2 WHERE tk_id = ?", ('3d296527-12f8-4796-b759-c501ca421f6b',)).fetchone()

if row:
    d = dict(row)
    print("Listing details for 3d296527-12f8-4796-b759-c501ca421f6b:")
    for k in sorted(d.keys()):
        val = d[k]
        if k in ['raw_images_tk_json', 'raw_drive_images_json', 'curated_config_json']:
            # Try to print length of JSON instead of full text to keep it readable
            try:
                parsed = json.loads(val)
                print(f"  {k}: [JSON list/dict with {len(parsed)} items]")
            except Exception:
                print(f"  {k}: {val}")
        else:
            print(f"  {k}: {repr(val)}")
else:
    print("Listing not found!")
conn.close()
