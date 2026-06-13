import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New.html"

with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

pos = html.find("0941151187")
if pos != -1:
    print("=== Found context around 0941151187 ===")
    print(html[max(0, pos-500):min(len(html), pos+500)])
else:
    print("Not found")
