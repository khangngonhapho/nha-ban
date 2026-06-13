with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
out = []

# Search for width styles on main structural elements
selectors = [
    r'body\s*\{[^}]*width',
    r'main\s*\{[^}]*width',
    r'#list\s*\{[^}]*width',
    r'\.sheet\s*\{[^}]*width',
    r'\.filter-panel\s*\{[^}]*width',
    r'header\s*\{[^}]*width',
    r'grid-template-columns',
    r'flex-basis',
    r'flex\s*:\s*[0-9]'
]

out.append("--- REGEX MATCHES FOR WIDTH/LAYOUT STYLE ---")
for sel in selectors:
    for m in re.finditer(sel, content, re.IGNORECASE):
        # print match and line number
        pos = m.start()
        line_num = content[:pos].count('\n') + 1
        out.append(f"Match for '{sel}' at line {line_num}:")
        start = max(0, pos - 100)
        end = min(len(content), m.end() + 200)
        out.append(content[pos:end])
        out.append("-" * 40)

with open('scratch/layout_width_search.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done searching layout width properties")
