import sys
sys.stdout.reconfigure(encoding='utf-8')

import gspread
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'd:/LHTBrain/01_PROJECTS/BDS-KhangNgo/khangngo-admin-a96043c2f638.json'
PUBLIC_SHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0'

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open_by_key(PUBLIC_SHEET_ID)
worksheet = sh.worksheet("Public")

print("Updating columns AJ, AK, AL (columns 36, 37, 38) headers on Public sheet...")

# Col AJ (36)
worksheet.update_cell(1, 36, "Hình Mặt Tiền")
worksheet.update_cell(2, 36, "hinh_mat_tien")
print("Updated Col 36 (AJ) to: R1='Hình Mặt Tiền', R2='hinh_mat_tien'")

# Col AK (37)
worksheet.update_cell(1, 37, "Tiêu đề BDS")
worksheet.update_cell(2, 37, "tieu_de_bds")
print("Updated Col 37 (AK) to: R1='Tiêu đề BDS', R2='tieu_de_bds'")

# Col AL (38)
worksheet.update_cell(1, 38, "Đăng BDS")
worksheet.update_cell(2, 38, "dang_bds")
print("Updated Col 38 (AL) to: R1='Đăng BDS', R2='dang_bds'")

print("Verification: reading Row 1 and Row 2 of Public sheet...")
vals = worksheet.get('1:2')
print("Row 1 updated:", vals[0][33:43])
print("Row 2 updated:", vals[1][33:43])
