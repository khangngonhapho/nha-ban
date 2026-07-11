import os
import sys
import requests
from bs4 import BeautifulSoup
import re
import json

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Read cookie
cookie_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/thienkhoi_cookie.txt"
with open(cookie_path, 'r', encoding='utf-8') as f:
    cookie = f.read().strip()

headers_html = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": cookie
}

headers_rsc = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": cookie,
    "RSC": "1",
    "Accept": "text/x-component",
    "Referer": "https://proptech.thienkhoi.com/warehouse/sources"
}

# Test different query string styles on /warehouse/sources
candidates = [
    ("page=2", "https://proptech.thienkhoi.com/warehouse/sources?page=2"),
    ("pageIndex=2", "https://proptech.thienkhoi.com/warehouse/sources?pageIndex=2"),
    ("p=2", "https://proptech.thienkhoi.com/warehouse/sources?p=2"),
    ("offset=20", "https://proptech.thienkhoi.com/warehouse/sources?offset=20"),
    ("limit=20&offset=20", "https://proptech.thienkhoi.com/warehouse/sources?limit=20&offset=20"),
]

print("=== Testing HTML Pagination on /warehouse/sources ===")
for name, url in candidates:
    print(f"Requesting HTML: {url}")
    try:
        r = requests.get(url, headers=headers_html, timeout=10)
        print(f"  Status: {r.status_code}, Length: {len(r.text)}")
        # Check for listing identifiers
        # In Thien Khoi pages, let's see if we find some listing address keywords
        found = [kw for kw in ["đường", "tỷ", "quận", "phường"] if kw in r.text.lower()]
        print(f"  Keywords match: {found}")
    except Exception as e:
        print(f"  Error: {e}")

print("\n=== Testing RSC Pagination on /warehouse/sources ===")
for name, url in candidates:
    print(f"Requesting RSC: {url}")
    try:
        r = requests.get(url, headers=headers_rsc, timeout=10)
        print(f"  Status: {r.status_code}, Length: {len(r.text)}")
        # Decode Unicode escapes to read easily
        text_decoded = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), r.text)
        found = [kw for kw in ["đường", "tỷ", "quận", "phường"] if kw in text_decoded.lower()]
        print(f"  Keywords match: {found}")
        if len(r.text) > 200:
            print(f"  Snippet: {text_decoded[:150]}...")
    except Exception as e:
        print(f"  Error: {e}")
