with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if 'function toggleFilter(' in line or 'function closeFilter(' in line or 'filterOpen =' in line:
        out.append(f"Line {idx+1}: {line.strip()}")
        # print context
        start = max(0, idx - 10)
        end = min(len(lines), idx + 25)
        out.append("Context:")
        for i in range(start, end):
            prefix = "--> " if i == idx else "    "
            out.append(f"{prefix}{i+1}: {lines[i].rstrip()}")
        out.append("=" * 60)

with open('scratch/filter_js_contexts.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done writing JS contexts")
