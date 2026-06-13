with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
out = []
# Search for JS style changes on structural elements
patterns = [
    r'\.style\.display\s*=',
    r'\.style\.width\s*=',
    r'\.style\.flex\s*=',
    r'\.style\.position\s*=',
    r'classList\.add',
    r'classList\.toggle'
]

for pat in patterns:
    for m in re.finditer(pat, content):
        pos = m.start()
        # Get context
        start = max(0, pos - 80)
        end = min(len(content), pos + 120)
        line_num = content[:pos].count('\n') + 1
        out.append(f"Match for '{pat}' at line {line_num}:")
        out.append(content[start:end].strip().replace('\n', ' '))
        out.append("-" * 50)

with open('scratch/js_layout_changes.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done searching JS style changes")
