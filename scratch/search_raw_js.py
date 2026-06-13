import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

folder_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New_files"

if os.path.exists(folder_path):
    files = os.listdir(folder_path)
    js_files = [f for f in files if f.endswith((".js", "tải xuống")) and not any(term in f for term in ["map.js", "util.js", "common.js", "places.js", "main.js"])]
    
    for f in js_files:
        fpath = os.path.join(folder_path, f)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_in:
                content = file_in.read()
            
            for kw in ["warehouse", "sources"]:
                pos = 0
                count = 0
                while True:
                    pos = content.lower().find(kw, pos)
                    if pos == -1:
                        break
                    print(f"File: {f} | Keyword: {kw} at position {pos}:")
                    print(content[max(0, pos-100):min(len(content), pos+150)])
                    print("-" * 50)
                    count += 1
                    pos += len(kw)
                    if count >= 3:
                        break
        except Exception as e:
            print(f"Error reading {f}: {e}")
else:
    print("Folder does not exist")
