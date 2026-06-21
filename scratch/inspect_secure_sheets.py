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
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)
        
        POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
        SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'
        
        print("--- SEARCHING IN SOURCE SHEET ---")
        try:
            source_sheet = client.open_by_key(SOURCE_SHEET_ID).worksheet("Source")
            source_records = source_sheet.get_all_values()
            print(f"Total rows in Source sheet: {len(source_records)}")
            
            # Find headers (row 0 or 1)
            headers = source_records[0]
            print(f"Source Headers: {headers[:15]} ...")
            
            for idx, row in enumerate(source_records):
                row_str = " ".join(row)
                if "HWMHIMBZINVN" in row_str or "Nguyễn Văn Nguyễn" in row_str:
                    print(f"Found row {idx+1} in Source sheet:")
                    for col_idx, val in enumerate(row):
                        header = headers[col_idx] if col_idx < len(headers) else f"Col{col_idx}"
                        print(f"  {header or f'Col{col_idx}'}: {val}")
        except Exception as e:
            print("Error reading Source sheet:", e)
            
        print("\n--- SEARCHING IN POOL SHEET ---")
        try:
            pool_sheet = client.open_by_key(POOL_SHEET_ID).worksheet("Pool")
            pool_records = pool_sheet.get_all_values()
            print(f"Total rows in Pool sheet: {len(pool_records)}")
            
            # Find headers
            headers = pool_records[0]
            print(f"Pool Headers: {headers[:15]} ...")
            
            for idx, row in enumerate(pool_records):
                row_str = " ".join(row)
                if "HWMHIMBZINVN" in row_str or "Nguyễn Văn Nguyễn" in row_str or "3acfcaeb-5304-4129-8c39-842a85610de9" in row_str:
                    print(f"Found row {idx+1} in Pool sheet:")
                    for col_idx, val in enumerate(row):
                        header = headers[col_idx] if col_idx < len(headers) else f"Col{col_idx}"
                        print(f"  {header or f'Col{col_idx}'}: {val}")
        except Exception as e:
            print("Error reading Pool sheet:", e)
            
    except Exception as e:
        print("Auth error:", e)
else:
    print("Credentials file does not exist")
