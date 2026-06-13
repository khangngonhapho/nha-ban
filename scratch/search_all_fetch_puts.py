import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find fetch blocks
matches = re.finditer(r"fetch\((.*?)\)", content, re.DOTALL)
results = []
for m in matches:
    start_pos = m.start()
    # Find line number
    line_no = content.count("\n", 0, start_pos) + 1
    # Check if there is method: 'PUT' or method: 'POST' or method: 'DELETE' nearby in the next 200 chars
    near_text = content[start_pos:start_pos+300]
    if "method" in near_text:
        results.append(f"Line {line_no}: {m.group(0).strip()} | Context: {near_text[:120].strip()}")

with open("scratch/all_fetch_writes.txt", "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(results))
print(f"Found {len(results)} matches.")
