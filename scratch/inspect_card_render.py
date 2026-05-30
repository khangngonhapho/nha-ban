import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("curator.html", "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("function fetchListings")
if idx != -1:
    print("=================== Surrounding Context for fetchListings ===================")
    print(content[idx-1000:idx])
else:
    print("Could not find function fetchListings")
