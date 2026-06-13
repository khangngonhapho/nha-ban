import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

keywords = ["Noi_dung_chinh", "Nội dung chính"]

for root_dir, dirs, files in os.walk("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"):
    if any(p in root_dir.lower() for p in [".git", "__pycache__", "build", "dist", "node_modules"]):
        continue
    for file in files:
        if file.endswith((".py", ".gs", ".html", ".js")):
            path = os.path.join(root_dir, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                for kw in keywords:
                    if kw in content:
                        print(f"Found '{kw}' in: {os.path.relpath(path, 'd:/LHTBrain/01_PROJECTS/BDS-KhangNgo')}")
            except Exception:
                pass
