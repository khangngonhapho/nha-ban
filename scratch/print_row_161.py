# -*- coding: utf-8 -*-
import requests
import json
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

sheet_id = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0'
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json"

response = requests.get(url)
text = response.text
match = re.search(r'google\.visualization\.Query\.setResponse\((.*)\);', text)

if match:
    json_data = json.loads(match.group(1))
    rows = json_data['table']['rows']
    
    target_row = None
    for idx, r in enumerate(rows):
        cells = r.get('c', [])
        row_str = " | ".join([str(c.get('v') if c else '') for c in cells])
        if "Nguyễn Văn Nguyễn" in row_str:
            target_row = r
            print(f"Found target row at index {idx}")
            break
            
    if target_row:
        cells = target_row.get('c', [])
        for i, cell in enumerate(cells):
            val = cell.get('v') if cell else None
            formatted = cell.get('f') if cell else None
            print(f"Col {i}: v={repr(val)}, f={repr(formatted)}")
else:
    print("Could not load")
