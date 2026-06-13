import os
import re

stories_dir = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\docs\stories"
inbox_dir = os.path.join(stories_dir, "_inbox")
index_file = os.path.join(stories_dir, "INDEX.md")

print("--- AUDITING STORY FILES ---")

# 1. Read INDEX.md and extract all indexed US IDs
indexed_ids = set()
with open(index_file, "r", encoding="utf-8") as f:
    content = f.read()
    # Find patterns like US-XXX in INDEX.md
    matches = re.findall(r"US-\d+", content)
    indexed_ids.update(matches)

print(f"Total US IDs found in INDEX.md: {len(indexed_ids)}")
print(f"Indexed IDs: {sorted(list(indexed_ids))}\n")

# 2. Scan docs/stories and docs/stories/_inbox
def scan_directory(directory, label):
    files = []
    for f in os.listdir(directory):
        if f.endswith(".md") and f != "INDEX.md":
            path = os.path.join(directory, f)
            # Read frontmatter ID
            us_id = None
            status = None
            with open(path, "r", encoding="utf-8") as file:
                lines = file.readlines()
                in_frontmatter = False
                for line in lines:
                    if line.strip() == "---":
                        if not in_frontmatter:
                            in_frontmatter = True
                        else:
                            break
                    elif in_frontmatter:
                        id_match = re.match(r"^id:\s*(US-\d+.*)", line.strip())
                        if id_match:
                            us_id = id_match.group(1).strip()
                        status_match = re.match(r"^status:\s*(\w+)", line.strip())
                        if status_match:
                            status = status_match.group(1).strip()
            files.append({
                "name": f,
                "path": path,
                "id": us_id,
                "status": status,
                "location": label
            })
    return files

stories_files = scan_directory(stories_dir, "outside_inbox")
inbox_files = scan_directory(inbox_dir, "inside_inbox")
all_files = stories_files + inbox_files

print(f"Found {len(stories_files)} files directly in docs/stories")
print(f"Found {len(inbox_files)} files in docs/stories/_inbox")
print(f"Total story files found: {len(all_files)}\n")

# 3. Check for files outside _inbox
outside = [f for f in all_files if f["location"] == "outside_inbox"]
if outside:
    print("Files located OUTSIDE _inbox:")
    for f in outside:
        print(f" - {f['name']} (ID: {f['id']}, Status: {f['status']})")
else:
    print("No files outside _inbox.")
print("")

# 4. Check for duplicate IDs
id_to_files = {}
for f in all_files:
    uid = f["id"]
    if uid:
        if uid not in id_to_files:
            id_to_files[uid] = []
        id_to_files[uid].append(f)

duplicates = {uid: files for uid, files in id_to_files.items() if len(files) > 1}
if duplicates:
    print("DUPLICATE US IDs FOUND:")
    for uid, files in duplicates.items():
        print(f" ID: {uid}")
        for f in files:
            print(f"  - Path: docs/stories/{'_inbox/' if f['location'] == 'inside_inbox' else ''}{f['name']} (Status: {f['status']})")
else:
    print("No duplicate US IDs found.")
print("")

# 5. Check for files not indexed in INDEX.md
not_indexed = []
for f in all_files:
    if f["id"] not in indexed_ids:
        not_indexed.append(f)

if not_indexed:
    print("FILES NOT INDEXED IN INDEX.md:")
    for f in not_indexed:
        print(f" - {f['name']} (ID: {f['id']}, Status: {f['status']}, Location: {f['location']})")
else:
    print("All files are indexed in INDEX.md.")
print("")
