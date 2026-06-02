import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open("curator.html", "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("function fetchListings")
if idx == -1:
    idx = content.find("fetchListings =")

if idx != -1:
    print("=================== fetchListings Definition ===================")
    print(content[idx:idx+2000])
else:
    print("Could not find fetchListings definition")
