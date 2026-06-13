import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if 'admin-card-left' in line:
        print(f"Line {i+1}: {line.strip()[:150]}")
        # print around it
        start = max(0, i - 10)
        end = min(len(lines), i + 35)
        for j in range(start, end):
            print(f"  {j+1}: {lines[j]}")
        print("==================\n")
