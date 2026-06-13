with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

lines = html.split('\n')

# Find body {
body_lines = []
for i, line in enumerate(lines):
    if line.strip() == 'body {':
        body_lines.append(i + 1)

print(f"body {{ found at lines: {body_lines}")

# Find mobile media query and filter-panel inside it
for i, line in enumerate(lines):
    if '@media (max-width: 767px)' in line:
        print(f"Mobile media query starts at line {i+1}")
        # Search for .filter-panel inside this media query
        for j in range(i, min(i + 150, len(lines))):
            if '.filter-panel {' in lines[j]:
                print(f"  .filter-panel {{ found at line {j+1}")
                # Print the block
                for k in range(j, j + 25):
                    print(f"    {k+1}: {lines[k]}")
                break
