import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open("curator.html", "r", encoding="utf-8") as f:
    content = f.read()

# Let's find some key search strings
keywords = [
    "loadListings", "listingsList", "search", "filter", "checkbox", "status", "select"
]

print("--- Keyword searches in curator.html ---")
for kw in keywords:
    matches = [m.start() for m in re.finditer(re.escape(kw), content)]
    print(f"Keyword '{kw}': {len(matches)} matches")

# Find where listings are loaded or rendered in JavaScript
match = re.search(r"function\s+loadListings", content)
if match:
    idx = match.start()
    print("\n--- loadListings Function Body ---")
    print(content[idx:idx+1500])
else:
    # Try arrow function or general render
    match_arrow = re.search(r"loadListings\s*=\s*", content)
    if match_arrow:
        idx = match_arrow.start()
        print("\n--- loadListings Arrow Function Context ---")
        print(content[idx:idx+1500])
