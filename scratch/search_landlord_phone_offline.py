import os
import sys
import re
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New.html"

if not os.path.exists(path):
    print("File not found")
    sys.exit(1)

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=== Scanning text for 10-digit phone numbers ===")
# Find all 10 digit numbers starting with 0
text = soup.get_text()
phones = re.findall(r'0\d{9}|0\d{2}\s\d{3}\s\d{4}|0\d{3}\s\d{3}\s\d{3}', text)
print(f"Phones found in text: {list(set(phones))}")

# Let's search inside the script tags as well
print("\n=== Scanning script tags for phone numbers ===")
for idx, s in enumerate(soup.find_all('script')):
    if s.string:
        matches = re.findall(r'0\d{9}', s.string)
        if matches:
            print(f"Script {idx} contains phone numbers: {list(set(matches))}")
            # Print context for first match
            pos = s.string.find(matches[0])
            print(f"  Context: {s.string[max(0, pos-50):min(len(s.string), pos+100)]}")

# Let's print out text around words like 'chủ nhà', 'sđt', 'điện thoại', 'chính chủ'
print("\n=== Context for contact-related keywords ===")
for keyword in ["chủ nhà", "chủ", "điện thoại", "đầu chủ", "sđt"]:
    elements = soup.find_all(string=lambda s: s and keyword in s.lower())
    print(f"Keyword '{keyword}' matches: {len(elements)}")
    for el in elements[:5]:
        print(f"  [{el.parent.name}]: {el.strip()[:150]}")
