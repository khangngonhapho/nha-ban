with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
for idx in range(6984, min(len(lines), 7045)):
    out.append(f"{idx+1}: {lines[idx].rstrip()}")

with open('scratch/admin_panel_html.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done writing to scratch/admin_panel_html.txt")
