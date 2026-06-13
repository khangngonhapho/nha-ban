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
    
    # Save to a text file so we can view it
    with open("scratch/dumped_detail_text.txt", "w", encoding="utf-8") as out:
        out.write("=== ALL TEXT ELEMENTS ===\n\n")
        for tag in soup.find_all(['p', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'button', 'li']):
            # Print tags that have direct text and no children of these types to get leaf nodes
            if tag.text and not tag.find(['p', 'span', 'div', 'li']):
                txt = tag.text.strip()
                if txt:
                    out.write(f"<{tag.name} class={tag.get('class')} id={tag.get('id')}>: {txt}\n")
                    
    print("[+] Dumped all leaf text elements to scratch/dumped_detail_text.txt")
else:
    print("File not found")
