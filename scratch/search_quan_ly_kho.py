with open('Quản lý Kho.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
out = []
for m in re.finditer(r'id=["\']\w*filter\w*["\']|class=["\']\w*filter\w*["\']|Hoa Lan|Cầu Kiệu', content, re.IGNORECASE):
    out.append(f"Found match in Quản lý Kho.html: {m.group()} at {m.start()}")

with open('scratch/quan_ly_kho_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print(f"Done searching Quản lý Kho.html, found {len(out)} matches")
