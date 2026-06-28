import os

filepath = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_e2e_curation.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if "btnAutoFillCuration" in line or "autoFillCurationDetails" in line or "dialog" in line or "accept" in line or "confirm" in line or "ai" in line.lower():
        out.append(f"Line {idx+1}: {line.strip()}\n")
        # print 5 lines before and after
        start = max(0, idx - 5)
        end = min(len(lines), idx + 10)
        out.append("--- Code chunk ---\n")
        for j in range(start, end):
            out.append(f"  {j+1}: {lines[j]}")
        out.append("-----------------\n")

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/test_e2e_curation_search.txt", "w", encoding="utf-8") as f_out:
    f_out.writelines(out)

print("Search in test_e2e_curation.py completed.")
