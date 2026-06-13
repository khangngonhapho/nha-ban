import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if 'function renderImageEditorWidget' in line or 'renderImageEditorWidget =' in line:
        print(f"Found renderImageEditorWidget at line {i+1}: {line.strip()}")
        # print next 100 lines
        for j in range(i, min(i+150, len(lines))):
            print(f"  {j+1}: {lines[j]}")
        break
