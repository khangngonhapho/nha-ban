import re
import os
import sys

keywords = ["Tự động điền", "autofill", "auto-fill", "AI", "lên sóng", "publish", "public"]
target_files = [
    "static/js/lego_detail_admin.js",
    "static/js/lego_core.js",
    "static/js/lego_render_admin.js",
    "curator.html",
    "index.html"
]

out_lines = []

for filename in target_files:
    filepath = os.path.join("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo", filename)
    if not os.path.exists(filepath):
        out_lines.append(f"File not found: {filepath}\n")
        continue
    out_lines.append(f"\n=== Searching in {filename} ===\n")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # search for keywords
    lines = content.splitlines()
    for i, line in enumerate(lines):
        for kw in keywords:
            if kw.lower() in line.lower():
                out_lines.append(f"Line {i+1}: {line.strip()[:200]}\n")
                break

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/search_results.txt", "w", encoding="utf-8") as out_f:
    out_f.writelines(out_lines)

print("Search completed. Output written to scratch/search_results.txt")
