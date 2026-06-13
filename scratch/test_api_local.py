import urllib.request
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

SHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0'

def test_api_logic():
    print("Testing serverless API logic...")
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req).read().decode('utf-8')
        
        # Extract JSON
        match = re.search(r'google\.visualization\.Query\.setResponse\((.*)\);', res)
        if not match:
            print("Failed to parse JSONP")
            return
        
        json_str = match.group(1)
        data = json.loads(json_str)
        rows = data['table']['rows']
        
        print(f"Total rows fetched: {len(rows)}")
        
        def cv(cell):
            if not cell:
                return ''
            v = cell.get('v')
            f = cell.get('f')
            return str(v if v is not None else (f if f is not None else ''))
            
        full_list = []
        for index, r in enumerate(rows):
            # Check if r has 'c'
            if 'c' not in r or r['c'] is None:
                print(f"Row {index} has no 'c' property!")
                continue
                
            cells = r['c']
            # Mimic filter: r.c[0] && r.c[0].v
            if len(cells) > 0 and cells[0] and cells[0].get('v'):
                # Mimic map
                try:
                    # Accessing index 34
                    sys_id = cv(cells[34]) if len(cells) > 34 else ''
                    
                    house = {
                        'id': cv(cells[0]) if len(cells) > 0 else '',
                        't': cv(cells[1]) if len(cells) > 1 else '',
                        'dt': cv(cells[2]) if len(cells) > 2 else '',
                        'tang': cv(cells[3]) if len(cells) > 3 else '',
                        'gia': cv(cells[5]) if len(cells) > 5 else '',
                        'phuong': cv(cells[7]) if len(cells) > 7 else '',
                        'duong_truoc_nha': cv(cells[10]) if len(cells) > 10 else '',
                        'system_id': sys_id or str(index + 1)
                    }
                    full_list.append(house)
                except Exception as row_err:
                    print(f"Error mapping row {index}: {row_err}")
                    
        print(f"Successfully mapped {len(full_list)} houses.")
        
    except Exception as e:
        print("API test failed:", e)

test_api_logic()
