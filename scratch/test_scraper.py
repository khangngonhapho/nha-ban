import io
import sys
import re
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\Temp\Quản lý Kho76.79.html"

with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

soup_detail = BeautifulSoup(html, "html.parser")

# Let's import get_val_by_label and safe_get_val from crawl_pipeline
sys.path.append(r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo")
import crawl_pipeline

ma_hang_scraped = crawl_pipeline.get_val_by_label(soup_detail, "mã hàng") or "TEST_ID"

mo_ta_scraped = crawl_pipeline.get_val_by_label(soup_detail, "mô tả")
if not mo_ta_scraped:
    lbl_mota = soup_detail.find("label", string=re.compile(r'mô tả', re.I))
    if lbl_mota and lbl_mota.find_next_sibling():
        mo_ta_scraped = lbl_mota.find_next_sibling().text.strip()

print("1. mo_ta_scraped from crawl_pipeline:", mo_ta_scraped)

# Let's see how crawl_pipeline get_val_by_label works
print("2. crawl_pipeline.get_val_by_label(soup_detail, 'mô tả'):", crawl_pipeline.get_val_by_label(soup_detail, "mô tả"))

# Let's print out what is returned by the full crawl_pipeline.extract_listing_details if applicable, 
# or look at the code of crawl_pipeline.py where get_val_by_label is defined.
print("\n--- CODE OF crawl_pipeline.get_val_by_label ---")
import inspect
try:
    print(inspect.getsource(crawl_pipeline.get_val_by_label))
except Exception as e:
    print("Error:", e)
