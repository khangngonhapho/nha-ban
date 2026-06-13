import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all media queries
matches = re.finditer(r'@media[^{]+\{', content)
out_lines = []
out_lines.append("--- MEDIA QUERIES FOUND ---")
for m in matches:
    start = max(0, m.start() - 100)
    end = min(len(content), m.end() + 500)
    out_lines.append(f"Position {m.start()}:")
    out_lines.append(content[m.start():end])
    out_lines.append("-" * 50)

with open('scratch/media_queries.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))
print("Done writing to scratch/media_queries.txt")
