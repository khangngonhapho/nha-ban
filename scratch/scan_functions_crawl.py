with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/crawl_pipeline.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if line.strip().startswith("def "):
        print(f"Line {idx+1}: {line.strip()}")
