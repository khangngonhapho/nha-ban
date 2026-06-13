with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
out = []
# Search for "Bất động sản" or "Sổ thửa đất"
for m in re.finditer(r'Bất động sản|Sổ thửa đất|Sơ đồ thửa đất', content):
    pos = m.start()
    line_num = content[:pos].count('\n') + 1
    out.append(f"Match for '{m.group()}' at line {line_num}:")
    out.append(content[pos-100:pos+300])
    out.append("-" * 40)

with open('scratch/sodo_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done searching")
