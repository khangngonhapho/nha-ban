import os
import sys
import re
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
    
    print("=== Decoded Images ===")
    img_urls = []
    for idx, img in enumerate(soup.find_all('img')):
        srcset = img.get('srcset')
        if srcset:
            match = re.search(r'url=([^&]+)', srcset)
            if match:
                encoded_url = match.group(1)
                decoded_url = urllib.parse.unquote(encoded_url)
                if "cloudfront.net" in decoded_url:
                    img_urls.append(decoded_url)
                    print(f"[{len(img_urls)}] Decoded: {decoded_url}")
                    
    print(f"\nTotal decoded Cloudfront URLs: {len(img_urls)}")
else:
    print("File not found")
