import os

project_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
search_terms = ["data.thienkhoi.com", "proptech.thienkhoi.com", "TK-", "Detail"]
occurrences = []

for root, dirs, files in os.walk(project_dir):
    # Skip build, dist, git, pycache, scratch folders
    if any(p in root for p in [".git", "__pycache__", "build", "dist", "dist (1)", "scratch", "Thien Khoi Group - Nguon Hang - Chi Tiet New_files"]):
        continue
    for f in files:
        if f.endswith(('.py', '.html', '.js', '.json', '.gs', '.md')):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8') as file:
                    content = file.read()
                for term in search_terms:
                    if term in content:
                        occurrences.append((fp, term))
            except Exception:
                pass

print("Found occurrences:")
for fp, term in occurrences:
    print(f"- {os.path.basename(fp)} contains '{term}' in {fp}")
