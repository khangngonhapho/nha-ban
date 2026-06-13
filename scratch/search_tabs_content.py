import os
import sys
import re
import json

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
        
    print(f"HTML length: {len(html)}")
    
    # 1. Search for phone numbers (e.g. 09xx or 03xx or 07xx or 08xx)
    print("\n=== Searching for Phone Numbers ===")
    phones = re.findall(r'\b0[35789]\d{8}\b|\b02\d{8,9}\b', html)
    # Filter out common ones if we know them
    print(f"Found phone numbers: {list(set(phones))}")
    
    # Let's search for some text around these phone numbers to see context
    for phone in set(phones):
        pos = html.find(phone)
        print(f"  Phone {phone} at position {pos}:")
        print(html[max(0, pos-80):min(len(html), pos+150)])
        print("-" * 40)
        
    # 2. Search for images (JPEG/JPG/PNG URLs)
    print("\n=== Searching for Image URLs ===")
    img_urls = re.findall(r'https?://[^\s"\'><]*?\.(?:jpg|jpeg|png)', html, re.I)
    print(f"Found {len(img_urls)} image URLs.")
    for idx, img in enumerate(list(set(img_urls))[:15]):
        print(f"  [{idx+1}] {img}")
        
    # 3. Check what's in the self.__next_f.push scripts
    print("\n=== Inspecting scripts ===")
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    print(f"Total scripts: {len(scripts)}")
    
    # Let's find script elements that contain "chủ nhà" or phone numbers
    for idx, s in enumerate(scripts):
        if s.string and ("chủ nhà" in s.string or "chuNha" in s.string or any(p in s.string for p in phones)):
            print(f"  Script {idx} contains landlord/phone info! Length: {len(s.string)}")
            # Print a portion of the script content
            # Let's write this script to a temp file for inspection
            out_fn = f"scratch/detail_script_{idx}.txt"
            with open(out_fn, "w", encoding="utf-8") as out:
                out.write(s.string)
            print(f"    Saved script {idx} content to {out_fn}")

else:
    print("File not found")
