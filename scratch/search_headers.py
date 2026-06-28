with open("canvas.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "poolHeaders" in line or "sourceHeaders" in line:
        print(f"Line {idx+1}: {line.strip()}")
