import os
import sys
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
    
    imgs = soup.find_all('img')
    print(f"Total images: {len(imgs)}")
    for idx, img in enumerate(imgs):
        print(f"[{idx+1}] img: src={img.get('src')}")
        if img.get('srcset'):
            print(f"    srcset: {img.get('srcset')[:200]}...")
            
    # Check if there is a directory for files
    folder_path = f"d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New_files"
    if os.path.exists(folder_path):
        print(f"\n[+] Found complete files folder: {folder_path}")
        files = os.listdir(folder_path)
        print(f"    Total files in folder: {len(files)}")
        print(f"    Sample files: {files[:10]}")
    else:
        print(f"\n[-] Complete files folder not found.")
else:
    print("File not found")
