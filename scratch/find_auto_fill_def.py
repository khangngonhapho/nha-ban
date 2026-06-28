import os

filepath = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_detail_admin.js"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if "autoFillCurationDetails" in line:
        out.append(f"Line {idx+1}: {line.strip()}\n")

# Let's search for function autoFillCurationDetails definitions
# Usually it's defined like `function autoFillCurationDetails()` or `window.autoFillCurationDetails = ...`
for idx, line in enumerate(lines):
    if "autoFillCurationDetails" in line and ("function" in line or "=" in line):
        # print 50 lines around it
        start = max(0, idx - 5)
        end = min(len(lines), idx + 100)
        out.append(f"\n--- Around Line {idx+1} ---\n")
        for j in range(start, end):
            out.append(f"{j+1}: {lines[j]}")

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/search_func.txt", "w", encoding="utf-8") as f_out:
    f_out.writelines(out)
