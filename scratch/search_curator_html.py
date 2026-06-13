with open('curator.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
out = []
for m in re.finditer(r'id=["\']\w*filter\w*["\']|class=["\']\w*filter\w*["\']', content, re.IGNORECASE):
    out.append(f"Found filter match in curator.html: {m.group()} at {m.start()}")

with open('scratch/curator_filter_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print(f"Done searching curator.html, found {len(out)} matches")
