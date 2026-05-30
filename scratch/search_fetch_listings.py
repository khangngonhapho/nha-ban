import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open("curator.html", "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("fetchListings")
if idx != -1:
    print("=================== fetchListings Occurrences ===================")
    start = max(0, idx - 100)
    end = min(len(content), idx + 2000)
    print(content[start:end])
else:
    print("Could not find fetchListings")
