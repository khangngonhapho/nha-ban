import re

with open("index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

results = []
for i, line in enumerate(lines):
    if "function" in line or "=>" in line:
        # Check if it looks like a function definition
        if "function " in line or " = function" in line or "const " in line or "let " in line:
            results.append(f"Line {i+1}: {line.strip()}")

with open("scratch/all_functions.txt", "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(results))
print(f"Found {len(results)} matches.")
