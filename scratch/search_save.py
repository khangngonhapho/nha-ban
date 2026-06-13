with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find occurrences of editPublicInteriorIndices and look for lines around them
matches = [m.start() for m in re.finditer('editPublicInteriorIndices', content)]
with open('scratch/save_search_results.txt', 'w', encoding='utf-8') as out:
    for m in matches:
        line_no = content[:m].count('\n') + 1
        start = max(0, m - 300)
        end = min(len(content), m + 500)
        out.write(f"Line {line_no}:\n")
        out.write(content[start:end])
        out.write("\n" + "="*80 + "\n")
print(f"Done search. Found {len(matches)} matches.")
