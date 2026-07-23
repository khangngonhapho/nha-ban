import os
import sys
import sqlite3
import json
import re

sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding='utf-8')

from google.oauth2 import service_account
from googleapiclient.discovery import build

DB_PATH = r"D:\02. CONG VIEC\khangngonhapho.com\raw_archive.db"
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'
POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'

def norm_addr(so_nha, duong):
    s = f"{so_nha or ''} {duong or ''}".lower()
    s = re.sub(r'\s+', '', s)
    return s.strip()

print(f"=== STEP 1: READING CLEAN DATA FROM PRODUCTION SQLITE ({DB_PATH}) ===")
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT tk_id, System_ID, Ngo_So_nha, Duong, Images_Admin_JSON, images_public_json
    FROM listings
    WHERE tk_id IS NOT NULL AND tk_id != ''
""")
db_rows = cursor.fetchall()
print(f"Found {len(db_rows)} listings in Production SQLite.")

sqlite_by_sys = {}
sqlite_by_addr = {}
for r in db_rows:
    sys_id = str(r["System_ID"] or "").strip()
    so_nha = str(r["Ngo_So_nha"] or "").strip()
    duong = str(r["Duong"] or "").strip()
    addr_key = norm_addr(so_nha, duong)
    
    item = {
        "tk_id": r["tk_id"],
        "sys_id": sys_id,
        "so_nha": so_nha,
        "duong": duong,
        "address": f"{so_nha} {duong}",
        "admin_json": r["Images_Admin_JSON"],
        "public_json": r["images_public_json"]
    }
    if sys_id:
        sqlite_by_sys[sys_id] = item
    if addr_key:
        sqlite_by_addr[addr_key] = item
    print(f"  - {sys_id or 'NO_SYS'}: {so_nha} {duong} (tk_id: {r['tk_id']}) | AddrKey: '{addr_key}'")

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
    sys_id = str(r[72] if len(r) > 72 else (r[71] if len(r) > 71 else "")).strip()
    so_nha = str(r[6] if len(r) > 6 else "").strip()
    duong = str(r[5] if len(r) > 5 else "").strip()
    addr_key = norm_addr(so_nha, duong)
    
    matched_item = sqlite_by_sys.get(sys_id) or sqlite_by_addr.get(addr_key)
    
    if matched_item:
        clean_admin = matched_item["admin_json"]
        address = matched_item["address"]
        matched_sys = matched_item["sys_id"]
        print(f"Restoring Sheet Pool Row {idx} ({address} | Sheet SysID: {sys_id} -> DB SysID: {matched_sys})...")
        
        # 1. Cập nhật Images_Admin_JSON (cột CQ / 95)
        service.spreadsheets().values().update(
            spreadsheetId=POOL_SHEET_ID,
            range=f"Pool!CQ{idx}:CQ{idx}",
            valueInputOption="USER_ENTERED",
            body={"values": [[clean_admin]]}
        ).execute()
        
        # 2. Cập nhật System ID (cột BU / 73) nếu lệch
        if matched_sys and sys_id != matched_sys:
            print(f"   [Cập nhật System ID] Đổi System ID trên Pool Row {idx} từ '{sys_id}' thành '{matched_sys}'")
            service.spreadsheets().values().update(
                spreadsheetId=POOL_SHEET_ID,
                range=f"Pool!BU{idx}:BU{idx}",
                valueInputOption="USER_ENTERED",
                body={"values": [[matched_sys]]}
            ).execute()

# 2. Update Sheet Source
print("\n--- Updating Sheet Source ---")
source_res = service.spreadsheets().values().get(spreadsheetId=SOURCE_SHEET_ID, range="Source!A1:AW").execute()
source_rows = source_res.get("values", [])

for idx, r in enumerate(source_rows[1:], 2): # 1-based index
    sys_id = str(r[37] if len(r) > 37 else "").strip()
    cu_phap = str(r[1] if len(r) > 1 else "").strip()
    
    matched_item = sqlite_by_sys.get(sys_id)
    if not matched_item:
        # Thử tìm theo cú pháp địa chỉ
        for a_key, item in sqlite_by_addr.items():
            if item["so_nha"].lower() in cu_phap.lower() and item["duong"].lower() in cu_phap.lower():
                matched_item = item
                break
                
    if matched_item:
        clean_pub = matched_item["public_json"]
        address = matched_item["address"]
        print(f"Restoring Sheet Source Row {idx} ({address} | System_ID: {sys_id})...")
        service.spreadsheets().values().update(
            spreadsheetId=SOURCE_SHEET_ID,
            range=f"Source!AW{idx}:AW{idx}",
            valueInputOption="USER_ENTERED",
            body={"values": [[clean_pub]]}
        ).execute()

print("\n=== STEP 3: REBUILDING CLOUDFLARE R2 CDN SHARDS ===")
from manager import generate_and_upload_public_shards
rebuild_res = generate_and_upload_public_shards(db_file=DB_PATH)
print("R2 CDN Rebuild Result:", rebuild_res)

print("\n✅ RESTORATION COMPLETED SUCCESSFULLY FOR ALL 6 LISTINGS!")
