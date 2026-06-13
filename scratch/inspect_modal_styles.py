import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/index_styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Let's search for keywords in css: modal, detail, preview, overlay
lines = css.split('\n')
for i, line in enumerate(lines):
    if any(kw in line for kw in ['.modal', '#detailModal', '.modal-content', '.detail-container', 'openS', 'openPoolS']):
        print(f"Line {i+1}: {line.strip()}")
        # print around it
        start = max(0, i - 2)
        end = min(len(lines), i + 15)
        print("---")
        for j in range(start, end):
            print(f"  {j+1}: {lines[j]}")
        print("==================\n")
