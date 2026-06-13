import sys
import os
import gspread

# Reconfigure stdout to use utf-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Import helper functions from curator_server
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from curator_server import get_google_credentials

def main():
    creds = get_google_credentials()
    if not creds:
        print("Could not load credentials.")
        return
        
    client = gspread.authorize(creds)
    
    print("Connecting to Pool Sheet...")
    pool_spreadsheet = client.open_by_key('1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw')
    pool_sheet = pool_spreadsheet.worksheet("Pool")
    
    headers = pool_sheet.row_values(1)
    print("\nActual Headers in Pool Sheet:")
    for idx, h in enumerate(headers):
        print(f"{idx}: {h}")

if __name__ == '__main__':
    main()
