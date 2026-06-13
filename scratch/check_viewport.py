with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = list(re.finditer(r'<meta[^>]*viewport[^>]*>', content, re.IGNORECASE))
out = []
for m in matches:
    out.append(f"Found viewport tag: {m.group()} at position {m.start()}")

if not matches:
    out.append("No viewport meta tag found!")
    # Let's search for any meta tags
    out.append("\nAll meta tags:")
    for m in re.finditer(r'<meta[^>]*>', content, re.IGNORECASE):
        out.append(m.group())

with open('scratch/viewport_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done checking viewport tag")
