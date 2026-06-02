import io
import sys
import re
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\Temp\Quản lý Kho76.79.html"

with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

soup_detail = BeautifulSoup(html, "html.parser")

sys.path.append(r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo")
import crawl_pipeline

link_fb = crawl_pipeline.get_val_by_label(soup_detail, "facebook") or crawl_pipeline.get_val_by_label(soup_detail, "fb")
if not link_fb:
    a_fb = soup_detail.find("a", href=re.compile(r'facebook\.com', re.I))
    if a_fb:
        link_fb = a_fb.get("href", "")

print("Link FB extracted:", link_fb)
