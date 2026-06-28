import os

search_dir = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo"

for root, dirs, files in os.walk(search_dir):
    if any(p in root for p in [".git", "node_modules", "dist", "build", "Backup DB", "__pycache__"]):
        continue
    for file in files:
        if file.endswith(".gs"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                for idx, line in enumerate(lines, 1):
                    if any(w in line.lower() for w in ["gpt-", "openai", "system", "payload"]):
                        if len(line.strip()) > 0:
                            print(f"{file}:{idx}: {line.strip()[:100]}")
            except Exception as e:
                pass
