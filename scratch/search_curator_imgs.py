with open('curator.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'curator-image-grid' in line or 'image-station' in line or 'image-grid' in line:
        print(f"Line {i+1}: {line.strip()}")
