with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = list(re.finditer(r'position\s*:', content, re.IGNORECASE))
out = []
for m in matches:
    pos = m.start()
    line_num = content[:pos].count('\n') + 1
    out.append(f"Found position at line {line_num}:")
    out.append(content[pos-100:pos+300])
    out.append("-" * 50)

with open('scratch/positions_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done searching positions")
