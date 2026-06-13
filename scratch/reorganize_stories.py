import os
import shutil
import re

root_dir = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo"
stories_dir = os.path.join(root_dir, "docs", "stories")
inbox_dir = os.path.join(stories_dir, "_inbox")
index_path = os.path.join(stories_dir, "INDEX.md")

print("--- STARTING STORIES REORGANIZATION ---")

# Step 1: Handle duplicate US-051
src_us51_path = os.path.join(stories_dir, "US-051_curator_editor_status_combobox.md")
dst_us51_path = os.path.join(inbox_dir, "US-051_curator_editor_status_combobox.md")

if os.path.exists(src_us51_path):
    print("Found US-051 outside _inbox (accepted). Overwriting the backlog one inside _inbox.")
    shutil.copy2(src_us51_path, dst_us51_path)
    os.remove(src_us51_path)
    print("US-051 successfully moved and resolved.")

# Step 2: Move other files from stories/ to stories/_inbox/
for filename in os.listdir(stories_dir):
    src_path = os.path.join(stories_dir, filename)
    if os.path.isfile(src_path) and filename.endswith(".md") and filename != "INDEX.md":
        dst_path = os.path.join(inbox_dir, filename)
        print(f"Moving {filename} -> _inbox/")
        shutil.move(src_path, dst_path)

# Step 3: Handle duplicate US-067 inside _inbox
old_us67_overwrite_path = os.path.join(inbox_dir, "US-067_fix_curation_overwrite.md")
new_us72_path = os.path.join(inbox_dir, "US-072_fix_curation_overwrite.md")

if os.path.exists(old_us67_overwrite_path):
    print("Renaming US-067_fix_curation_overwrite.md to US-072_fix_curation_overwrite.md")
    # Read the file content and change the ID inside the frontmatter
    with open(old_us67_overwrite_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace frontmatter id
    new_content = content.replace("id: US-067", "id: US-072")
    
    # Save to the new filename
    with open(new_us72_path, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    # Delete old file
    os.remove(old_us67_overwrite_path)
    print("US-067_fix_curation_overwrite.md successfully renamed to US-072 with id: US-072.")

# Step 4: Update INDEX.md
if os.path.exists(index_path):
    print("Updating docs/stories/INDEX.md...")
    with open(index_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 1. Update stats (Total: 71 -> 72, accepted: 46 -> 47)
        if line.startswith("- Total:"):
            total_match = re.search(r"\d+", line)
            if total_match:
                total_val = int(total_match.group())
                line = f"- Total: {total_val + 1}\n"
                print(f"Updated Stats: Total -> {total_val + 1}")
        elif line.startswith("- accepted:"):
            acc_match = re.search(r"\d+", line)
            if acc_match:
                acc_val = int(acc_match.group())
                line = f"- accepted: {acc_val + 1}\n"
                print(f"Updated Stats: accepted -> {acc_val + 1}")
                
        new_lines.append(line)
        
        # 2. Insert US-072 row in All Stories table
        if "| US-071 |" in line:
            us72_row = "| US-072 | Khắc phục lỗi xuất bản Curation ghi đè thiếu trường & lệch cột Google Sheets | accepted | S | 2026-06-03 | `curator_server.py` |\n"
            new_lines.append(us72_row)
            print("Inserted US-072 row in All Stories table.")
            
        # 3. Insert US-072 in By Keyword (Crawl / Sync Tracking)
        if "### Crawl / Sync Tracking" in line:
            new_lines.append(lines[i+1])  # Append the blank line or whatever next line
            us72_keyword = "- [[US-072_fix_curation_overwrite|US-072]]: Khắc phục lỗi xuất bản Curation ghi đè thiếu trường & lệch cột Google Sheets (accepted)\n"
            new_lines.append(us72_keyword)
            print("Inserted US-072 under Crawl / Sync Tracking keyword section.")
            i += 1  # Skip the next line as we manually added it
            
        i += 1
        
    with open(index_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("INDEX.md successfully updated.")

print("--- STORIES REORGANIZATION COMPLETE ---")
