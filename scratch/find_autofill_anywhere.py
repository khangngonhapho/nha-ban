import os

keywords = ["autoFillCurationDetails"]
root_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"

out = []
for dirpath, dirnames, filenames in os.walk(root_dir):
    # Skip some folders like .git, __pycache__, build, dist
    if any(p in dirpath for p in [".git", "__pycache__", "build", "dist", "Backup DB", "temp", "Thien Khoi Group"]):
        continue
    for filename in filenames:
        if not (filename.endswith(".js") or filename.endswith(".html") or filename.endswith(".py") or filename.endswith(".gs")):
            continue
        filepath = os.path.join(dirpath, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            continue
        
        if any(kw in content for kw in keywords):
            lines = content.splitlines()
            out.append(f"\n=== Found in {os.path.relpath(filepath, root_dir)} ===\n")
            for idx, line in enumerate(lines):
                if any(kw in line for kw in keywords):
                    out.append(f"Line {idx+1}: {line.strip()}\n")
                    # print 15 lines before and after if it seems to be the function definition
                    if "function" in line or "=>" in line or "window." in line or ":" in line:
                        start = max(0, idx - 5)
                        end = min(len(lines), idx + 80)
                        out.append(f"--- Code block ---\n")
                        for j in range(start, end):
                            out.append(f"  {j+1}: {lines[j]}\n")
                        out.append(f"-----------------\n")

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/search_results_auto_fill.txt", "w", encoding="utf-8") as out_f:
    out_f.writelines(out)

print("Search completed. Output written to scratch/search_results_auto_fill.txt")
