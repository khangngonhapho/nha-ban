import sys
import os
import traceback

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath(os.getcwd()))

try:
    from curator_server import get_google_credentials
    import gspread
    
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    
    print("Connecting to spreadsheet...")
    ss = client.open_by_key('1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE')
    print("Worksheets:", [w.title for w in ss.worksheets()])
    
    sheet = ss.worksheet('Source')
    values = sheet.get_all_values()
    print("Fetched values. Total rows:", len(values))
    
    headers = values[0] # Row 1 headers
    
    # Find matching row for TQD
    tqd_row = None
    row_num = -1
    for idx, row in enumerate(values[1:]):
        if len(row) > 37 and (row[37] == 'SYS-MP752STS-B3' or row[3] == 'AWOIZTIDQT'):
            tqd_row = row
            row_num = idx + 2
            break
            
    if tqd_row:
        print(f"=== DETAILS FOR SOURCE ROW {row_num} (Trần Quang Diệu) ===")
        for idx, h in enumerate(headers):
            val = tqd_row[idx] if idx < len(tqd_row) else ""
            print(f"Col {idx+1} ({gspread.utils.rowcol_to_a1(1, idx+1)[:2].replace('1','')}): '{h}' -> '{val}'")
    else:
        print("TQD row not found in Source sheet!")
            
except Exception as e:
    print("Error occurred:")
    traceback.print_exc()
