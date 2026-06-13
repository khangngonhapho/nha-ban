import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

keywords = ["refresh", "token", "refreshToken", "refresh-token"]

# Search in BDS-KhangNgo files
search_dirs = [
    "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo",
    "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch",
    "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New_files"
]

for d in search_dirs:
    if not os.path.exists(d):
        continue
    print(f"\n=== Scanning directory: {d} ===")
    for f in os.listdir(d):
        fpath = os.path.join(d, f)
        if os.path.isfile(fpath) and f.endswith((".py", ".js", ".html", "tải xuống")):
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_in:
                    content = file_in.read()
                matches = []
                for kw in keywords:
                    if kw in content:
                        # Find occurrences
                        matches.append(kw)
                if matches:
                    print(f"  [📄 File] {f} matched: {matches}")
                    # Print context for refresh
                    if "refresh" in matches:
                        pos = content.find("refresh")
                        print(f"    Context: ... {content[max(0, pos-40):min(len(content), pos+80)].replace('\n', ' ')} ...")
            except Exception as e:
                pass
