import os

root_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
files_found = []

for dirpath, dirnames, filenames in os.walk(root_dir):
    if any(p in dirpath for p in [".git", "__pycache__", "build", "dist", "Backup DB", "temp", "Thien Khoi Group"]):
        continue
    for filename in filenames:
        if filename.endswith(".txt") or filename.endswith(".md"):
            files_found.append(os.path.relpath(os.path.join(dirpath, filename), root_dir))

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/txt_md_files.txt", "w", encoding="utf-8") as f:
    for file in sorted(files_found):
        f.write(file + "\n")

print("File list written successfully.")
