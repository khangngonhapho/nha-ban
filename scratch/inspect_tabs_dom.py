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
    
    # Let's list all elements with class containing 'tabs' or 'tab'
    # or elements with attribute data-state or role="tabpanel"
    tabpanels = soup.find_all(attrs={"role": "tabpanel"})
    print(f"Total tab panels found: {len(tabpanels)}")
    for idx, panel in enumerate(tabpanels):
        print(f"Panel {idx+1}: id={panel.get('id')}, class={panel.get('class')}, data-state={panel.get('data-state')}")
        # Print a snippet of its text
        print(f"  Text snippet: {panel.get_text().strip()[:200]}")
        print("-" * 50)
        
    # Check if there are script tags containing large JSON strings or chunks
    # that might contain data of other tabs
    print("\n=== Searching for next_f or NEXT_DATA script blocks ===")
    scripts = soup.find_all('script')
    for idx, s in enumerate(scripts):
        if s.string:
            # Look for keywords that represent landlord or phone or sodo
            matches = []
            for kw in ["chuNha", "phone", "sodo", "soDo", "chu_nha", "chủ nhà", "pháp lý"]:
                if kw in s.string:
                    matches.append(kw)
            if matches:
                print(f"Script {idx}: contains keywords {matches}. Length: {len(s.string)}")
                # Write script content to a scratch file
                with open(f"scratch/detail_script_match_{idx}.txt", "w", encoding="utf-8") as out:
                    out.write(s.string)
                print(f"  Saved matching script to scratch/detail_script_match_{idx}.txt")
else:
    print("File not found")
