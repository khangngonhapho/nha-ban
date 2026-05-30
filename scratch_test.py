with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if 'if (isAdmin && isTokenValid)' in line:
        print(f"Match found at line {idx}: {line.strip()}")
        break
