import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

folder_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New_files"

if os.path.exists(folder_path):
    files = os.listdir(folder_path)
    js_files = [f for f in files if f.endswith((".js", "tải xuống"))]
    
    print(f"Scanning {len(js_files)} JS files...")
    
    api_patterns = [
        # Match routes starting with /api/ or similar
        r'["\'`](/[a-zA-Z0-9_\-\/]+?/api/[a-zA-Z0-9_\-\/]+?)["\'`]',
        r'["\'`](/api/[a-zA-Z0-9_\-\/]+?)["\'`]',
        r'["\'`](/warehouse/[a-zA-Z0-9_\-\/]+?)["\'`]',
        r'["\'`](/sources/[a-zA-Z0-9_\-\/]+?)["\'`]',
        # Match any string containing a URL format or host
        r'https?://[a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9_\-\.\/]+',
    ]
    
    found_urls = set()
    for f in js_files:
        fpath = os.path.join(folder_path, f)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_in:
                content = file_in.read()
            for pattern in api_patterns:
                matches = re.findall(pattern, content)
                for m in matches:
                    if len(m) < 150 and not any(term in m for term in ["w3.org", "react", "google", "facebook", "github", "favicon"]):
                        found_urls.add(m)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    print(f"\nFound {len(found_urls)} unique potential URLs/endpoints:")
    for url in sorted(list(found_urls)):
        print(f"  {url}")
else:
    print("Folder does not exist")
