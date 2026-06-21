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

# Extract JSON from __gsCallback(...)
match = re.search(r'google\.visualization\.Query\.setResponse\((.*)\);', text)
if not match:
    # Try another pattern just in case
    match = re.search(r'/\*O_o\*/\s*google\.visualization\.Query\.setResponse\((.*)\);', text)

if match:
    json_data = json.loads(match.group(1))
    rows = json_data['table']['rows']
    print(f"Total rows on public sheet: {len(rows)}")
    
    # Let's search for "Nguyễn Văn Nguyễn" or "212.137"
    found = []
    for idx, r in enumerate(rows):
        cells = r.get('c', [])
        # Join all cell values as a string to search
        row_str = " | ".join([str(c.get('v') if c else '') for c in cells])
        if "Nguyễn Văn Nguyễn" in row_str or "212.137" in row_str:
            found.append({
                "row_index": idx,
                "cells": [c.get('v') if c else None for c in cells]
            })
            
    print(f"Found {len(found)} matching rows on public sheet:")
    for f in found:
        print(f"\nRow {f['row_index']}:")
        for i, val in enumerate(f['cells']):
            if val is not None:
                # If it looks like JSON
                val_str = str(val)
                if val_str.strip().startswith('{'):
                    print(f"  Col {i}: {val_str}")
                elif "Nguyễn" in val_str or "212.137" in val_str:
                    print(f"  Col {i}: {val_str}")
                elif i < 15:
                    print(f"  Col {i}: {val_str}")
else:
    print("Could not parse gviz response")
    print(text[:200])
