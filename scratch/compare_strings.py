# -*- coding: utf-8 -*-
import json
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# 1. Read option from settings.json
with open('settings.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)
    
options = cfg["json_ui_filters"][0]["options"]
option_val = ""
for opt in options:
    if "Ngõ ngách" in opt:
        option_val = opt
        break

print(f"Option in settings.json: {repr(option_val)}")
print("Char codes:", [ord(c) for c in option_val])

# 2. Read value from sqlite
conn = sqlite3.connect('raw_archive.db')
cur = conn.cursor()
row = cur.execute("SELECT JSON_UI FROM listings WHERE tk_id = '3acfcaeb-5304-4129-8c39-842a85610de9'").fetchone()
db_val = ""
if row and row[0]:
    js = json.loads(row[0])
    db_val = js.get("Criteria_Duong_truoc_nha", "")

print(f"Value in SQLite: {repr(db_val)}")
print("Char codes:", [ord(c) for c in db_val])

# Compare
print("Are they identical?", db_val == option_val)
conn.close()
