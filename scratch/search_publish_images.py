with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find occurrences of sodo1Url, customCoverUrl, and editPublicInteriorIndices in the saving/publishing functions
matches = [m.start() for m in re.finditer(r'saveSourceChanges|saveNewListingFromPool|publish', content)]
with open('scratch/save_images_logic.txt', 'w', encoding='utf-8') as out:
    for m in matches:
        line_no = content[:m].count('\n') + 1
        start = max(0, m - 50)
        end = min(len(content), m + 3500)
        out.write(f"Line {line_no}:\n")
        out.write(content[start:end])
        out.write("\n" + "="*80 + "\n")
print(f"Done. Found {len(matches)} matches.")
