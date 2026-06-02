import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

stories_dir = "docs/stories/_inbox"

print("STORIES WITH STATUS BACKLOG OR DRAFT:")
print("=" * 60)

found = False
for fn in os.listdir(stories_dir):
    if fn.endswith(".md"):
        path = os.path.join(stories_dir, fn)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        lines = content.split("\n")
        status = ""
        size = "unknown"
        for line in lines[:10]:
            if line.startswith("status:"):
                status = line.split(":")[1].strip()
            elif line.startswith("size:"):
                size = line.split(":")[1].strip()
                
        if status in ["backlog", "draft"]:
            found = True
            title = ""
            for line in lines:
                if line.startswith("# US-"):
                    title = line.replace("#", "").strip()
                    break
            
            # Extract User Story text
            us_lines = []
            capture = False
            for line in lines:
                if "## User story" in line or "## User Story" in line:
                    capture = True
                    continue
                if capture:
                    if line.startswith("##") or line.startswith("---"):
                        break
                    if line.strip():
                        us_lines.append(line.strip())
            
            print(f"ID: {fn.split('_')[0]} | Status: {status} | Size: {size}")
            print(f"Title: {title}")
            print("User Story:")
            for ul in us_lines[:3]:
                print(f"  {ul}")
            print("-" * 60)

if not found:
    print("No user stories currently in backlog or draft status.")
