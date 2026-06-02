import os
import sys

# Configure stdout to use utf-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

stories_dir = "docs/stories/_inbox"
keywords = ["google sheet", "sheet", "xuất bản", "publish", "pool", "đồng bộ", "credentials"]

print("SEARCH RESULTS FOR GOOGLE SHEETS / PUBLISHING STORIES:")
print("=" * 60)

for fn in os.listdir(stories_dir):
    if fn.endswith(".md"):
        path = os.path.join(stories_dir, fn)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check if content contains any of the keywords
        found_kws = [kw for kw in keywords if kw.lower() in content.lower()]
        if found_kws:
            # Extract ID and Title
            lines = content.split("\n")
            title = ""
            for line in lines:
                if line.startswith("# US-"):
                    title = line.strip("#").strip()
                    break
            
            # Print story details
            print(f"File: {fn}")
            print(f"Title: {title}")
            print(f"Matched Keywords: {found_kws}")
            # Print brief summary (first 5 lines after frontmatter)
            body_lines = [l for l in lines if l.strip() and not l.startswith("---")][:5]
            print("Summary Snippet:")
            for bl in body_lines:
                if not bl.startswith("id:") and not bl.startswith("status:") and not bl.startswith("date:") and not bl.startswith("size:"):
                    print(f"  {bl[:120]}")
            print("-" * 60)
