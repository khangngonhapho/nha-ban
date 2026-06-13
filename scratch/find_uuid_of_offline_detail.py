import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New.html"

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# UUID pattern: 8-4-4-4-12 chars
uuids = re.findall(r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}', html)
print(f"Total UUIDs found: {len(uuids)}")
print("Unique UUIDs found:")
for u in set(uuids):
    print(f"  - {u}")
