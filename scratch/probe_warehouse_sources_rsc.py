import os
import sys
import requests
import json
import urllib.parse

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

cookie_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/thienkhoi_cookie.txt"

if not os.path.exists(cookie_path):
    print("[❌] Không tìm thấy file cookie!")
    sys.exit(1)

with open(cookie_path, 'r', encoding='utf-8') as f:
    cookie = f.read().strip()

print(f"Cookie length: {len(cookie)}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": cookie,
    "RSC": "1",
    "Accept": "text/x-component",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://proptech.thienkhoi.com/warehouse"
}

# We will probe the following URLs
candidates = [
    "https://proptech.thienkhoi.com/warehouse/sources",
    "https://proptech.thienkhoi.com/warehouse/sources?page=1",
    "https://proptech.thienkhoi.com/warehouse/sources?page=2",
    "https://proptech.thienkhoi.com/warehouse/sources?pageIndex=2",
    "https://proptech.thienkhoi.com/warehouse/sources?offset=20",
    "https://proptech.thienkhoi.com/warehouse/sources?page=2&pageSize=20",
    "https://proptech.thienkhoi.com/warehouse/sources?limit=20&page=2"
]

print("\n=== Probing Warehouse Sources with RSC: 1 ===")
for url in candidates:
    print(f"\nProbing: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"  Status: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('Content-Type')}")
        print(f"  Length: {len(r.text)}")
        snippet = r.text[:300].strip()
        print(f"  Snippet: {snippet}...")
        
        # Check if response text has real estate listings keywords
        found = []
        for kw in ["trần", "phạm", "đường", "tỷ", "triệu", "trần văn đang", "phạm văn hai"]:
            if kw in r.text.lower():
                found.append(kw)
        if found:
            print(f"  [🎉 SUCCESS - FOUND REAL ESTATE DATA!] Matches: {found}")
            parsed_url = urllib.parse.urlparse(url)
            safe_name = parsed_url.path.replace("/", "_") + "_" + parsed_url.query.replace("&", "_").replace("=", "_")
            out_path = f"scratch/probe_rsc_{safe_name}.txt"
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(r.text)
            print(f"    Saved response to {out_path}")
            
    except Exception as e:
        print(f"  [❌] Error: {e}")
