import os

filepath = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/manager.py"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if "fetch_google_doc_content" in line or "doc_prompt" in line:
        start = max(0, idx - 5)
        end = min(len(lines), idx + 20)
        out.append(f"--- Line {idx+1} ---\n")
        for j in range(start, end):
            out.append(f"{j+1}: {lines[j]}")
        out.append("-----------------\n")

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/search_doc_fetch.txt", "w", encoding="utf-8") as f_out:
    f_out.writelines(out)

print("Search completed.")
