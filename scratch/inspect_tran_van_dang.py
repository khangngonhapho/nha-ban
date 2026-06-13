import sys
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Danh Sach.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("=== Searching for 'Trần Văn Đang' in Thien Khoi Group - Nguon Hang - Danh Sach.html ===")
elements = soup.find_all(string=lambda s: s and "Trần Văn Đang" in s)
print(f"Found {len(elements)} elements")
for idx, el in enumerate(elements):
    parent = el.parent
    print(f"[{idx+1}] Parent tag: {parent.name}, class: {parent.get('class')}")
    # Print outer HTML of parent
    print(parent.prettify()[:500])
    print("-" * 50)
