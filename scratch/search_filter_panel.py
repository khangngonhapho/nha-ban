with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = list(re.finditer(r'#filterPanel', content))
out_lines = []
for m in matches:
    start = max(0, m.start() - 100)
    end = min(len(content), m.end() + 600)
    out_lines.append(f"Position {m.start()}:")
    out_lines.append(content[start:end])
    out_lines.append("-" * 50)

with open('scratch/filter_panel_styles.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))
print(f"Done writing {len(matches)} matches to scratch/filter_panel_styles.txt")
