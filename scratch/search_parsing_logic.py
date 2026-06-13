import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

for fn in ["crawl_pipeline.py", "curator_server.py"]:
    path = f"d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/{fn}"
    if os.path.exists(path):
        print(f"=== File: {fn} ===")
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            if "Noi_dung_chinh" in line or "Nội dung chính" in line:
                print(f"  Line {idx+1}: {line.strip()}")
