import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if 'window.openS = function' in line or 'function openS(' in line:
        start_line = i
        # print lines from start_line + 350 onwards
        for j in range(start_line + 350, min(start_line + 550, len(lines))):
            print(f"  {j+1}: {lines[j]}")
        break
