import sys

sys.stdout.reconfigure(encoding='utf-8')

js_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_helpers.js"

with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, start=1):
    if "TK" in line:
        print(f"Line {idx}: {line.strip()[:120]}")
