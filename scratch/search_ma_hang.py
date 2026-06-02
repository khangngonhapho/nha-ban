import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def search_files(paths, keyword):
    for path in paths:
        if not os.path.exists(path):
            continue
        print(f"\n--- Searching in {path} for '{keyword}' ---")
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            if keyword in line:
                print(f"Line {idx+1}: {line.strip()}")

search_files(['curator_server.py', 'crawl_pipeline.py'], 'Ma_Hang')
search_files(['curator_server.py', 'crawl_pipeline.py'], 'TK-')
