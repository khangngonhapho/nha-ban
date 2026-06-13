import os
import sys
import re
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
    
    # Let's search for typical listing identifiers, e.g. "Mã:" or numbers like "tỷ"
    # Find all divs containing text "tỷ" or "m²"
    print("=== Searching for divs with real estate terms ===")
    count = 0
    for div in soup.find_all('div'):
        # Check if this div has text and does not contain child divs to find leaf nodes
        if div.text and not div.find('div'):
            txt = div.text.strip()
            # If it contains "tỷ" or "m²" or "m2" or "tầng"
            if any(term in txt.lower() for term in ["tỷ", "m²", "m2", "tầng", "phòng"]):
                print(f"Div (class={div.get('class')}): {txt[:100]}")
                count += 1
                if count > 20:
                    break
                    
    # Let's search for URLs of images
    print("\n=== Searching for image URLs ===")
    img_urls = []
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src')
        if src:
            img_urls.append(src)
    print(f"Total img tags: {len(img_urls)}")
    print(f"Sample images: {img_urls[:10]}")
    
    # Search for all URLs that look like CDN or details
    print("\n=== Searching for details links ===")
    details_links = []
    for a in soup.find_all('a'):
        href = a.get('href')
        if href and ('detail' in href.lower() or 'hang' in href.lower() or 'san-pham' in href.lower() or 'house' in href.lower() or 'post' in href.lower()):
            details_links.append((a.text.strip(), href))
    print(f"Total detail-like links: {len(details_links)}")
    for txt, href in details_links[:10]:
        print(f"  Text: {txt} -> Link: {href}")

else:
    print(f"File {fn} does not exist.")
