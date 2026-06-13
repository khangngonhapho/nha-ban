with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

lines = html.split('\n')

header_line = -1
for i, line in enumerate(lines):
    if '<header' in line:
        header_line = i
        break

output = []
if header_line != -1:
    output.append(f"Header starts at line {header_line + 1}\n")
    for j in range(header_line, min(header_line + 150, len(lines))):
        output.append(f"{j+1}: {lines[j]}\n")
else:
    output.append("No header tag found!\n")

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/inspect_header_placement_output.txt', 'w', encoding='utf-8') as f_out:
    f_out.write("".join(output))

print("Wrote output to scratch/inspect_header_placement_output.txt")
