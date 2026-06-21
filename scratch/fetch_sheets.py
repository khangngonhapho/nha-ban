# -*- coding: utf-8 -*-
import requests
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

SHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0'
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json"

print(f"Fetching GViz data from public sheet: {url}")
r = requests.get(url)
if r.status_code == 200:
    # GViz wraps response in google.visualization.Query.setResponse(...)
    m = re.search(r'google\.visualization\.Query\.setResponse\((.*)\);', r.text)
    if m:
        data_json = m.group(1)
        data = json.loads(data_json)
        rows = data['table']['rows']
        cols = [c['label'] if c else '' for c in data['table']['cols']]
        print(f"Total rows fetched: {len(rows)}")
        print(f"Cols: {cols}")
        
        # Let's search for "HWMHIMBZINVN"
        for i, row in enumerate(rows):
            cells = [cell['v'] if (cell and 'v' in cell) else '' for cell in row['c']]
            cells_str = " ".join(str(c) for c in cells)
            if "HWMHIMBZINVN" in cells_str or "Nguyễn Văn Nguyễn" in cells_str:
                print(f"\nFound row {i+2} in public sheet (0-indexed row index {i}):")
                for col_idx, cell in enumerate(row['c']):
                    val = cell['v'] if (cell and 'v' in cell) else ''
                    lbl = cols[col_idx] if col_idx < len(cols) else f"Col{col_idx}"
                    print(f"  {lbl or f'Col{col_idx}'}: {val}")
                
                # Check for json_ui string in the cells of this row
                for cell in row['c']:
                    val = str(cell['v'] if (cell and 'v' in cell) else '')
                    if val.strip().startswith('{') and val.strip().endswith('}'):
                        print(f"Found JSON string: {val}")
    else:
        print("Failed to parse GViz response wrapper")
else:
    print(f"Failed to fetch public sheet: {r.status_code}")
