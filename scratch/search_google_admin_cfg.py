with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'gClientId' in line or 'Cấu hình Google Admin' in line or 'g_access_token' in line:
        print(f"Line {i+1}: {line.strip()[:150]}")
