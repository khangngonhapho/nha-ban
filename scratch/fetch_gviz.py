import urllib.request
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

SHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json'

print(f"Fetching: {url}")
try:
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
    
    print(f"Fetched {len(html)} bytes.")
    
    # Extract JSON from JSONP
    match = re.search(r'google\.visualization\.Query\.setResponse\((.*)\);', html)
    if not match:
        # Try checking for alternative JSONP formats or raw response
        print("Standard JSONP pattern not found. Raw start:")
        print(html[:200])
        # Save raw output to file for inspection
        with open("scratch/gviz_raw.txt", "w", encoding="utf-8") as f:
            f.write(html)
        sys.exit(1)
        
    json_str = match.group(1)
    data = json.loads(json_str)
    
    print("GViz API returned status:", data.get('status'))
    if 'errors' in data:
        print("Errors returned:", data.get('errors'))
        
    table = data.get('table', {})
    rows = table.get('rows', [])
    cols = table.get('cols', [])
    print(f"Number of columns: {len(cols)}")
    print(f"Number of rows: {len(rows)}")
    
    # Let's inspect column headers
    print("Columns:")
    for i, col in enumerate(cols):
        print(f"  Col {i}: id={col.get('id')}, label='{col.get('label')}', type={col.get('type')}")
        
    # Test parsing some rows like index.html does
    print("\nParsing first 5 rows:")
    def cv(cell):
        if not cell:
            return ""
        # cell can be a dict
        v = cell.get('v')
        f = cell.get('f')
        return str(v if v is not None else (f if f is not None else ""))

    for index, r in enumerate(rows[:5]):
        cells = r.get('c', [])
        # print sizes and elements
        print(f"Row {index}: number of cells = {len(cells)}")
        if len(cells) > 0:
            print(f"  Col 0 (ID): {cv(cells[0])}")
        if len(cells) > 1:
            print(f"  Col 1 (Title): {cv(cells[1])}")
        
except Exception as e:
    print("Error:", e)
