import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

with open('crawl_pipeline.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'tk_id' in line or 'Ma_Hang' in line or 'ma_hang' in line:
        if len(line.strip()) < 120:
            print(f"Line {idx+1}: {line.strip()}")
