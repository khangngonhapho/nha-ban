import io
import sys
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\Temp\Quản lý Kho76.79.html"

with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

for lbl in soup.find_all("label"):
    if lbl.text.strip().lower() == "mô tả":
        print("Label HTML:", str(lbl))
        sib = lbl.find_next_sibling()
        if sib:
            print("Sibling Tag Name:", sib.name)
            print("Sibling Attributes:", sib.attrs)
            print("Sibling Text Content (First 200 chars):")
            print(sib.text.strip()[:200])
            print("Sibling Inner HTML (First 500 chars):")
            print(str(sib)[:500])
            print("-" * 40)
