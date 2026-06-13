import os
import sys
import re

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
        
    print(f"File length: {len(html)}")
    
    # Let's search for common strings that would be in the detailed tabs:
    # "Chủ nhà", "Điện thoại", "Sổ đỏ", "Sơ đồ", "Hợp đồng"
    # We will search inside the script blocks
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    
    for idx, s in enumerate(scripts):
        if not s.string:
            continue
        # Find if it contains any property data
        # For example, let's search for "phạm văn hai" or "24" or the head agent's name "Nguyễn Hoàng Nam"
        if "phạm văn hai" in s.string.lower() or "hoàng nam" in s.string.lower():
            print(f"\n--- Script {idx} matches property data! (Length: {len(s.string)}) ---")
            # Let's search if there are typical patterns of images or texts
            # Let's write this script to scratch/script_data_{idx}.txt
            out_path = f"scratch/script_data_{idx}.txt"
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(s.string)
            print(f"  Saved script content to {out_path}")
            
            # Let's print the first 500 characters of the script to see what it is
            print("  Snippet:")
            print(s.string[:500])
            print("...")
            
            # Let's do a regex search for any phone number inside this script
            phones = re.findall(r'\b0\d{9}\b|\b0\d{2}[-.\s]\d{3}[-.\s]\d{4}\b', s.string)
            print(f"  Phones in this script: {phones}")
            
            # Let's do a regex search for image URLs or files inside this script
            urls = re.findall(r'https?://[^\s"\'><]*?\.(?:jpg|jpeg|png)', s.string, re.I)
            print(f"  Images in this script: {len(urls)}")
            if urls:
                print(f"    Sample images: {urls[:5]}")
else:
    print("File not found")
