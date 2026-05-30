import re
from bs4 import BeautifulSoup
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\Temp\Quản lý Kho76.79.html"

with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("--- ALL DATE PATTERNS IN HTML ---")
# Let's search for dd/mm/yyyy or yyyy-mm-dd patterns in text or attributes
date_pattern = re.compile(r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{4}\b|\b\d{4}[/\-]\d{1,2}[/\-]\d{1,2}\b')

matches = []
for node in soup.find_all(text=True):
    txt = node.strip()
    if not txt:
        continue
    if node.parent and node.parent.name in ['script', 'style']:
        continue
    for m in date_pattern.finditer(txt):
        matches.append((txt, m.group(), node.parent.name))

# Also search inside all input/hidden elements
for inp in soup.find_all('input'):
    for attr, val in inp.attrs.items():
        val_str = str(val)
        for m in date_pattern.finditer(val_str):
            matches.append((f"Input attr '{attr}'='{val_str}'", m.group(), inp.name))

print(f"Found {len(matches)} date instances:")
for idx, (context, date_val, tag) in enumerate(matches):
    print(f"[{idx+1}] Date: '{date_val}' in <{tag}> -> Context: '{context[:200]}'")

# Let's search for specific terms: "cập nhật", "ngày" inside label or spans
print("\n--- SEARCHING FOR LABELS WITH 'CẬP NHẬT' OR 'NGÀY' ---")
for tag in soup.find_all(['label', 'span', 'div', 'p', 'th', 'td']):
    txt = tag.text.strip()
    if not txt:
        continue
    if any(term in txt.lower() for term in ['cập nhật', 'cap nhat', 'ngày', 'ngay tao', 'ngay cap nhat', 'ngay dang', 'đăng tin', 'last update', 'updated']):
        # print if short
        if len(txt) < 150:
            print(f"Tag <{tag.name}> class={tag.get('class')} id={tag.get('id')}: '{txt}'")
