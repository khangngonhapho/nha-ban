import os
import re

path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New.html"

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Look for warehouse/sources/<UUID>
matches = re.findall(r'warehouse/sources/([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})', html)
print(f"Matched detail URLs: {list(set(matches))}")
