with open("index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

results = []
for i, line in enumerate(lines):
    if "function edit" in line or "editListing" in line or "openEdit" in line or "showEdit" in line:
        results.append(f"Line {i+1}: {line.strip()}")

# Write results
with open("scratch/edit_logic_search.txt", "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(results))
print("Done")
