import os
import sys
from bs4 import BeautifulSoup
import urllib.parse

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

fn = "Thien Khoi Group - Nguon Hang - Chi Tiet New.html"
path = f"d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/{fn}"

if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    print("=== Image tags with their surrounding HTML context ===")
    for idx, img in enumerate(soup.find_all('img')):
        src = img.get('src')
        # Print parent class, alt, and check if inside swiper or tab
        parent = img.parent
        grandparent = parent.parent if parent else None
        
        # Look up recursive parents to find if any has class or id containing 'legal', 'document', 'sodo', 'diagram', 'swiper', etc.
        p = img
        labels = []
        while p:
            if p.name:
                classes = p.get('class', [])
                id_val = p.get('id', '')
                if id_val:
                    labels.append(f"id:{id_val}")
                for c in classes:
                    if any(term in c.lower() for term in ["legal", "document", "sodo", "diagram", "swiper", "tab", "panel"]):
                        labels.append(f"class:{c}")
            p = p.parent
            
        print(f"[{idx+1}] src={src} | Alt={img.get('alt')} | Labels={list(set(labels))}")
        
else:
    print("File not found")
