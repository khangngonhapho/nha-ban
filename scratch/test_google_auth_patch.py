import time
import datetime
import requests
import sys
import os

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Do chenh lech thoi gian thuc te
try:
    r = requests.get('https://www.google.com', timeout=5)
    google_date_str = r.headers.get('Date')
    if google_date_str:
        google_time = datetime.datetime.strptime(google_date_str, '%a, %d %b %Y %H:%M:%S GMT').replace(tzinfo=datetime.timezone.utc)
        local_time = datetime.datetime.now(datetime.timezone.utc)
        skew = (google_time - local_time).total_seconds()
        print(f"[*] Clock skew do duoc: {skew} giay (Google nhanh hon Local {skew} giay)")
    else:
        skew = 183.0
except Exception as e:
    print(f"[!] Khong do duoc clock skew, dung mac dinh: {e}")
    skew = 183.0

# Luu lai ham time goc
original_time = time.time

# Patch time.time
time.time = lambda: original_time() + skew
print(f"[*] Da patch time.time! Gio local moi (UTC): {datetime.datetime.now(datetime.timezone.utc)}")

# Thu ket noi Google Sheets xem co loi invalid_grant nua khong
sys.path.append(os.path.abspath(os.getcwd()))
import curator_server

try:
    creds = curator_server.get_google_credentials()
    if creds:
        # Thu lay access token
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        print("[🎉 THANH CONG] Google Auth Refresh Token thanh cong sau khi patch clock skew!")
        print(f"Token moi: {creds.token[:20]}...")
    else:
        print("[-] Khong load duoc credentials.json")
except Exception as e:
    print(f"[❌ THAT BAI] Loi ket noi Google Auth: {e}")
