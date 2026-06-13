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
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://proptech.thienkhoi.com/warehouse"
}

# 1. First test: request warehouse html to see if cookie is valid
print("\n=== Probing: Warehouse HTML Page ===")
try:
    r = requests.get("https://proptech.thienkhoi.com/warehouse", headers={"User-Agent": headers["User-Agent"], "Cookie": cookie}, timeout=15)
    print(f"Status: {r.status_code}")
    print(f"Final URL: {r.url}")
    if "login" in r.url.lower() or "security" in r.url.lower():
        print("[⚠️ WARNING] Cookie seems to be expired or invalid (redirected to login/security).")
    else:
        print("[✅] Access successful! Page Title matches.")
except Exception as e:
    print(f"[❌] Error: {e}")

# 2. List of candidate API endpoints to probe
candidates = [
    # General API endpoints
    "https://proptech.thienkhoi.com/api/warehouse/sources",
    "https://proptech.thienkhoi.com/api/warehouse/properties",
    "https://proptech.thienkhoi.com/api/sources",
    "https://proptech.thienkhoi.com/api/properties",
    
    # Endpoints with typical paging queries
    "https://proptech.thienkhoi.com/api/warehouse/sources?page=2&limit=20",
    "https://proptech.thienkhoi.com/api/warehouse/sources?pageIndex=2&pageSize=20",
    "https://proptech.thienkhoi.com/api/sources?page=2",
    
    # Next.js RSC path candidates
    "https://proptech.thienkhoi.com/warehouse?_rsc=1",
    "https://proptech.thienkhoi.com/warehouse/sources?_rsc=1"
]

print("\n=== Probing candidate endpoints ===")
for url in candidates:
    print(f"\nProbing: {url}")
    try:
        # Try both Accept: application/json and default headers
        r = requests.get(url, headers=headers, timeout=10)
        print(f"  Status: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('Content-Type')}")
        content_snippet = r.text[:300].strip()
        print(f"  Snippet: {content_snippet}...")
        
        # If it is JSON or RSC, write to a temp file
        if r.status_code == 200 and len(r.text) > 100:
            parsed_url = urllib.parse.urlparse(url)
            safe_name = parsed_url.path.replace("/", "_") + "_" + parsed_url.query.replace("&", "_").replace("=", "_")
            out_path = f"scratch/probe_{safe_name}.txt"
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(r.text)
            print(f"  [✅] Saved response to {out_path}")
    except Exception as e:
        print(f"  [❌] Error: {e}")
