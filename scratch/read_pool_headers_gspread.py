import sys
sys.stdout.reconfigure(encoding='utf-8')

import gspread
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'd:/LHTBrain/01_PROJECTS/BDS-KhangNgo/khangngo-admin-a96043c2f638.json'
POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open_by_key(POOL_SHEET_ID)
worksheet = sh.worksheet("Pool")

vals = worksheet.get('1:2')
row1 = vals[0] if len(vals) > 0 else []
row2 = vals[1] if len(vals) > 1 else []

print(f"Total headers in Pool: {max(len(row1), len(row2))}")
for idx in range(max(len(row1), len(row2))):
    col_str = ""
    temp = idx
    while temp >= 0:
        col_str = chr(65 + (temp % 26)) + col_str
        temp = (temp // 26) - 1
    val1 = row1[idx] if idx < len(row1) else ""
    val2 = row2[idx] if idx < len(row2) else ""
    print(f"Index {idx} (Col {col_str}): R1='{val1}' | R2='{val2}'")
