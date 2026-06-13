import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

folder_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New_files"

if not os.path.exists(folder_path):
    print("Folder does not exist")
    sys.exit(1)

files = os.listdir(folder_path)
js_files = [f for f in files if f.endswith((".js", "tải xuống"))]

print(f"Scanning {len(js_files)} JS files...")

# List of interesting keywords to look for in the JS files
keywords = [
    "api/warehouse",
    "warehouse/sources",
    "sources/detail",
    "sources/",
    "sources?",
    "getDetail",
    "getSources",
    "getProperty",
    "detail-information",
    "legal-document",
    "Next-Action",
    "next-action",
    "NextAction",
    "NEXT_ACTION",
    "actionId",
    "action_id"
]

for f in js_files:
    fpath = os.path.join(folder_path, f)
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_in:
            content = file_in.read()
            
        found = []
        for kw in keywords:
            if kw in content:
                found.append(kw)
                
        if found:
            print(f"\n[📄 File] {f} (Size: {len(content)} bytes)")
            print(f"  Keywords matched: {found}")
            
            # Find and print some context for each keyword
            for kw in found:
                pos = content.find(kw)
                # Print 150 chars context around it
                start = max(0, pos - 50)
                end = min(len(content), pos + 100)
                snippet = content[start:end].replace('\n', ' ')
                print(f"    - '{kw}': ... {snippet} ...")
                
    except Exception as e:
        print(f"Error reading {f}: {e}")
