import os
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

def main():
    creds_file = 'khangngo-admin-a96043c2f638.json'
    if not os.path.exists(creds_file):
        creds_file = 'credentials.json'
    if not os.path.exists(creds_file):
        print("No credentials found")
        return
        
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = service_account.Credentials.from_service_account_file(creds_file, scopes=scopes)
    req = google.auth.transport.requests.Request()
    creds.refresh(req)
    token = creds.token
    
    POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
    SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'
    
    out_lines = []
    
    # Pool
    out_lines.append("--- POOL SHEET (A1:E5) ---")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{POOL_SHEET_ID}/values/Pool!A1:E5"
    res = requests.get(url, headers={'Authorization': f"Bearer {token}"})
    if res.ok:
        data = res.json()
        for idx, row in enumerate(data.get('values', [])):
            out_lines.append(f"Row {idx+1}: {row}")
    else:
        out_lines.append(f"Error Pool: {res.status_code} - {res.text}")
        
    # Source
    out_lines.append("\n--- SOURCE SHEET (A1:E5) ---")
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SOURCE_SHEET_ID}/values/Source!A1:E5"
    res = requests.get(url, headers={'Authorization': f"Bearer {token}"})
    if res.ok:
        data = res.json()
        for idx, row in enumerate(data.get('values', [])):
            out_lines.append(f"Row {idx+1}: {row}")
    else:
        out_lines.append(f"Error Source: {res.status_code} - {res.text}")
        
    # Write to file
    with open('scratch/pool_rows_output.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))
        
    print("Done inspecting. Output saved to scratch/pool_rows_output.txt")

if __name__ == '__main__':
    main()
