with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
out = []
# Find functions that render listing cards
for m in re.finditer(r'function\s+\w*card\w*|class=["\']\w*admin-card\w*["\']|id=["\']\w*admin\w*["\']', content, re.IGNORECASE):
    pos = m.start()
    line_num = content[:pos].count('\n') + 1
    out.append(f"Match for '{m.group()}' at line {line_num}:")
    out.append(content[pos:pos+200])
    out.append("-" * 40)

# Search for "is-admin" or "adminMode"
for m in re.finditer(r'adminMode|isAdmin', content):
    pos = m.start()
    line_num = content[:pos].count('\n') + 1
    out.append(f"Match for admin variable at line {line_num}:")
    out.append(content[pos-50:pos+150])
    out.append("-" * 40)

with open('scratch/admin_list_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done searching admin list properties")
