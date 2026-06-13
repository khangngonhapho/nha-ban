with open("index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

results = []
for i, line in enumerate(lines):
    if "savePoolBtn" in line or "save-pool-btn" in line:
        results.append(f"Line {i+1}: {line.strip()}")

with open("scratch/save_pool_btn_search.txt", "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(results))
print("Done")
