import os
import re

for root, dirs, files in os.walk('.'):
    # Ignore git, cache and build dirs
    if any(p in root for p in ['.git', '__pycache__', 'build', 'dist', 'node_modules']):
        continue
    for f in files:
        if f.endswith(('.html', '.js', '.py')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file_obj:
                    for i, line in enumerate(file_obj, 1):
                        if 'POOL_HEADERS' in line:
                            clean_line = line.strip().encode('ascii', 'ignore').decode('ascii')
                            print(f"{path}:{i} -> {clean_line}")
            except Exception as e:
                pass
