import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if 'c.className = p.isFromPoolOnly' in line:
        # print from line i to line i + 80
        for j in range(i, min(i+100, len(lines))):
            print(f"  {j+1}: {lines[j]}")
        break
