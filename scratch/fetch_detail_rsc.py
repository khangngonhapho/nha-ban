import os
import sys
import requests

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

cookie_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/thienkhoi_cookie.txt"

with open(cookie_path, 'r', encoding='utf-8') as f:
    cookie_str = f.read().strip()

# Extract accessToken
access_token = None
for part in cookie_str.split(";"):
    part = part.strip()
    if part.startswith("TKG_accessToken="):
        access_token = part.split("=", 1)[1]
        break

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": cookie_str,
    "RSC": "1",
    "Accept": "text/x-component",
    "Referer": "https://proptech.thienkhoi.com/warehouse/sources"
}

uuid = "19c74ebc-e5a4-4cfb-844b-3ae5365e6318"
url = f"https://proptech.thienkhoi.com/warehouse/sources/{uuid}"

print(f"Fetching RSC Detail Page: {url}")
r = requests.get(url, headers=headers, timeout=10)
print(f"Status: {r.status_code}")
print(f"Response Length: {len(r.text)}")

# Save to file
os.makedirs("scratch", exist_ok=True)
with open("scratch/raw_detail_rsc.txt", "w", encoding="utf-8") as f:
    f.write(r.text)

print("\nSearching for phone numbers in raw RSC text:")
print("  Contains 0941151187 (Landlord?):", "0941151187" in r.text)
print("  Contains 0944666655 (Đầu chủ):", "0944666655" in r.text)

# Search case-insensitive for some key strings in raw RSC
found_terms = []
for term in ["núi thành", "nui thanh", "thương hiền", "võ thương hiền"]:
    if term in r.text.lower():
        found_terms.append(term)
print(f"Found terms: {found_terms}")
