import os
import sys
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Danh Sach.html"
if os.path.exists(path):
    soup = BeautifulSoup(open(path, encoding='utf-8').read(), 'html.parser')
    
    # Search for potential scroll container
    print("=== Overflow elements ===")
    overflow_els = soup.find_all(class_=lambda x: x and ('overflow-auto' in x or 'overflow-y-auto' in x or 'custom-scrollbar' in x))
    for idx, el in enumerate(overflow_els):
        print(f"[{idx+1}] {el.name} class={el.get('class')}")
        # Print child text summaries
        txt = el.text.strip()
        print(f"    Text snippet: {repr(txt[:100])}")
        
    print("\n=== Spinner or Loading elements ===")
    spinner_els = soup.find_all(class_=lambda x: x and any(term in x.lower() for term in ["spinner", "loading", "load", "animate-spin"]))
    for idx, el in enumerate(spinner_els[:10]):
        print(f"[{idx+1}] {el.name} class={el.get('class')}")
else:
    print("File not found")
