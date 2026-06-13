import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for the start of openS
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'window.openS = function' in line or 'function openS(' in line:
        start_line = i
        print(f"openS definition starts at line {start_line+1}")
        # print lines from start_line to start_line + 150
        for j in range(start_line, min(start_line + 120, len(lines))):
            print(f"  {j+1}: {lines[j]}")
        break
