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
    
    row2 = values[1]
    
    print(f"=== ALL ROW 2 HEADERS (Total columns: {len(row2)}) ===")
    for idx, h in enumerate(row2):
        print(f"Col {idx+1} ({gspread.utils.rowcol_to_a1(1, idx+1)[:3].replace('1','')}): '{h}'")
            
except Exception as e:
    print("Error:", e)
