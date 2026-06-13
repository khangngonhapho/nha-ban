import gspread
import os
import sys
from google.oauth2 import service_account

sys.stdout = open("scratch/simulate_load_output.txt", "w", encoding="utf-8")

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
        
        # Load sheets
        spreadsheet_source = client.open_by_key(sheet_id_source)
        sheet_source = spreadsheet_source.worksheet("Source")
        source_rows = sheet_source.get_all_values()
        
        spreadsheet_pool = client.open_by_key(sheet_id_pool)
        sheet_pool = spreadsheet_pool.worksheet("Pool")
        pool_rows = sheet_pool.get_all_values()
        
        # In index.html, it queries Source!A2:AT. So the first row (headers) is removed.
        # So source_rows[1:] corresponds to sourceRows.
        # Same for poolRows (Pool!A2:CO).
        sourceRows = source_rows[1:]
        poolRows = pool_rows[1:]
        
        target_id = "HWZOICBIMSIPDP"
        
        # Replicate index.html map/filter logic
        found_p = None
        for index, sr in enumerate(sourceRows):
            # Pad sr to 46 columns
            while len(sr) < 46:
                sr.append("")
                
            if not sr[3] and not sr[4]:
                continue
                
            targetRowNumber = index + 2
            srId = sr[3]
            srSystemId = sr[37]
            
            if srId == target_id or srSystemId == target_id:
                # Find matching pool row
                poolRow = None
                for pr in poolRows:
                    while len(pr) < 93:
                        pr.append("")
                    prSystemId = pr[72] if pr[72] else pr[71] if pr[71] else ''
                    prId = pr[55] if pr[55] else pr[54] if pr[54] else ''
                    
                    if (srSystemId and prSystemId == srSystemId) or (srId and prId == srId) or (srSystemId and prId == srSystemId):
                        poolRow = pr
                        break
                        
                p = {
                    'id': sr[3] or '',
                    'system_id': sr[37] or str(index + 1),
                    'source_row_index': targetRowNumber,
                    'is_invisible': 'ẩn' in (sr[15] or '').lower() or 'đã bán' in (sr[15] or '').lower() or 'invisible' in (sr[15] or '').lower()
                }
                if poolRow:
                    p['pool_row_index'] = poolRows.index(poolRow) + 2
                else:
                    p['pool_row_index'] = None
                
                print(f"Listing HWZOICBIMSIPDP mapped object:")
                print(p)
                found_p = p
                
        if not found_p:
            print("Listing HWZOICBIMSIPDP was not found or mapped!")
            
    except Exception as e:
        print("Error:")
        import traceback
        traceback.print_exc()
else:
    print(f"Service account file {service_account_file} not found.")

sys.stdout.close()
