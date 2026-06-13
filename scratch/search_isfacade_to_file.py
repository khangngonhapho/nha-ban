with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r'isFacadeUrl', content)]
with open('scratch/isfacade_matches.txt', 'w', encoding='utf-8') as out:
    out.write(f"Found {len(matches)} matches for isFacadeUrl\n")
    for m in matches:
        line_no = content[:m].count('\n') + 1
        start = max(0, m - 100)
        end = min(len(content), m + 200)
        out.write(f"Line {line_no}: {content[start:end]}\n")
        out.write("-" * 50 + "\n")
print(f"Done. Found {len(matches)} matches.")
