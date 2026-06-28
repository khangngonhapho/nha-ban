import os

root_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
keywords = ["curator_html_data"]

for dirpath, dirnames, filenames in os.walk(root_dir):
    if any(p in dirpath for p in [".git", "__pycache__", "build", "dist", "Backup DB", "temp", "Thien Khoi Group"]):
        continue
    for filename in filenames:
        if filename.endswith(".py"):
            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                continue
            if any(kw in content for kw in keywords):
                print(f"Found in {os.path.relpath(filepath, root_dir)}")
