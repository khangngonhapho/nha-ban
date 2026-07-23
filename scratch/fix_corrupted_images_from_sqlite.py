import os
import sys
import sqlite3
import json

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding='utf-8')

from google.oauth2 import service_account
from googleapiclient.discovery import build

DB_PATH = r"D:\02. CONG VIEC\khangngonhapho.com\raw_archive.db"
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'
POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'

print(f"=== STEP 1: READING CLEAN DATA FROM PRODUCTION SQLITE ({DB_PATH}) ===")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT tk_id, System_ID, Ngo_So_nha, Duong, Images_Admin_JSON, images_public_json
    FROM listings
    WHERE System_ID IS NOT NULL AND System_ID != ''
""")
db_rows = cursor.fetchall()
print(f"Found {len(db_rows)} listings in Production SQLite.")

sqlite_data = {}
for r in db_rows:
    sys_id = r["System_ID"]
    sqlite_data[sys_id] = {
        "tk_id": r["tk_id"],
        "address": f"{r['Ngo_So_nha']} {r['Duong']}",
        "admin_json": r["Images_Admin_JSON"],
        "public_json": r["images_public_json"]
    }
    print(f"  - {sys_id}: {r['Ngo_So_nha']} {r['Duong']} (tk_id: {r['tk_id']})")
    print(f"    Admin JSON len: {len(r['Images_Admin_JSON'] or '')}")
    print(f"    Public JSON len: {len(r['images_public_json'] or '')}")

conn.close()

print("\n=== STEP 2: CONNECTING TO GOOGLE SHEETS ===")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# 1. Update Sheet Pool
print("\n--- Updating Sheet Pool ---")
pool_res = service.spreadsheets().values().get(spreadsheetId=POOL_SHEET_ID, range="Pool!A1:CQ").execute()
pool_rows = pool_res.get("values", [])

for idx, r in enumerate(pool_rows[1:], 2): # 1-based index
    sys_id = r[72] if len(r) > 72 else (r[71] if len(r) > 71 else "")
    sys_id = str(sys_id).strip()
    if sys_id in sqlite_data:
        clean_admin = sqlite_data[sys_id]["admin_json"]
        address = sqlite_data[sys_id]["address"]
        print(f"Restoring Sheet Pool Row {idx} ({address} | System_ID: {sys_id})...")
        update_range = f"Pool!CQ{idx}:CQ{idx}"
        service.spreadsheets().values().update(
            spreadsheetId=POOL_SHEET_ID,
            range=update_range,
            valueInputOption="USER_ENTERED",
            body={"values": [[clean_admin]]}
        ).execute()

# 2. Update Sheet Source
print("\n--- Updating Sheet Source ---")
source_res = service.spreadsheets().values().get(spreadsheetId=SOURCE_SHEET_ID, range="Source!A1:AW").execute()
source_rows = source_res.get("values", [])

for idx, r in enumerate(source_rows[1:], 2): # 1-based index
    sys_id = r[37] if len(r) > 37 else ""
    sys_id = str(sys_id).strip()
    if sys_id in sqlite_data:
        clean_pub = sqlite_data[sys_id]["public_json"]
        address = sqlite_data[sys_id]["address"]
        print(f"Restoring Sheet Source Row {idx} ({address} | System_ID: {sys_id})...")
        update_range = f"Source!AW{idx}:AW{idx}"
        service.spreadsheets().values().update(
            spreadsheetId=SOURCE_SHEET_ID,
            range=update_range,
            valueInputOption="USER_ENTERED",
            body={"values": [[clean_pub]]}
        ).execute()

print("\n=== STEP 3: REBUILDING CLOUDFLARE R2 CDN SHARDS ===")
from manager import generate_and_upload_public_shards
rebuild_res = generate_and_upload_public_shards(db_file=DB_PATH)
print("R2 CDN Rebuild Result:", rebuild_res)

print("\n✅ RESTORATION COMPLETED SUCCESSFULLY!")
