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
POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

INPUT_FILE = os.path.join("scratch", "restored_curated_images.json")

def norm_addr(so_nha, duong):
    s = f"{so_nha or ''} {duong or ''}".lower()
    s = re.sub(r'\s+', '', s)
    return s.strip()

def build_public_json_from_admin(admin_json_str):
    """
    Sử dụng chuẩn 100% logic từ core/business_rules.py (L620-L630) & manager.py (L1080-L1091):
    - Loại bỏ ảnh bị ẩn (is_hidden != 0)
    - Loại bỏ các ảnh vai trò private/only_facade: ["facade", "diagram", "deleted", "hidden"]
    - Đưa các ảnh có role "cover" (Bìa) lên vị trí đầu tiên
    """
    try:
        items = json.loads(admin_json_str) if isinstance(admin_json_str, str) else admin_json_str
        if not isinstance(items, list):
            return "[]"
            
        cover_urls = []
        other_urls = []
        for img in items:
            if not isinstance(img, dict):
                continue
            is_hidden = img.get("is_hidden", 0)
            role = str(img.get("role", "")).lower().strip()
            
            # Khớp 100% chuẩn core/business_rules.py & manager.py
            if is_hidden == 0 and role not in ["facade", "diagram", "deleted", "hidden", "sodo", "mặt tiền", "ẩn"]:
                url = (img.get("r2_url") or img.get("image_url") or "").strip()
                if not url:
                    continue
                if role == "cover" or role == "bìa":
                    if url not in cover_urls:
                        cover_urls.append(url)
                else:
                    if url not in other_urls:
                        other_urls.append(url)
                        
        public_urls = cover_urls + [u for u in other_urls if u not in cover_urls]
        return json.dumps(public_urls, ensure_ascii=False)
    except Exception as e:
        print("Error building public JSON:", e)
        return "[]"

print("=== RESTORE CUSTOM CURATED IMAGES SCRIPT ===")

if not os.path.exists(INPUT_FILE):
    print(f"❌ File '{INPUT_FILE}' not found! Creating template...")
    template = {
        "489.24.39B Huỳnh Văn Bánh": ""
    }
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    print(f"Created '{INPUT_FILE}'. Please put your Images_Admin_JSON string for each listing into this file.")
    sys.exit(0)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    restored_map = json.load(f)

print(f"Loaded {len(restored_map)} listing image configurations from {INPUT_FILE}.")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# Read Pool & Source
pool_res = service.spreadsheets().values().get(spreadsheetId=POOL_SHEET_ID, range="Pool!A1:CQ").execute()
pool_rows = pool_res.get("values", [])

source_res = service.spreadsheets().values().get(spreadsheetId=SOURCE_SHEET_ID, range="Source!A1:AW").execute()
source_rows = source_res.get("values", [])

for addr_query, admin_json_str in restored_map.items():
    if not admin_json_str:
        print(f"⚠️ Empty JSON for '{addr_query}', skipping...")
        continue
        
    if isinstance(admin_json_str, (list, dict)):
        admin_json_str = json.dumps(admin_json_str, ensure_ascii=False)

    pub_json_str = build_public_json_from_admin(admin_json_str)
    
    print(f"\n🔄 Processing: '{addr_query}'")
    print(f"   Admin JSON len: {len(admin_json_str)}")
    print(f"   Derived Public JSON len: {len(pub_json_str)}")

    # 1. Update SQLite
    cursor.execute("""
        UPDATE listings
        SET Images_Admin_JSON = ?, images_public_json = ?
        WHERE (Ngo_So_nha || ' ' || Duong) LIKE ? OR System_ID = ? OR tk_id = ?
    """, (admin_json_str, pub_json_str, f"%{addr_query}%", addr_query, addr_query))
    affected_db = cursor.rowcount
    print(f"   [SQLite] Updated {affected_db} row(s) in DB.")

    # 2. Update Sheet Pool
    for idx, r in enumerate(pool_rows[1:], 2):
        so_nha = str(r[6] if len(r) > 6 else "").strip()
        duong = str(r[5] if len(r) > 5 else "").strip()
        full_addr = f"{so_nha} {duong}".strip()
        sys_id = str(r[72] if len(r) > 72 else "").strip()
        
        if norm_addr(so_nha, duong) == norm_addr(addr_query, "") or addr_query.lower() in full_addr.lower() or sys_id == addr_query:
            print(f"   [Sheet Pool Row {idx}] Restoring Images_Admin_JSON for {full_addr}...")
            service.spreadsheets().values().update(
                spreadsheetId=POOL_SHEET_ID,
                range=f"Pool!CQ{idx}:CQ{idx}",
                valueInputOption="USER_ENTERED",
                body={"values": [[admin_json_str]]}
            ).execute()

    # 3. Update Sheet Source
    for idx, r in enumerate(source_rows[1:], 2):
        cu_phap = str(r[1] if len(r) > 1 else "").strip()
        sys_id = str(r[37] if len(r) > 37 else "").strip()
        
        if addr_query.lower() in cu_phap.lower() or sys_id == addr_query:
            print(f"   [Sheet Source Row {idx}] Restoring Images_Public_JSON for {cu_phap[:30]}...")
            service.spreadsheets().values().update(
                spreadsheetId=SOURCE_SHEET_ID,
                range=f"Source!AW{idx}:AW{idx}",
                valueInputOption="USER_ENTERED",
                body={"values": [[pub_json_str]]}
            ).execute()

conn.commit()
conn.close()

print("\n=== STEP 4: REBUILDING CLOUDFLARE R2 CDN SHARDS ===")
from manager import generate_and_upload_public_shards
rebuild_res = generate_and_upload_public_shards(db_file=DB_PATH)
print("R2 CDN Rebuild Result:", rebuild_res)

print("\n🎉 RESTORATION OF CUSTOM CURATED IMAGES COMPLETED SUCCESSFULLY!")
