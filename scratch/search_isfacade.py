with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r'isFacadeUrl', content)]
print(f"Found {len(matches)} matches for isFacadeUrl")
for m in matches:
    line_no = content[:m].count('\n') + 1
    start = max(0, m - 100)
    end = min(len(content), m + 200)
    print(f"Line {line_no}: {content[start:end].replace('\n', ' ')}")
    print("-" * 50)
