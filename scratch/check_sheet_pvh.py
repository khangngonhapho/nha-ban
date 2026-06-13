import os
import json
import requests
from google.oauth2 import service_account

def get_access_token(creds_path):
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)
    import google.auth.transport.requests
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    return creds.token

def main():
    creds_path = "khangngo-admin-a96043c2f638.json"
    if not os.path.exists(creds_path):
        creds_path = "credentials.json"
    
    if not os.path.exists(creds_path):
        print("Credentials file not found!")
        return

    print(f"Using credentials from: {creds_path}")
    
    try:
        token = get_access_token(creds_path)
        headers = {"Authorization": f"Bearer {token}"}
        
        SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'
        POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
        
        # Search Source Sheet
        print("Reading Source Sheet...")
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{SOURCE_SHEET_ID}/values/Source!A1:AO"
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        rows = res.json().get('values', [])
        print(f"Source row count: {len(rows)}")
        
        source_matches = []
        for idx, row in enumerate(rows):
            row_str = " ".join([str(x) for x in row]).lower()
            if '9.36a' in row_str or '9/36a' in row_str or '9.36' in row_str:
                source_matches.append((idx + 1, row))
                
        print(f"Source matches count: {len(source_matches)}")
        
        # Save matches to file to avoid console printing encoding errors
        with open("scratch/source_sheet_matches.txt", "w", encoding="utf-8") as out:
            for idx, row in source_matches:
                out.write(f"Row {idx}:\n")
                for col_idx, val in enumerate(row):
                    out.write(f"  Col {col_idx}: {val}\n")
                    
        # Search Pool Sheet
        print("Reading Pool Sheet...")
        url_pool = f"https://sheets.googleapis.com/v4/spreadsheets/{POOL_SHEET_ID}/values/Pool!A1:BZ"
        res_pool = requests.get(url_pool, headers=headers)
        res_pool.raise_for_status()
        pool_rows = res_pool.json().get('values', [])
        print(f"Pool row count: {len(pool_rows)}")
        
        pool_matches = []
        for idx, row in enumerate(pool_rows):
            row_str = " ".join([str(x) for x in row]).lower()
            if '9.36a' in row_str or '9/36a' in row_str or '9.36' in row_str:
                pool_matches.append((idx + 1, row))
                
        print(f"Pool matches count: {len(pool_matches)}")
        with open("scratch/pool_sheet_matches.txt", "w", encoding="utf-8") as out:
            for idx, row in pool_matches:
                out.write(f"Row {idx}:\n")
                # print first 80 columns
                for col_idx, val in enumerate(row[:80]):
                    out.write(f"  Col {col_idx}: {val}\n")

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
