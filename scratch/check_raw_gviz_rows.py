import urllib.request
import json
import re

SHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0'
url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json'

try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req).read().decode('utf-8')
    match = re.search(r'google\.visualization\.Query\.setResponse\((.*)\);', res)
    if not match:
        print("Failed to parse JSONP")
        sys.exit(1)
        
    json_str = match.group(1)
    data = json.loads(json_str)
    rows = data['table']['rows']
    
    print(f"Total fetched rows: {len(rows)}")
    for i, r in enumerate(rows):
        if 'c' not in r:
            print(f"Row {i} is MISSING 'c' property!")
        elif r['c'] is None:
            print(f"Row {i} has 'c' as None!")
        elif not isinstance(r['c'], list):
            print(f"Row {i} has 'c' as {type(r['c'])} instead of list!")
        else:
            # Check length of c and content
            cells = r['c']
            if len(cells) == 0:
                print(f"Row {i} has an empty 'c' list!")
            else:
                # Check first cell
                if cells[0] is not None:
                    v = cells[0].get('v')
                    # print(f"Row {i} Col 0: {v}")
                else:
                    print(f"Row {i} Col 0 is None!")
                    
except Exception as e:
    print("Error:", e)
