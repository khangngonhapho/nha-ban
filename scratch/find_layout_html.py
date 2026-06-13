with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Find where body starts and show its content till list starts
body_start = content.find("<body>")
list_start = content.find('id="list"')
filter_start = content.find('id="filterPanel"')

out = []
out.append(f"body_start: {body_start}")
out.append(f"list_start: {list_start}")
out.append(f"filter_start: {filter_start}")

if list_start != -1 and filter_start != -1:
    first = min(list_start, filter_start)
    last = max(list_start, filter_start)
    out.append("--- Structure between body and first layout element ---")
    out.append(content[body_start:first])
    out.append("--- Structure between first and last layout element ---")
    out.append(content[first:last + 500])

with open('scratch/layout_html_structure.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done writing layout structure to scratch/layout_html_structure.txt")
