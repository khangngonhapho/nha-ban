with open("curator_server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

results = []
for i, line in enumerate(lines):
    if "def get_google_credentials" in line or "get_google_credentials(" in line:
        results.append(f"Line {i+1}: {line.strip()}")

# Print definition block of get_google_credentials if found
found_def_line = -1
for i, line in enumerate(lines):
    if "def get_google_credentials" in line:
        found_def_line = i
        break

if found_def_line != -1:
    results.append("\n=== Definition Block ===")
    for j in range(found_def_line, min(found_def_line + 40, len(lines))):
        results.append(f"Line {j+1}: {lines[j].rstrip()}")

with open("scratch/server_creds_search.txt", "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(results))
print("Done")
