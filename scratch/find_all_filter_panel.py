with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if '#filterPanel' in line:
        out.append(f"Line {idx+1}: {line.strip()}")
        # print 5 lines before and after
        start_idx = max(0, idx - 8)
        end_idx = min(len(lines), idx + 8)
        out.append("Context:")
        for i in range(start_idx, end_idx):
            prefix = "--> " if i == idx else "    "
            out.append(f"{prefix}{i+1}: {lines[i].rstrip()}")
        out.append("=" * 60)

with open('scratch/filter_panel_all_contexts.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print(f"Written context to scratch/filter_panel_all_contexts.txt")
