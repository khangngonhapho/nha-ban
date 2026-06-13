import os
import sys
import re
from bs4 import BeautifulSoup

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
    
    print(f"Title of Page: {soup.title.text.strip() if soup.title else 'No Title'}")
    
    # Let's search for typical labels in Vietnamese for property attributes:
    # "Giá chốt", "Giá chào", "Đầu chủ", "Chủ nhà", "Điện thoại", "Sổ đỏ", "Sơ đồ", "Hợp đồng"
    # We will search for all elements containing these keywords
    keywords = ["giá chốt", "giá chào", "đầu chủ", "chủ nhà", "điện thoại", "sơ đồ", "hợp đồng", "phân loại", "phòng ngủ", "toilet", "vệ sinh", "hướng", "đường vào"]
    
    print("\n=== Searching for key terms and their adjacent values ===")
    for kw in keywords:
        found_els = soup.find_all(text=re.compile(rf'{kw}', re.I))
        print(f"Keyword '{kw}': found {len(found_els)} occurrences.")
        for el in found_els[:5]:
            # Print parent text
            parent = el.parent
            text = parent.get_text().strip()
            print(f"  [{parent.name} class={parent.get('class')}]: {text[:150]}")
            
    # Search for all image tags and print their source
    print("\n=== Searching for Images ===")
    imgs = soup.find_all('img')
    print(f"Total img tags: {len(imgs)}")
    for img in imgs[:15]:
        src = img.get('src') or img.get('data-src')
        alt = img.get('alt')
        print(f"  Img: src={src}, alt={alt}, class={img.get('class')}")
        
    # Search for links that look like Facebook or other contact info
    print("\n=== Searching for external links ===")
    links = soup.find_all('a')
    for a in links:
        href = a.get('href')
        if href and ('facebook' in href.lower() or 'tel:' in href.lower() or 'zalo' in href.lower()):
            print(f"  Link: text={a.text.strip()} -> href={href}")

else:
    print("File not found")
