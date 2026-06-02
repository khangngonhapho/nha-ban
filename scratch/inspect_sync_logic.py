import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Search for the function that merges Pool to Source or similar
with open('pool_backend_v3.gs', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find function declarations or comments
lines = content.split('\n')
current_func = ""
for idx, line in enumerate(lines):
    if "function" in line:
        current_func = line.strip()
    if any(k in line for k in ["Source", "source", "PUBLIC", "public", "sync", "Sync", "merge", "Merge"]):
        print(f"Line {idx+1} [{current_func[:40]}]: {line.strip()}")
