with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Find occurrences of setupScrollCarousel in index.html to see how images are filtered for display
matches = [m.start() for m in re.finditer(r'setupScrollCarousel', content)]
with open('scratch/client_images_display.txt', 'w', encoding='utf-8') as out:
    for m in matches:
        line_no = content[:m].count('\n') + 1
        start = max(0, m - 300)
        end = min(len(content), m + 1000)
        out.write(f"Line {line_no}:\n")
        out.write(content[start:end])
        out.write("\n" + "="*80 + "\n")
print(f"Done. Found {len(matches)} matches.")
