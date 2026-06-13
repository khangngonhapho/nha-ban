import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

lines = html.split('\n')

targets = ['filter-panel', 'filterPanel', 'sheet', 'overlay', '@media', '.sbody']

for target in targets:
    print(f"=== Matches for '{target}' ===")
    count = 0
    for i, line in enumerate(lines):
        if target in line:
            # Check if this is within the style section (approximate line check, say lines < 3700)
            if i + 1 < 3700:
                print(f"Line {i+1}: {line.strip()}")
                # Print subsequent lines until we hit a closing brace
                for j in range(i + 1, min(i + 30, len(lines))):
                    print(f"  {lines[j].rstrip()}")
                    if '}' in lines[j] and '{' not in lines[j]:
                        break
                print("-" * 40)
                count += 1
                if count > 30:
                    print("... truncated ...")
                    break
