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

# Extract TKG_accessToken
access_token = None
for part in cookie_str.split(";"):
    part = part.strip()
    if part.startswith("TKG_accessToken="):
        access_token = part.split("=", 1)[1]
        break

if not access_token:
    print("[❌] Không tìm thấy TKG_accessToken trong cookie!")
    sys.exit(1)

print(f"Access Token length: {len(access_token)}")
print(f"Token snippet: {access_token[:50]}...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://proptech.thienkhoi.com",
    "Referer": "https://proptech.thienkhoi.com/"
}

url = "https://backend.thienkhoi.com/product/v1/property?page=1&limit=20&searchBy=address"
print(f"\nRequesting Backend API: {url}")
try:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response Content-Type: {r.headers.get('Content-Type')}")
    if r.status_code == 200:
        data = r.json()
        print("[✅] Success! Response JSON parsed successfully.")
        print(f"Message: {data.get('message')}")
        # Print first listing address and ID
        listings = data.get("data", {}).get("data", [])
        print(f"Number of listings in response: {len(listings)}")
        if listings:
            first = listings[0]
            print("First listing data:")
            print(json.dumps(first, indent=2, ensure_ascii=False)[:1000])
    else:
        print(f"Response text: {r.text[:500]}")
except Exception as e:
    print(f"[❌] Error: {e}")
