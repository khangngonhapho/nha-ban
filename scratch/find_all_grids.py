with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Regex to find selectors and display properties
css_blocks = re.finditer(r'([^{]+)\{([^}]+)\}', content)
out = []
for m in css_blocks:
    selector = m.group(1).strip()
    body = m.group(2)
    if 'display' in body and ('flex' in body or 'grid' in body):
        pos = m.start()
        line_num = content[:pos].count('\n') + 1
        # Extract display property line
        display_line = ""
        for line in body.split('\n'):
            if 'display' in line:
                display_line = line.strip()
                break
        out.append(f"Line {line_num}: {selector} -> {display_line}")

with open('scratch/all_display_rules.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done listing display rules")
