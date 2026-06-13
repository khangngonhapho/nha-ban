import os
import sys
from bs4 import BeautifulSoup
import re

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
    
    print("=== Searching for Pagination Elements ===")
    
    # 1. Search for buttons or links containing numbers or next/prev icons
    # e.g. pagination classes
    pagination_els = soup.find_all(class_=lambda x: x and any(term in x.lower() for term in ["pagination", "page", "paging", "loadmore", "scroll"]))
    print(f"Found {len(pagination_els)} elements with paging-related classes.")
    for idx, el in enumerate(pagination_els[:10]):
        print(f"  [{idx+1}] {el.name} class={el.get('class')}: {el.text.strip()[:100]}")
        
    # 2. Search for all button tags and text in details
    buttons = soup.find_all('button')
    print(f"\nTotal button elements: {len(buttons)}")
    for idx, btn in enumerate(buttons):
        txt = btn.text.strip()
        if txt:
            print(f"  Button {idx+1}: {txt}")
            
    # 3. Look for links containing page parameters or next/prev text
    links = soup.find_all('a')
    page_links = []
    for a in links:
        href = a.get('href', '')
        text = a.text.strip()
        if 'page=' in href.lower() or 'p=' in href.lower() or any(term in text.lower() for term in ["sau", "tiếp", "trước", "next", "prev"]):
            page_links.append((text, href))
            
    print(f"\nFound {len(page_links)} page-related links:")
    for text, href in page_links:
        print(f"  Text: {text} -> href: {href}")
        
    # 4. Search the raw JS inside script tags for pagination variables like page, limit, pageSize, total, offset, scroll
    print("\n=== Searching for pagination in scripts ===")
    scripts = soup.find_all('script')
    for idx, s in enumerate(scripts):
        if s.string:
            for kw in ["pageSize", "pageIndex", "totalPages", "totalItems", "pageNumber", "limit", "offset", "pagination"]:
                if kw in s.string:
                    print(f"  Script {idx} contains keyword '{kw}'! (Length: {len(s.string)})")
                    # Find context
                    pos = s.string.find(kw)
                    print(f"    Context: {s.string[max(0, pos-50):min(len(s.string), pos+100)]}")
                    
else:
    print("File not found")
