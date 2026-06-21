# -*- coding: utf-8 -*-
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

creds_file = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/khangngo-admin-a96043c2f638.json"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if os.path.exists(creds_file):
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    
    POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
    pool_sheet = client.open_by_key(POOL_SHEET_ID).worksheet("Pool")
    pool_records = pool_sheet.get_all_values()
    
    headers = pool_records[0]
    for idx, row in enumerate(pool_records):
        if "HWMHIMBZINVN" in " ".join(row) or "3acfcaeb-5304-4129-8c39-842a85610de9" in " ".join(row):
            print(f"Row {idx+1} indices:")
            for i, val in enumerate(row):
                if val:
                    header = headers[i] if i < len(headers) else f"Col{i}"
                    print(f"  [{i}] {header}: {val}")
else:
    print("Credentials file does not exist")
