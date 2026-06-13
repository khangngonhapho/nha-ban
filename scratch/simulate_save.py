import gspread
import os
import sys
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

sys.stdout = open("scratch/simulate_save_output.txt", "w", encoding="utf-8")

service_account_file = "khangngo-admin-a96043c2f638.json"
sheet_id = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

if os.path.exists(service_account_file):
    try:
        scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
        # Refresh to get valid token
        creds.refresh(Request())
        token = creds.token
        
        # Row 94 data (length 46)
        row_data = [""] * 46
        row_data[3] = "HWZOICBIMSIPDP" # Column D
        row_data[38] = "https://res.cloudinary.com/deru9p712/image/upload/v1779908301/BDS-KhangNgo/f04947-mmdt1euj-f4bf99b3/emqazmkuwgsjft96usww.jpg"
        row_data[40] = "FALSE"
        
        write_url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/Source!A94:AT94?valueInputOption=USER_ENTERED"
        print(f"URL: {write_url}")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Test 1: Write correct length (46)
        payload = {
            "values": [row_data]
        }
        res = requests.put(write_url, headers=headers, json=payload)
        print(f"Test 1 (Length 46) response status: {res.status_code}")
        print(f"Response: {res.text}")
        
        # Test 2: Write short array (e.g. 38 elements) to see if Sheets API is ok with that
        short_data = [""] * 38
        short_data[3] = "HWZOICBIMSIPDP"
        payload_short = {
            "values": [short_data]
        }
        res_short = requests.put(write_url, headers=headers, json=payload_short)
        print(f"Test 2 (Length 38) response status: {res_short.status_code}")
        print(f"Response: {res_short.text}")

        # Test 3: What if source_row_index is undefined/null/NaN?
        bad_write_url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}/values/Source!Aundefined:ATundefined?valueInputOption=USER_ENTERED"
        res_bad = requests.put(bad_write_url, headers=headers, json=payload)
        print(f"Test 3 (Bad URL) response status: {res_bad.status_code}")
        print(f"Response: {res_bad.text}")

    except Exception as e:
        print("Error:")
        import traceback
        traceback.print_exc()
else:
    print(f"Service account file {service_account_file} not found.")

sys.stdout.close()
