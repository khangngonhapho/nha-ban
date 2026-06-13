import sys
import json
import requests
sys.stdout.reconfigure(encoding='utf-8')

from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'd:/LHTBrain/01_PROJECTS/BDS-KhangNgo/khangngo-admin-a96043c2f638.json'
SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'

scopes = [
    'https://www.googleapis.com/auth/spreadsheets'
]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
import google.auth.transport.requests
auth_req = google.auth.transport.requests.Request()
creds.refresh(auth_req)
token = creds.token

# Read row 94 values first
import gspread
gc = gspread.authorize(creds)
sh = gc.open_by_key(SOURCE_SHEET_ID)
w = sh.worksheet("Source")
row_data = w.get_all_values()[93] # Row 94 (0-indexed 93)

print("Original Row 94 length:", len(row_data))
print("Original Row 94:", row_data)

# Simulate Javascript changes in saveSourceChanges
new_row = list(row_data)
# Pad to length 46 if it is shorter
while len(new_row) < 46:
    new_row.append("")

# Make sure we simulate index modifications
new_row[2] = row_data[2] if len(row_data) > 2 else "" # Note
new_row[12] = row_data[12] if len(row_data) > 12 else "" # Huong
new_row[13] = row_data[13] if len(row_data) > 13 else "" # Duong
new_row[14] = row_data[14] if len(row_data) > 14 else "-" # RongHem
new_row[15] = row_data[15] if len(row_data) > 15 else "" # TinhTrang
new_row[16] = row_data[16] if len(row_data) > 16 else "" # DanhGia
new_row[17] = row_data[17] if len(row_data) > 17 else "" # NguTret
new_row[18] = row_data[18] if len(row_data) > 18 else "" # CHDV
new_row[19] = row_data[19] if len(row_data) > 19 else "" # MoTa
new_row[30] = "2026-06-05T10:00:00.000Z" # LastUpdated
new_row[32] = row_data[32] if len(row_data) > 32 else "-" # SoPN
new_row[33] = row_data[33] if len(row_data) > 33 else "-" # SoWC
new_row[4] = row_data[4] if len(row_data) > 4 else "" # TieuDe
new_row[39] = "" # Tiêu đề BDS

# Update images 1-10
cleanPublicImages = []
for i in range(20, 30):
    url = new_row[i] if i < len(new_row) else ""
    if url and not cleanPublicImages.count(url):
        cleanPublicImages.append(url)
for i in range(41, 46):
    url = new_row[i] if i < len(new_row) else ""
    if url and not cleanPublicImages.count(url):
        cleanPublicImages.append(url)

while len(cleanPublicImages) < 15:
    cleanPublicImages.append("")

for i in range(10):
    new_row[20 + i] = cleanPublicImages[i]
for i in range(10, 15):
    new_row[31 + i] = cleanPublicImages[i]

print("\nPayload Row length:", len(new_row))
print("Payload Row:", new_row)

# Send raw PUT request
url = f"https://sheets.googleapis.com/v4/spreadsheets/{SOURCE_SHEET_ID}/values/Source!A94:AT94?valueInputOption=USER_ENTERED"
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}
body = {
    "values": [new_row]
}

res = requests.put(url, headers=headers, json=body)
print("\nResponse status code:", res.status_code)
print("Response body:")
try:
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))
except Exception:
    print(res.text)
