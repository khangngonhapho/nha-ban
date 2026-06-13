with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

lines = html.split('\n')

toggle_filter_line = -1
for i, line in enumerate(lines):
    if 'function toggleFilter(' in line or 'window.toggleFilter =' in line:
        toggle_filter_line = i
        break

output = []
if toggle_filter_line != -1:
    output.append(f"toggleFilter starts at line {toggle_filter_line + 1}\n")
    for j in range(toggle_filter_line, min(toggle_filter_line + 80, len(lines))):
        output.append(f"{j+1}: {lines[j]}\n")
else:
    output.append("No toggleFilter function found!\n")

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/inspect_toggle_filter_output.txt', 'w', encoding='utf-8') as f_out:
    f_out.write("".join(output))

print("Wrote output to scratch/inspect_toggle_filter_output.txt")
