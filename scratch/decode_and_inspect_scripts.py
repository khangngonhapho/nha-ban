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
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    
    print(f"Total scripts: {len(scripts)}")
    
    for idx, s in enumerate(scripts):
        if not s.string:
            continue
        
        # Decode unicode escapes in the script text for search
        # We can use a regex to replace \uXXXX with actual characters
        decoded_text = s.string
        try:
            # Simple decoder for unicode escapes
            decoded_text = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), decoded_text)
        except Exception as e:
            pass
            
        # Search for key patterns in the decoded text
        # "phạm văn hai" or "hẻm 2 ô tô" or "24" or head agent "nam"
        if "phạm văn hai" in decoded_text.lower() or "hoàng nam" in decoded_text.lower() or "cư xá" in decoded_text.lower() or "24 tỷ" in decoded_text:
            print(f"\n[+] Script {idx} matches property data! (Decoded length: {len(decoded_text)})")
            print(f"  Snippet (first 500 chars):")
            print(decoded_text[:500])
            print("...")
            
            # Let's save the decoded script to a file
            out_path = f"scratch/decoded_script_{idx}.txt"
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(decoded_text)
            print(f"  Saved decoded script to {out_path}")
            
            # Search for any phone numbers inside this script
            phones = re.findall(r'\b0\d{9}\b|\b0\d{2}[-.\s]\d{3}[-.\s]\d{4}\b', decoded_text)
            print(f"  Phones in this script: {phones}")
            
            # Search for image URLs in the decoded text
            # E.g. Cloudfront, spms2, thienkhoi, etc.
            urls = re.findall(r'https?://[^\s"\'><]*?\.(?:jpg|jpeg|png)', decoded_text, re.I)
            # Also check for images in custom paths
            print(f"  Image URLs in script: {len(urls)}")
            if urls:
                print(f"    Sample image URLs: {list(set(urls))[:10]}")
else:
    print("File not found")
