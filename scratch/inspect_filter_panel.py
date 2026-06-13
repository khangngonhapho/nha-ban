import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's search for id="filterPanel" or class="filter-panel"
lines = html.split('\n')
for i, line in enumerate(lines):
    if 'id="filterPanel"' in line or 'class="filter-panel"' in line:
        print(f"Found filter panel at line {i+1}: {line.strip()}")
        # print next 80 lines
        for j in range(i, min(i+100, len(lines))):
            print(f"  {j+1}: {lines[j]}")
        break
