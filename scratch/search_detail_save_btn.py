with open("index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

results = []
for i, line in enumerate(lines):
    if "saveSourceChanges" in line or "saveNewListingFromPool" in line:
        results.append(f"Line {i+1}: {line.strip()}")

with open("scratch/detail_save_btn_search.txt", "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(results))
print("Done")
