with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if '.crow {' in line or '.crow{' in line or '.ibox {' in line or '.ibox{' in line:
        out.append(f"Line {idx+1}: {line.strip()}")
        start = max(0, idx - 5)
        end = min(len(lines), idx + 10)
        out.append("Context:")
        for i in range(start, end):
            prefix = "--> " if i == idx else "    "
            out.append(f"{prefix}{i+1}: {lines[i].rstrip()}")
        out.append("=" * 60)

with open('scratch/crow_css_contexts.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done searching card layout styles")
