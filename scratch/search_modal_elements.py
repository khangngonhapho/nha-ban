import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
count = 0
for i, line in enumerate(lines):
    if 'modal' in line.lower() or 'detail' in line.lower():
        count += 1
        if count < 50:
            print(f"Line {i+1}: {line.strip()[:150]}")

print("Total matches:", count)
