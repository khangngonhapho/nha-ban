import gspread
import os
import sys
from google.oauth2 import service_account

sys.stdout = open("scratch/inspect_curated_listing_output.txt", "w", encoding="utf-8")

service_account_file = "khangngo-admin-a96043c2f638.json"
sheet_id_source = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'
sheet_id_pool = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'

if os.path.exists(service_account_file):
    try:
        scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        creds = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet_source = client.open_by_key(sheet_id_source).worksheet("Source")
        sheet_pool = client.open_by_key(sheet_id_pool).worksheet("Pool")
        
        # Row 94 of Source (1-indexed)
        sr = sheet_source.row_values(94)
        # Row 5724 of Pool (1-indexed)
        pr = sheet_pool.row_values(5724)
        
        # Pad sr to 46
        while len(sr) < 46:
            sr.append("")
        # Pad pr to 93
        while len(pr) < 93:
            pr.append("")
            
        print(f"Source Row 94 values (length {len(sr)}):")
        for i, val in enumerate(sr):
            print(f"  Index {i}: {repr(val)}")
            
        print(f"\nPool Row 5724 values (length {len(pr)}):")
        for i, val in enumerate(pr):
            if val:
                print(f"  Index {i}: {repr(val)}")
                
    except Exception as e:
        print("Error:")
        import traceback
        traceback.print_exc()
else:
    print(f"Service account file {service_account_file} not found.")

sys.stdout.close()
