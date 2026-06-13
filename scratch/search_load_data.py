with open("index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

results = []
for i, line in enumerate(lines):
    if "fetch(" in line and "spreadsheets" in line:
        results.append(f"Line {i+1}: {line.strip()}")
    elif "async function loadData" in line or "loadData(" in line:
        results.append(f"Line {i+1}: {line.strip()}")

with open("scratch/load_data_search.txt", "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(results))
print("Done")
