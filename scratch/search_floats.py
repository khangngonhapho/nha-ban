with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = list(re.finditer(r'float\s*:', content, re.IGNORECASE))
out = []
for m in matches:
    pos = m.start()
    line_num = content[:pos].count('\n') + 1
    out.append(f"Found float at line {line_num}:")
    out.append(content[pos-50:pos+150])
    out.append("-" * 50)

with open('scratch/floats_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done searching floats")
