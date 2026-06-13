import sys
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("=== Searching for tabs in Thien Khoi Group - Nguon Hang.html ===")
for text in ["Danh sách nguồn hàng", "Danh sách nguồn hàng"]:
    elements = soup.find_all(string=lambda s: s and text in s)
    print(f"Found {len(elements)} elements for '{text}'")
    for el in elements:
        parent = el.parent
        print(f"Parent tag: {parent.name}, class: {parent.get('class')}, id: {parent.get('id')}")
        # Print grand-parent
        gp = parent.parent
        if gp:
            print(f"Grand-parent tag: {gp.name}, class: {gp.get('class')}, id: {gp.get('id')}")
            # Print outer HTML of grand-parent
            print("Outer HTML:")
            print(gp.prettify()[:1000])
        print("-" * 50)
