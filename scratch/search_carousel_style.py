with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
out = []
# Search for carousel styling
selectors = [
    r'carouselNha',
    r'carouselSo',
    r'accPool',
    r'admin-scroll-carousel'
]

for sel in selectors:
    for m in re.finditer(sel, content):
        pos = m.start()
        line_num = content[:pos].count('\n') + 1
        out.append(f"Match for '{sel}' at line {line_num}:")
        out.append(content[pos-100:pos+300])
        out.append("-" * 40)

with open('scratch/carousel_style_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done searching carousel styles")
