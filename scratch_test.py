import os

path = "d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\index.html"
with open(path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

with open("scratch/includes_ty.txt", "w", encoding="utf-8") as out:
    for idx, line in enumerate(lines, 1):
        if "tỷ" in line and "includes" in line:
            out.write(f"Line {idx}: {line.strip()}\n")
