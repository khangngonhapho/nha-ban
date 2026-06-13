with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
for idx in range(3399, min(len(lines), 3505)):
    out.append(f"{idx+1}: {lines[idx].rstrip()}")

with open('scratch/query_lines.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print("Done writing to scratch/query_lines.txt")
