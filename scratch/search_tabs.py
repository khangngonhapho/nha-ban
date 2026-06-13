with open('curator.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'switchTab' in line or 'tab-button' in line or 'tab-content' in line or 'active-tab' in line:
        clean_line = line.strip().encode('ascii', errors='replace').decode('ascii')
        print(f"{idx+1}: {clean_line}")
