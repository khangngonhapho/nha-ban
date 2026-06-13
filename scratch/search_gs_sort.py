with open('pool_backend_v3.gs', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r'(?i)\.sort', content)]
print(f"Found {len(matches)} matches in pool_backend_v3.gs")
for m in matches:
    start = max(0, m - 100)
    end = min(len(content), m + 150)
    print(content[start:end].replace('\n', ' '))
    print("-" * 50)
