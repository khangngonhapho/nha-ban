import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def search_in_file(filepath, kw_list):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"\n=== Search Results in {filepath} ===")
    for kw in kw_list:
        matches = [m.start() for m in re.finditer(re.escape(kw), content)]
        print(f"Keyword '{kw}': {len(matches)} matches")
        # If there are matches, let's print the first match context
        if matches:
            idx = matches[0]
            start = max(0, idx - 100)
            end = min(len(content), idx + 800)
            print(f"--- Context for first match of '{kw}' ---")
            print(content[start:end])

search_in_file("curator_server.py", ["/api/publish", "bulk", "publish_all", "publish_multiple"])
search_in_file("curator.html", ["publish", "bulk", "sync", "Pool"])
