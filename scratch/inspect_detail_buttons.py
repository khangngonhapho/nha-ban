import os
from bs4 import BeautifulSoup

path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/sources_page_body.html"

if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    
    print("=== All button elements on the detail page ===")
    for idx, btn in enumerate(soup.find_all("button")):
        print(f"[{idx+1}] class={btn.get('class')} text='{btn.text.strip()}' attributes={list(btn.attrs.keys())}")
        
    print("\n=== Elements with role='tab' ===")
    for idx, tab in enumerate(soup.find_all(attrs={"role": "tab"})):
        print(f"[{idx+1}] text='{tab.text.strip()}' data-state={tab.get('data-state')} id={tab.get('id')}")
        
    print("\n=== Elements containing 'chủ nhà' or 'điện thoại' ===")
    for idx, el in enumerate(soup.find_all(text=True)):
        if el.parent.name not in ["script", "style"]:
            txt = el.strip()
            if txt and any(term in txt.lower() for term in ["chủ nhà", "điện thoại", "liên hệ", "sđt", "chủ"]):
                print(f"[{idx+1}] {el.parent.name}: {txt}")
else:
    print("Detail page body HTML not found")
