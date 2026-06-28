with open("static/js/lego_core.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "POOL_HEADERS" in line:
        print(f"Line {idx+1}: {line.strip()}")
