import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/curator_server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== Scanning curator_server.py for tk_id ===")
for idx, line in enumerate(lines):
    if "tk_id" in line:
        print(f"Line {idx+1}: {line.strip()}")
