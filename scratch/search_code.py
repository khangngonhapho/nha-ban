import os
import glob

search_terms = ["cv(r.c"]
js_dir = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\static\js"

for term in search_terms:
    print(f"=== Searching for '{term}' ===")
    for root, dirs, files in os.walk(js_dir):
        if any(d in root for d in [".git", "__pycache__", "dist", "build", "Backup DB", "dist (1)"]):
            continue
        for file in files:
            if file.endswith(".js"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for idx, line in enumerate(f, 1):
                            if term in line:
                                clean_line = line.strip().encode('ascii', 'ignore').decode('ascii')
                                rel_path = os.path.relpath(filepath, js_dir)
                                print(f"{rel_path}:{idx}: {clean_line}")
                except Exception:
                    pass
