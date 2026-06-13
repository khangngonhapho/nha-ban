import sys

sys.stdout = open("scratch/functions_filtered.txt", "w", encoding="utf-8")

with open("scratch/all_functions.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    line_lower = line.lower()
    if "edit" in line_lower or "show" in line_lower or "open" in line_lower or "image" in line_lower:
        print(line.strip())

sys.stdout.close()
