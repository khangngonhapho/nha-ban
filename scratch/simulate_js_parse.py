# -*- coding: utf-8 -*-
import requests
import json
import re
import sys

output_lines = []
def print_out(msg):
    output_lines.append(str(msg))

sheet_id = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0'
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:json"

try:
    response = requests.get(url)
    text = response.text
    print_out(f"Response status: {response.status_code}")
    print_out(f"Response length: {len(text)}")
    
    match = re.search(r'google\.visualization\.Query\.setResponse\((.*)\);', text)
    if not match:
        match = re.search(r'/\*O_o\*/\s*google\.visualization\.Query\.setResponse\((.*)\);', text)
        
    if match:
        json_data = json.loads(match.group(1))
        rows = json_data['table']['rows']
        print_out(f"Total rows on public sheet: {len(rows)}")
        
        target_row = None
        for idx, r in enumerate(rows):
            cells = r.get('c', [])
            row_str = " | ".join([str(c.get('v') if c else '') for c in cells])
            if "Nguyễn Văn Nguyễn" in row_str:
                target_row = r
                print_out(f"Found target row at index {idx}")
                break
                
        if target_row:
            cells = target_row.get('c', [])
            print_out(f"Row cells length: {len(cells)}")
            
            def cv(cell):
                if not cell:
                    return ''
                v = cell.get('v')
                f = cell.get('f')
                if v is not None:
                    return v
                if f is not None:
                    return f
                return ''
                
            jsonUiVal = ''
            for i in range(len(cells) - 1, -1, -1):
                val = str(cv(cells[i]))
                print_out(f"Index {i}: value={repr(val)}")
                if val and val.strip().startswith('{') and val.strip().endswith('}'):
                    jsonUiVal = val
                    print_out(f"--> Found JSON_UI at index {i}: {jsonUiVal}")
                    break
                    
            if jsonUiVal:
                try:
                    parsed = json.loads(jsonUiVal)
                    print_out(f"Parsed JSON_UI: {parsed}")
                    print_out(f"Criteria_Duong_truoc_nha value: {parsed.get('Criteria_Duong_truoc_nha')}")
                except Exception as e:
                    print_out(f"Failed to parse JSON_UI: {e}")
            else:
                print_out("JSON_UI NOT FOUND in row!")
        else:
            print_out("Target row not found in rows!")
    else:
        print_out("Could not parse gviz response")
except Exception as ex:
    print_out(f"Global exception: {ex}")

with open('scratch/simulate_output.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(output_lines))

print("Simulation completed.")
