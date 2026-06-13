import os

project_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
json_files = []

for root, dirs, files in os.walk(project_dir):
    for f in files:
        if f.endswith('.json') and not "package" in f and not "tsconfig" in f and not ".git" in root:
            json_files.append(os.path.join(root, f))

print("Found JSON files:")
for jf in json_files:
    print(f"- {jf} ({os.path.getsize(jf)} bytes)")
