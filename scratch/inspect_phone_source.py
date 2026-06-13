import os
import sys
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New.html"

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("=== Looking for '0941151187' in HTML ===")
elements = soup.find_all(string=lambda s: s and "0941151187" in s)
for idx, el in enumerate(elements):
    parent = el.parent
    print(f"[{idx+1}] Parent tag: {parent.name}, class: {parent.get('class')}")
    print(parent.prettify()[:1000])
    print("-" * 50)
