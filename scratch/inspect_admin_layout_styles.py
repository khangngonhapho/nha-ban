import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if '.sbody' in line or 'accordion' in line or 'accPool' in line or 'accSource' in line:
        if '{' in line:
            print(f"Line {i+1}: {line.strip()}")
            # print next 10 lines
            for j in range(i+1, min(i+15, len(lines))):
                print(f"  {lines[j].rstrip()}")
                if '}' in lines[j]:
                    break
            print("---")
