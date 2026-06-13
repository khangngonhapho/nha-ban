import gspread
import os
import sys
from google.oauth2 import service_account

sys.stdout = open("scratch/inspect_pool_col_headers_output.txt", "w", encoding="utf-8")

service_account_file = "khangngo-admin-a96043c2f638.json"
sheet_id = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'

if os.path.exists(service_account_file):
    try:
        scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.worksheet("Pool")
        
        print(f"Pool sheet col_count: {sheet.col_count}")
        
        headers = sheet.row_values(1)
        print(f"Headers count: {len(headers)}")
        for i, h in enumerate(headers):
            print(f"  Col {i+1} ({gspread.utils.rowcol_to_a1(1, i+1).replace('1', '')}): {repr(h)}")
            
    except Exception as e:
        print("Error:")
        import traceback
        traceback.print_exc()
else:
    print(f"Service account file {service_account_file} not found.")

sys.stdout.close()
