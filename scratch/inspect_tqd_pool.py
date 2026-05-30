import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.getcwd()))

try:
    from curator_server import get_google_credentials
    import gspread
    
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    # Open Pool BDS
    ss = client.open_by_key('1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw')
    sheet = ss.worksheet('Pool')
    values = sheet.get_all_values()
    
    headers = values[0] # Row 1 headers
    
    # Search for System ID
    sys_id_idx = headers.index('System ID')
    found = False
    for r_idx, row in enumerate(values[1:]):
        row_num = r_idx + 2
        sys_id = row[sys_id_idx].strip()
        if sys_id == 'SYS-MP752STS-B3':
            found = True
            print(f"=== DETAILS FOR POOL ROW {row_num} (SYS-MP752STS-B3) ===")
            for idx, h in enumerate(headers):
                val = row[idx] if idx < len(row) else ""
                # Print image columns and sodo/mat tien
                if 'ảnh' in h.lower() or 'sơ đồ' in h.lower() or 'mặt tiền' in h.lower() or 'hẻm' in h.lower():
                    if val.strip() != "":
                        print(f"  Col {idx+1} (Index {idx}) '{h}': {val}")
            break
            
    if not found:
        print("SYS-MP752STS-B3 not found in Pool sheet!")
        
except Exception as e:
    print("Error:", e)
