import os
import sys
import requests
from bs4 import BeautifulSoup
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Read cookie
cookie_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/thienkhoi_cookie.txt"
with open(cookie_path, 'r', encoding='utf-8') as f:
    cookie = f.read().strip()

# Read Page 1 titles for comparison
p1_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Danh Sach.html"
with open(p1_path, 'r', encoding='utf-8') as f:
    p1_html = f.read()
p1_soup = BeautifulSoup(p1_html, 'html.parser')
p1_titles = [t.text.strip() for t in p1_soup.find_all('p', {'data-testid': 'title-property'})]
print(f"Page 1 titles (total {len(p1_titles)}):")
for idx, title in enumerate(p1_titles[:3]):
    print(f"  - {title}")

# Candidates query strings to test
candidates = [
    ("page=2", "https://proptech.thienkhoi.com/warehouse?page=2"),
    ("Page=2", "https://proptech.thienkhoi.com/warehouse?Page=2"),
    ("pageIndex=2", "https://proptech.thienkhoi.com/warehouse?pageIndex=2"),
    ("p=2", "https://proptech.thienkhoi.com/warehouse?p=2"),
    ("offset=20", "https://proptech.thienkhoi.com/warehouse?offset=20"),
    ("page=2&pageSize=20", "https://proptech.thienkhoi.com/warehouse?page=2&pageSize=20"),
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": cookie
}

print("\n=== Testing HTML Pagination ===")
for name, url in candidates:
    print(f"Requesting: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            titles = [t.text.strip() for t in soup.find_all('p', {'data-testid': 'title-property'})]
            print(f"  Found {len(titles)} titles on Page 2.")
            
            # Compare with Page 1
            if titles:
                # Check if any title overlaps with Page 1
                overlaps = set(p1_titles).intersection(set(titles))
                overlap_ratio = len(overlaps) / len(titles) if titles else 0
                print(f"  Overlap with Page 1: {len(overlaps)} titles (Ratio: {overlap_ratio:.1%})")
                if len(overlaps) == 0:
                    print(f"  [🎉 SUCCESS!] '{name}' is the correct pagination query! The pages do not overlap.")
                    print("  Sample Page 2 titles:")
                    for t in titles[:3]:
                        print(f"    - {t}")
                else:
                    print(f"  [x] Overlap detected. Same as Page 1 or same list.")
            else:
                print("  [x] No listings found on this page.")
        else:
            print(f"  Status code: {r.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
