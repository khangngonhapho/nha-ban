import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open("curator.html", "r", encoding="utf-8") as f:
    content = f.read()

# Let's search for fetch calls
idx = 0
while True:
    idx = content.find("fetch(", idx)
    if idx == -1:
        break
    print(f"\n=================== FETCH CALL AT {idx} ===================")
    start = max(0, idx - 100)
    end = min(len(content), idx + 800)
    print(content[start:end])
    idx += len("fetch(")
