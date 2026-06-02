import io
import sys
import re
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\Temp\Quản lý Kho76.79.html"

with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

out_lines = []
out_lines.append("--- SEARCHING FOR UPDATE/DATE FIELDS IN HTML ---")

# Let's search all tags that contain text related to update, date, day, time, ngày, cập nhật, tạo
search_terms = [
    r'cập nhật', r'update', r'ngày', r'tạo', r'date', r'time', r'last', r'lần cuối'
]

# Find text nodes or labels containing these terms
found_items = []
for el in soup.find_all(text=True):
    txt = el.strip()
    if not txt:
        continue
    # skip large scripts or styles
    if el.parent and el.parent.name in ['script', 'style']:
        continue
        
    for term in search_terms:
        if re.search(term, txt, re.I):
            # Capture parent details
            p_tag = el.parent
            siblings = [s.text.strip() for s in p_tag.find_next_siblings()[:2] if s.text.strip()]
            siblings_str = " | ".join(siblings)
            found_items.append(f"Text: '{txt}' -> Parent: <{p_tag.name} class='{p_tag.get('class', '')}' id='{p_tag.get('id', '')}'> -> Sibling text: '{siblings_str}'")
            break

out_lines.append(f"Total matching elements: {len(found_items)}")
for idx, item in enumerate(found_items[:50]): # limit to 50
    out_lines.append(f"[{idx+1}] {item}")

# Let's also look for any form inputs/elements that might contain datetime or date values
out_lines.append("\n--- SEARCHING FOR DATE/TIME INPUTS ---")
for inp in soup.find_all(['input', 'span', 'div', 'p', 'label']):
    # check attributes
    for attr, val in inp.attrs.items():
        val_str = str(val)
        if any(term in val_str.lower() for term in ['date', 'time', 'ngay', 'capnhat', 'created', 'updated']):
            out_lines.append(f"Tag: <{inp.name}>, Attribute: '{attr}'='{val_str}' -> Text: '{inp.text.strip()[:100]}'")

output_str = "\n".join(out_lines)

with open(r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\scratch\date_search_results.txt", "w", encoding="utf-8") as f:
    f.write(output_str)

print("SUCCESS: Output written to scratch/date_search_results.txt")
