with open('curator_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r'(?i)\.sort|sorted', content)]
print(f"Found {len(matches)} matches in curator_server.py")
for m in matches:
    start = max(0, m - 100)
    end = min(len(content), m + 150)
    snippet = content[start:end]
    if "index" in snippet or "interior" in snippet or "alley" in snippet or "img" in snippet:
        print(snippet.replace('\n', ' '))
        print("-" * 50)
