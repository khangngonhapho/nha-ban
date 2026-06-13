with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
found = False
for idx, line in enumerate(lines):
    if 'id="filterPanel"' in line or "id='filterPanel'" in line:
        found = True
        out.append(f"Line {idx+1}: {line.strip()}")
        # print 30 lines after to see the HTML wrapper
        for i in range(idx, min(len(lines), idx + 40)):
            out.append(f"    {i+1}: {lines[i].rstrip()}")
        break

if not found:
    print("Could not find id='filterPanel' in HTML body")
else:
    with open('scratch/filter_html.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print("Written HTML definition to scratch/filter_html.txt")
