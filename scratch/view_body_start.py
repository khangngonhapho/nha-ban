with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
for idx in range(3669, min(len(lines), 3745)):
    out.append(f"{idx+1}: {lines[idx].rstrip()}")

with open('scratch/body_start_html.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done writing body start")
