import os
import sys
import requests
import json

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

cookie_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/thienkhoi_cookie.txt"

with open(cookie_path, 'r', encoding='utf-8') as f:
    cookie_str = f.read().strip()

# Extract TKG_accessToken and TKG_refreshToken
access_token = None
refresh_token = None
for part in cookie_str.split(";"):
    part = part.strip()
    if part.startswith("TKG_accessToken="):
        access_token = part.split("=", 1)[1]
    elif part.startswith("TKG_refreshToken="):
        refresh_token = part.split("=", 1)[1]

if not refresh_token:
    print("[❌] Không tìm thấy TKG_refreshToken!")
    sys.exit(1)

print(f"Refresh Token snippet: {refresh_token[:50]}...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://proptech.thienkhoi.com",
    "Referer": "https://proptech.thienkhoi.com/",
    "Authorization": f"Bearer {access_token}" if access_token else ""
}

payload = {
    "refresh_token": refresh_token,
    "appLogin": "nguonhang",
    "platform": "web"
}

url = "https://backend.thienkhoi.com/auth/v1/auth/refresh-token"
print(f"Posting directly to Refresh Token API: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    r = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"Status code: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"[❌] Error calling refresh API: {e}")
