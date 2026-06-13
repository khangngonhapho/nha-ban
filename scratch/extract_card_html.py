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
    
    # Find the link with warehouse/sources
    link = soup.find('a', href=lambda x: x and 'warehouse/sources/' in x)
    if link:
        print("[+] Found a link!")
        # Find its ancestor that represents the whole card
        # Let's go up a few parents to find the main container (e.g. flex flex-col)
        parent = link
        for i in range(5):
            parent = parent.parent
            if parent and parent.get('class') and any('bg-white' in c for c in parent.get('class')):
                break
        
        print(f"Parent tag: {parent.name}, class: {parent.get('class')}")
        # Pretty print the HTML of this parent
        print("\n=== Card HTML ===")
        print(parent.prettify()[:2500])
        
        # Save to file
        with open("scratch/sample_card_prettified.html", "w", encoding="utf-8") as out:
            out.write(parent.prettify())
        print("\n[+] Saved full card HTML to scratch/sample_card_prettified.html")
    else:
        print("[-] Could not find any link with warehouse/sources/")
else:
    print(f"File {fn} does not exist.")
