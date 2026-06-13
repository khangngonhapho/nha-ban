import os

found = []
for root, dirs, files in os.walk('.'):
    if '.git' in root or '__pycache__' in root or 'dist' in root or 'build' in root:
        continue
    for file in files:
        if file.endswith('.db'):
            path = os.path.join(root, file)
            size = os.path.getsize(path)
            found.append((path, size))

if found:
    print("Found SQLite files:")
    for path, size in found:
        print(f"- {path} ({size} bytes)")
else:
    print("No .db files found in this workspace directory.")
