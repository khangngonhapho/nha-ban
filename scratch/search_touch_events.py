with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

lines = html.split('\n')
output = []
for i, line in enumerate(lines):
    if 'touchstart' in line or 'touchmove' in line or 'touchend' in line or 'touch-action' in line:
        output.append(f"Line {i+1}: {line.strip()}\n")
        for j in range(max(0, i-2), min(len(lines), i+10)):
            output.append(f"  {j+1}: {lines[j]}\n")
        output.append("="*50 + "\n")

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/search_touch_events_output.txt', 'w', encoding='utf-8') as f_out:
    f_out.write("".join(output))

print("Wrote output to scratch/search_touch_events_output.txt")
