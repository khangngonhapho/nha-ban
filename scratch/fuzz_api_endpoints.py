import os
import sys
import requests
import time

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

cookie_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/thienkhoi_cookie.txt"
with open(cookie_path, 'r', encoding='utf-8') as f:
    cookie = f.read().strip()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": cookie,
    "Accept": "application/json, text/plain, */*"
}

# Generate a list of common API patterns
prefixes = ["/api", "/api/v1", "/api/v2", "/api/member", "/api/public", "/warehouse/api", "/sources/api"]
entities = ["sources", "warehouse", "properties", "listings", "houses", "products", "items", "posts", "source", "property", "listing"]
suffixes = ["", "/list", "/search", "/filter", "/all"]

urls = []
for prefix in prefixes:
    for entity in entities:
        for suffix in suffixes:
            urls.append(f"https://proptech.thienkhoi.com{prefix}/{entity}{suffix}")
            
# Also add some direct paths with query strings
direct_tests = [
    "https://proptech.thienkhoi.com/api/warehouse/sources",
    "https://proptech.thienkhoi.com/api/warehouse/sources?page=2",
    "https://proptech.thienkhoi.com/api/warehouse/sources/list",
    "https://proptech.thienkhoi.com/api/warehouse/sources/search",
]
urls.extend(direct_tests)
urls = list(set(urls))

print(f"Generated {len(urls)} target URLs to probe. Bắt đầu quét...")

found_endpoints = []
count = 0
for url in urls:
    count += 1
    if count % 20 == 0:
        print(f"Scanned {count}/{len(urls)}...")
    try:
        r = requests.get(url, headers=headers, timeout=5)
        # If status is NOT 404, we found something!
        # Status 200, 401 (Auth needed), 403 (Forbidden), 405 (Method Not Allowed), 500 (Internal Server Error)
        # all mean the route exists on the server!
        if r.status_code != 404:
            # Check if it just redirected to a 404 page or login page
            if "login" in r.url.lower() or "404" in r.url.lower():
                continue
            print(f"[⭐ FOUND!] Route exists: {url} (Status: {r.status_code})")
            found_endpoints.append((url, r.status_code))
            
            # Print response snippet
            print(f"  Snippet: {r.text[:200]}")
    except Exception as e:
        pass
    # Sleep briefly to be nice to the server
    time.sleep(0.1)
    
print("\n=== Scan Complete ===")
print(f"Found {len(found_endpoints)} potential API endpoints:")
for url, status in found_endpoints:
    print(f"  {url} -> Status: {status}")
