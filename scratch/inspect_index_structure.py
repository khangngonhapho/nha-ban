import re

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find style tags or check the layout divs
print("File length:", len(content))

# Look for media queries in the CSS
media_queries = re.findall(r'@media[^{]+{[^}]+}', content)
print("\n--- Existing media queries ---")
for mq in media_queries[:15]:
    print(mq)

# Look for card grid/list container
print("\n--- Potential list containers or card classes ---")
for line in content.split('\n'):
    if 'class="card' in line or 'id="list' in line or 'class="list' in line or 'id="cards' in line or 'id="grid' in line:
        print(line.strip()[:120])
    if 'id="detailModal"' in line or 'class="modal"' in line:
        print("Modal element:", line.strip()[:120])
