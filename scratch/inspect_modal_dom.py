with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

lines = html.split('\n')

output = []
for i, line in enumerate(lines):
    if 'class="overlay' in line or 'class="sheet' in line or 'id="detailModal"' in line:
        output.append(f"Line {i+1}: {line.strip()}\n")
        for j in range(max(0, i - 2), min(len(lines), i + 20)):
            output.append(f"  {j+1}: {lines[j]}\n")
        output.append("="*50 + "\n")

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/inspect_modal_dom_output.txt', 'w', encoding='utf-8') as f_out:
    f_out.write("".join(output))

print("Wrote output to scratch/inspect_modal_dom_output.txt")
