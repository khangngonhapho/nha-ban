import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

keywords = ["proptech", "warehouse", "sources"]
print("=== Searching for references to new TK website ===")

for root_dir, dirs, files in os.walk("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"):
    # Skip .git, __pycache__, build, dist, node_modules
    if any(p in root_dir.lower() for p in [".git", "__pycache__", "build", "dist", "node_modules"]):
        continue
    for file in files:
        if file.endswith((".py", ".gs", ".html", ".js", ".json", ".txt")):
            path = os.path.join(root_dir, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                for kw in keywords:
                    if kw in content:
                        # Find occurrences
                        count = content.count(kw)
                        print(f"Found '{kw}' ({count} times) in: {os.path.relpath(path, 'd:/LHTBrain/01_PROJECTS/BDS-KhangNgo')}")
            except Exception as e:
                pass
