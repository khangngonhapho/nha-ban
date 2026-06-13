import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

for cls in ['admin-card-inner', 'admin-card-left', 'admin-img-wrapper']:
    count = content.count(cls)
    print(f"Class '{cls}' count:", count)
    # find where it occurs
    for i, line in enumerate(content.split('\n')):
        if cls in line:
            print(f"  Line {i+1}: {line.strip()[:120]}")
