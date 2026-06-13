import os

with open("curator_server.py", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = re.findall(r".*khangngo-admin.*", content)
print("Matches in curator_server.py:")
for m in matches:
    print(m)
