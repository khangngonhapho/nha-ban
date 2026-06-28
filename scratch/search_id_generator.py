import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

search_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
query = "def gen"
query2 = "generate"

for root, dirs, files in os.walk(search_dir):
    if ".git" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if query in content or query2 in content:
                    lines = content.split('\n')
                    for idx, line in enumerate(lines, start=1):
                        if query in line or query2 in line:
                            print(f"{file}:{idx}: {line.strip()}")
            except Exception:
                pass
