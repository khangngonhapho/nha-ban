import re

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/index_styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

def find_blocks(selectors):
    print(f"\n=== Searching for selectors: {selectors} ===")
    pattern = r'(?:^|\s)(' + '|'.join(re.escape(s) for s in selectors) + r')\s*(?:,[^{]+)*\s*{(.*?)}'
    matches = re.finditer(pattern, css, re.DOTALL)
    for m in matches:
        selector_name = m.group(1)
        body = m.group(2).strip()
        # print first few lines of the body or full body if short
        lines = body.split('\n')
        snippet = '\n'.join(lines[:15])
        if len(lines) > 15:
            snippet += f"\n... (truncated {len(lines)-15} lines)"
        print(f"{selector_name} {{\n{snippet}\n}}")

# Let's inspect .card, #list, main, etc.
find_blocks(['main', '#list', '.card', '.card-grid', '.modal', '.detail-modal', '.card-container'])

# Find media queries in CSS
print("\n=== All Media Queries in CSS ===")
media_matches = re.finditer(r'@media\s*([^{]+)\s*{(.*?)}', css, re.DOTALL)
for m in media_matches:
    query = m.group(1).strip()
    body = m.group(2).strip()
    # Let's check size of body and print first few lines
    lines = body.split('\n')
    snippet = '\n'.join(lines[:8])
    if len(lines) > 8:
        snippet += f"\n... (truncated {len(lines)-8} lines)"
    print(f"@media {query} {{\n{snippet}\n}}")
