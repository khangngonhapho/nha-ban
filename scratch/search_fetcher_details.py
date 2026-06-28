import sys

sys.stdout.reconfigure(encoding='utf-8')

fetcher_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/fetcher.py"

with open(fetcher_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== Functions in fetcher.py ===")
for idx, line in enumerate(lines, start=1):
    if "def " in line:
        print(f"Line {idx}: {line.strip()}")
