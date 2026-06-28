import os
import sys
import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

def get_google_credentials():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    cred_file = 'khangngo-admin-a96043c2f638.json'
    if not os.path.exists(cred_file):
        cred_file = 'credentials.json'
    return service_account.Credentials.from_service_account_file(cred_file, scopes=scopes)

creds = get_google_credentials()
req = google.auth.transport.requests.Request()
creds.refresh(req)
token = creds.token

POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
url = f"https://sheets.googleapis.com/v4/spreadsheets/{POOL_SHEET_ID}/values/Pool!A1:G5"
headers = {'Authorization': f'Bearer {token}'}
res = requests.get(url, headers=headers)
pool_data = res.json()

SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'
url_source = f"https://sheets.googleapis.com/v4/spreadsheets/{SOURCE_SHEET_ID}/values/Source!A1:G5"
res_source = requests.get(url_source, headers=headers)
source_data = res_source.json()

output = {
    "pool": pool_data,
    "source": source_data
}

with open("scratch/inspect_sheets_output.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("Saved output to scratch/inspect_sheets_output.json successfully!")
