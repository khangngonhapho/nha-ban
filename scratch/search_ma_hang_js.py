import sys

sys.stdout.reconfigure(encoding='utf-8')

js_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/js/lego_helpers.js"

with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, start=1):
    if "Ma_Hang" in line or "maHang" in line or "mã hàng" in line.lower() or "gen" in line.lower():
        if "function" in line or "const " in line or "let " in line or "=>" in line:
            print(f"Line {idx}: {line.strip()[:120]}")
