import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/detail_script_match_23.txt"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    print(f"Content length: {len(content)}")
    # Search for all strings starting with https://
    urls = re.findall(r'https?://[^\s"\'><]*', content)
    print(f"Found {len(urls)} URLs in Script 23:")
    for u in list(set(urls))[:10]:
        print(f"  {u}")
        
    # Search for vietnamese text or key terms in Script 23
    for term in ["chủ nhà", "chuNha", "phone", "sodo", "sổ đỏ", "pháp lý"]:
        matches = [m.start() for m in re.finditer(term, content, re.I)]
        print(f"Keyword '{term}': found {len(matches)} occurrences at positions: {matches}")
        for pos in matches[:3]:
            print(f"  Context around {pos}:")
            print(content[max(0, pos-50):min(len(content), pos+100)])
            print("-" * 30)
else:
    print("File not found")
