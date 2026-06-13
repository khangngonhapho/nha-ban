import os
import re

index_path = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\docs\stories\INDEX.md"

with open(index_path, "r", encoding="utf-8") as f:
    content = f.read()

# Separate content into sections
parts = content.split("\n")

in_table = False
table_headers = []
table_rows = []
other_before = []
other_after = []

for line in parts:
    if line.strip().startswith("| ID") or (in_table and line.strip().startswith("|")):
        in_table = True
        if line.strip().startswith("| ID") or line.strip().startswith("| ---"):
            table_headers.append(line)
        else:
            table_rows.append(line)
    else:
        if in_table:
            # We reached the end of the table
            in_table = False
            other_after.append(line)
        else:
            if not other_after:
                other_before.append(line)
            else:
                other_after.append(line)

# Sort table rows by US ID descending
def get_us_id(row_str):
    match = re.search(r"US-(\d+)", row_str)
    if match:
        return int(match.group(1))
    return 0

table_rows.sort(key=get_us_id, reverse=True)

# Combine everything back
new_content = "\n".join(other_before + table_headers + table_rows + other_after)

with open(index_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("INDEX.md table sorted successfully by ID descending.")
