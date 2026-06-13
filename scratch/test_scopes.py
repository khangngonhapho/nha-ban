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

# Patch time
original_time = time.time
time.time = lambda: original_time() + skew

from google.oauth2 import service_account
from google.auth.transport.requests import Request

cred_path = 'd:/LHTBrain/01_PROJECTS/BDS-KhangNgo/credentials.json'
print(f"[*] Test voi file: {cred_path}")

try:
    # Scope lay tu get_google_credentials cua curator_server.py
    scopes = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)
    creds.refresh(Request())
    print("[🎉 THANH CONG] Refresh Token thanh cong voi exact scopes!")
    print(f"Token: {creds.token[:20]}...")
except Exception as e:
    print(f"[❌ THAT BAI] Loi: {e}")
