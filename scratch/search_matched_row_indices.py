import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Search for patterns like row[71], matchedRow[72], etc.
patterns = [
    r"\bpr\[\d+\]",
    r"\brow\[\d+\]",
    r"\bmatchedRow\[\d+\]",
    r"\bp\.pool_row_data\[\d+\]",
    r"\bsr\[\d+\]"
]

results = []
for p in patterns:
    matches = re.finditer(p, content)
    for m in matches:
        start_pos = m.start()
        line_no = content.count("\n", 0, start_pos) + 1
        text = m.group(0)
        # Extract number
        idx = int(re.search(r"\d+", text).group(0))
        if 70 <= idx <= 80:
            # Print surrounding line context
            line_content = content.splitlines()[line_no - 1].strip()
            results.append(f"Line {line_no}: {line_content}")

with open("scratch/matched_row_indices.txt", "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(results))
print(f"Found {len(results)} matches.")
