import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if 'is-pool-card' in line and i > 2500:
        print(f"Found is-pool-card at line {i+1}: {line.strip()[:150]}")
        # print 30 lines before and 60 lines after
        start = max(0, i - 15)
        end = min(len(lines), i + 40)
        for j in range(start, end):
            print(f"  {j+1}: {lines[j]}")
        print("==================\n")
        break
