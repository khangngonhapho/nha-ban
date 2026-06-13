with open("index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

results = []
for i, line in enumerate(lines):
    if "SHEET_ID" in line:
        results.append(f"Line {i+1}: {line.strip()}")

with open("scratch/sheet_id_search.txt", "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(results))
print("Done")
