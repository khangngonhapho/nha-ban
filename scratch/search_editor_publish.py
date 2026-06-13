with open('curator.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'publish' in line.lower() and 'fetch' in line:
        clean_line = line.strip().encode('ascii', errors='replace').decode('ascii')
        print(f"{idx+1}: {clean_line}")
