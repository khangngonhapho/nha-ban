import time
import datetime
import requests
import sys
import os

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Clock skew
try:
    r = requests.get('https://www.google.com', timeout=5)
    google_date_str = r.headers.get('Date')
    if google_date_str:
        google_time = datetime.datetime.strptime(google_date_str, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=datetime.timezone.utc)
        local_time = datetime.datetime.now(datetime.timezone.utc)
        skew = (google_time - local_time).total_seconds()
    else:
        skew = 183.0
except Exception as e:
    skew = 183.0

original_time = time.time
time.time = lambda: original_time() + skew

from google.oauth2 import service_account
from google.auth.transport.requests import Request

new_cred_path = 'd:/LHTBrain/01_PROJECTS/BDS-KhangNgo/khangngo-admin-a96043c2f638.json'
print(f"[*] Thử kết nối Google Auth bằng file mới: {new_cred_path}")

try:
    scopes = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    creds = service_account.Credentials.from_service_account_file(new_cred_path, scopes=scopes)
    creds.refresh(Request())
    print("[🎉 THÀNH CÔNG] Đã xác thực thành công Google Sheets bằng file key mới!")
    print(f"Token mới: {creds.token[:20]}...")
except Exception as e:
    print(f"[❌ THẤT BẠI] Lỗi: {e}")
