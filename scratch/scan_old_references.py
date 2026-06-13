import os

project_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
old_names = ["curator_config.json", "crawl_pipeline.py", "curator_server.py"]
occurrences = []

for root, dirs, files in os.walk(project_dir):
    # Skip build, dist, git, pycache folders
    if any(p in root for p in [".git", "__pycache__", "build", "dist", "dist (1)", "Thien Khoi Group - Nguon Hang - Chi Tiet New_files"]):
        continue
    for f in files:
        if f.endswith(('.py', '.html', '.bat', '.json', '.spec', '.iss', '.md', '.txt')):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8') as file:
                    content = file.read()
                for old in old_names:
                    if old in content:
                        occurrences.append((fp, old))
            except Exception:
                pass

print("Found occurrences of old filenames:")
for fp, old in occurrences:
    print(f"- {os.path.basename(fp)} references {old} in {fp}")
