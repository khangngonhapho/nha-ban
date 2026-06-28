import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk("."):
    if any(p in root for p in [".git", "__pycache__", "build", "dist", "dist (1)", "scratch"]):
        continue
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            with open(fp, 'r', encoding='utf-8') as file:
                for i, line in enumerate(file):
                    if "raw_archive_temp_read.db" in line:
                        print(f"{fp} Line {i+1}: {line.strip()}")
