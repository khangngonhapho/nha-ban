import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Search for patterns like 1[a-zA-Z0-9-_]{43} in .py, .json, .gs, .md files
id_pattern = re.compile(r'1[a-zA-Z0-9-_]{43}')

found_ids = {}

for root, dirs, files in os.walk('.'):
    # skip node_modules, git, pycache
    if any(p in root for p in ['.git', '__pycache__', 'node_modules', 'dist', 'build']):
        continue
    for file in files:
        if file.endswith(('.py', '.json', '.gs', '.md', '.bat')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                matches = id_pattern.findall(content)
                if matches:
                    for m in matches:
                        if m not in found_ids:
                            found_ids[m] = []
                        found_ids[m].append(f"{path}")
            except Exception as e:
                pass

print("Found Google Sheet / Drive Folder IDs:")
for fid, paths in found_ids.items():
    print(f"ID: {fid}")
    print(f"  Present in: {list(set(paths))[:5]}")
