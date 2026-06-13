import os
import sys
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

fn = "Thien Khoi Group - Nguon Hang - Danh Sach.html"
path = f"d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/{fn}"

if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    titles = soup.find_all('p', {'data-testid': 'title-property'})
    print(f"Total titles found: {len(titles)}")
    for idx, t in enumerate(titles):
        print(f"[{idx+1}] {t.text.strip()}")
else:
    print("File not found")
