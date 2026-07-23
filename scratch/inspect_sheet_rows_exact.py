import sys
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding='utf-8')

import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'
POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'

print("=== EXACT ROW INDEXES ON SHEET POOL ===")
pool_res = service.spreadsheets().values().get(spreadsheetId=POOL_SHEET_ID, range="Pool!A1:CQ").execute()
pool_rows = pool_res.get("values", [])

for idx, r in enumerate(pool_rows[1:], 2): # 1-based index
    so_nha = r[6] if len(r) > 6 else ""
    duong = r[5] if len(r) > 5 else ""
    sys_id = r[72] if len(r) > 72 else (r[71] if len(r) > 71 else "")
    id_val = r[55] if len(r) > 55 else ""
    admin_imgs = r[94] if len(r) > 94 else ""
    print(f"Pool Row {idx:2d}: {so_nha} {duong} | System_ID: {sys_id} | id: {id_val}")
    if admin_imgs:
        print(f"         Images_Admin_JSON len: {len(admin_imgs)} | snippet: {admin_imgs[:120]}...")

print("\n=== EXACT ROW INDEXES ON SHEET SOURCE ===")
source_res = service.spreadsheets().values().get(spreadsheetId=SOURCE_SHEET_ID, range="Source!A1:AW").execute()
source_rows = source_res.get("values", [])

for idx, r in enumerate(source_rows[1:], 2): # 1-based index
    cu_phap = r[1] if len(r) > 1 else ""
    sys_id = r[37] if len(r) > 37 else ""
    id_val = r[3] if len(r) > 3 else ""
    pub_imgs = r[48] if len(r) > 48 else ""
    print(f"Source Row {idx:2d}: {cu_phap[:40]} | System_ID: {sys_id} | id: {id_val}")
    if pub_imgs:
        print(f"           Images_Public_JSON len: {len(pub_imgs)} | snippet: {pub_imgs[:120]}...")
