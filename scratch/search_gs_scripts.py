import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

scripts = ['pool_backend_v3.gs', 'source_sheet_ai.gs']
for s in scripts:
    if os.path.exists(s):
        print(f"\n--- Searching in {s} ---")
        with open(s, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            if 'openById' in line or 'SpreadsheetApp' in line or '1klR' in line or '1PJY' in line or '1to1' in line:
                print(f"Line {idx+1}: {line.strip()}")
