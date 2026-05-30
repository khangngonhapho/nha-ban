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
    
    ss = client.open_by_key('1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0')
    sheet = ss.worksheet('Public')
    values = sheet.get_all_values()
    
    row3 = values[2] # Row 3 data (Trần Quang Diệu)
    
    print("=== ALL RAW VALUES FOR ROW 3 ===")
    print("Total columns returned:", len(row3))
    for idx, val in enumerate(row3):
        print(f"Index {idx} (Col {gspread.utils.rowcol_to_a1(1, idx+1)[:2].replace('1','')}): '{val}'")
            
except Exception as e:
    print("Error:", e)
