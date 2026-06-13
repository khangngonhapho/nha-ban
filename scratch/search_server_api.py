import re

with open("curator_server.py", "r", encoding="utf-8") as f:
    content = f.read()

# Search for @app.route
matches = re.finditer(r"@app\.route\((.*?)\)", content)
results = []
for m in matches:
    start_pos = m.start()
    line_no = content.count("\n", 0, start_pos) + 1
    # Get the route definition and the function definition below it
    context = content[start_pos:start_pos+300]
    func_match = re.search(r"def\s+\w+\(.*?\):", context)
    func_str = func_match.group(0) if func_match else ""
    results.append(f"Line {line_no}: {m.group(0)} -> {func_str}")

with open("scratch/server_routes.txt", "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(results))
print(f"Found {len(results)} routes.")
