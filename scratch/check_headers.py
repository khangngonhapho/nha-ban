import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

with open('curator_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

found = False
for idx, line in enumerate(lines):
    if 'POOL_HEADERS = [' in line:
        found = True
        print(f"Found POOL_HEADERS at line {idx+1}")
        for i in range(idx, idx + 45):
            print(lines[i].strip())
        break
