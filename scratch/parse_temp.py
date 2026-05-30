import io
import sys
from bs4 import BeautifulSoup
import re

# Force standard output to utf-8 if possible
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\Temp\Quản lý Kho76.79.html"

with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

out_lines = []
out_lines.append("--- DEMO PARSING ---")
out_lines.append(f"Title: {soup.title.string if soup.title else 'None'}")

# Find description label and its value
def get_val_by_label(soup, label_name):
    # exact label matching
    for lbl in soup.find_all("label"):
        text = lbl.text.strip().lower()
        if label_name in text:
            sibling = lbl.find_next_sibling()
            if sibling:
                return sibling.text.strip()
            # or parent sibling
            parent = lbl.parent
            if parent:
                for child in parent.children:
                    if child != lbl and child.name in ["span", "div", "textarea", "input", "p"]:
                        return child.text.strip()
    return None

out_lines.append(f"Mô tả (get_val_by_label): {get_val_by_label(soup, 'mô tả')}")
out_lines.append(f"Nội dung chính: {soup.select_one('#Detail_sNoiDung').text.strip() if soup.select_one('#Detail_sNoiDung') else 'None'}")
out_lines.append(f"Địa chỉ: {soup.select_one('#Detail_sDiaChi').text.strip() if soup.select_one('#Detail_sDiaChi') else 'None'}")
out_lines.append(f"Facebook label: {get_val_by_label(soup, 'facebook')}")

out_lines.append("\n--- TEXT TEXTAREAS ---")
for ta in soup.find_all("textarea"):
    out_lines.append(f"Textarea ID={ta.get('id')}, Name={ta.get('name')}:")
    out_lines.append(ta.text.strip()[:300])
    out_lines.append("-" * 20)

out_lines.append("\n--- LABELS AND SIBLINGS ---")
for lbl in soup.find_all("label"):
    text = lbl.text.strip()
    sib = lbl.find_next_sibling()
    sib_text = sib.text.strip()[:150] if sib else "None"
    out_lines.append(f"Label: '{text}' -> Sibling: '{sib_text}'")

output_str = "\n".join(out_lines)

with open(r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\scratch\output.txt", "w", encoding="utf-8") as f:
    f.write(output_str)

print("SUCCESS: Output written to scratch/output.txt")
