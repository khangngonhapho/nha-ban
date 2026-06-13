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

access_token = None
for part in cookie_str.split(";"):
    part = part.strip()
    if part.startswith("TKG_accessToken="):
        access_token = part.split("=", 1)[1]
        break

if not access_token:
    print("[❌] Không tìm thấy access token!")
    sys.exit(1)

headers_backend = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    "Origin": "https://proptech.thienkhoi.com",
    "Referer": "https://proptech.thienkhoi.com/"
}

headers_rsc = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": cookie_str,
    "RSC": "1",
    "Accept": "text/x-component",
    "Referer": "https://proptech.thienkhoi.com/warehouse/sources"
}

uuid = "19c74ebc-e5a4-4cfb-844b-3ae5365e6318"

candidates = [
    ("Backend Direct ID", f"https://backend.thienkhoi.com/product/v1/property/{uuid}"),
    ("Backend Detail Subpath", f"https://backend.thienkhoi.com/product/v1/property/detail/{uuid}"),
    ("Backend Sources Subpath", f"https://backend.thienkhoi.com/product/v1/property/sources/{uuid}"),
    ("Next.js RSC Detail Page", f"https://proptech.thienkhoi.com/warehouse/sources/{uuid}")
]

print("=== Probing Property Detail Endpoints ===")
for name, url in candidates:
    print(f"\nProbing {name}: {url}")
    try:
        headers = headers_rsc if "proptech" in url else headers_backend
        r = requests.get(url, headers=headers, timeout=10)
        print(f"  Status: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('Content-Type')}")
        print(f"  Length: {len(r.text)}")
        snippet = r.text[:300].strip()
        print(f"  Snippet: {snippet}...")
        
        # Check if snippet or text has the address "Núi Thành"
        if "núi thành" in r.text.lower() or "nui thanh" in r.text.lower() or "mô tả" in r.text.lower():
            print("  [🎉 SUCCESS] Found property detail data!")
            # Save response to a file
            out_file = f"scratch/detail_{name.replace(' ', '_').replace('.', '_')}.txt"
            with open(out_file, "w", encoding="utf-8") as out:
                out.write(r.text)
            print(f"    Saved response to {out_file}")
    except Exception as e:
        print(f"  [❌] Error: {e}")
