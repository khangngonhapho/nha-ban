import os
import sys
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

fn = "nha_ban_1.html"
path = f"d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/{fn}"

if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    print(f"Title: {soup.title.text.strip() if soup.title else 'No title'}")
    print(f"Body text snippet (first 1000 chars):")
    print(soup.body.get_text()[:1000] if soup.body else soup.get_text()[:1000])
else:
    print(f"File {fn} does not exist.")
