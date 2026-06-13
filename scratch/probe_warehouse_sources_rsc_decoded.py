import os
import sys
import requests
import re
import json

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
    "RSC": "1",
    "Accept": "text/x-component",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://proptech.thienkhoi.com/warehouse"
}

url = "https://proptech.thienkhoi.com/warehouse/sources"
print(f"Requesting: {url} with RSC: 1")
r = requests.get(url, headers=headers, timeout=15)
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('Content-Type')}")
print(f"Raw Length: {len(r.text)}")

# Save raw RSC response
with open("scratch/raw_rsc_sources.txt", "w", encoding="utf-8") as f:
    f.write(r.text)

# Decode unicode escapes in r.text
def decode_escapes(text):
    # E.g. replace \u1ea7 with character
    try:
        # We can decode it using codecs or json
        # Since r.text can contain invalid json block directly, let's use regex
        return re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), text)
    except Exception as e:
        print(f"Error decoding escapes: {e}")
        return text

decoded = decode_escapes(r.text)
print(f"Decoded Length: {len(decoded)}")

# Search for some keywords in decoded
found = []
for kw in ["trần", "phạm", "đường", "tỷ", "triệu", "trần văn đang", "phạm văn hai", "mã nguồn hàng"]:
    if kw in decoded.lower():
        found.append(kw)

print(f"Matches found in decoded text: {found}")

# Write first 5000 characters of decoded to see what it is
print("\n=== First 2000 chars of decoded ===")
print(decoded[:2000])

# Let's save decoded to a file
with open("scratch/decoded_rsc_sources.txt", "w", encoding="utf-8") as f:
    f.write(decoded)
print("\nSaved decoded text to scratch/decoded_rsc_sources.txt")
