import sqlite3
import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect("raw_archive.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

row = cursor.execute("SELECT * FROM listings ORDER BY id DESC LIMIT 1").fetchone()
d = dict(row)
print("LISTING DATA:")
for k, v in d.items():
    if v is not None:
        print(f"  {k}: {repr(v)}")
    else:
        print(f"  {k}: None")

conn.close()
