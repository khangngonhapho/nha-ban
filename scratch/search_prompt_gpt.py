import os

root_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
keywords = ["system_prompt", "systemPrompt", "openai", "openai_system_prompt", "DEFAULT_CONFIG"]

out = []
for dirpath, dirnames, filenames in os.walk(root_dir):
    if any(p in dirpath for p in [".git", "__pycache__", "build", "dist", "Backup DB", "temp", "Thien Khoi Group"]):
        continue
    for filename in filenames:
        if not (filename.endswith(".py") or filename.endswith(".js") or filename.endswith(".html") or filename.endswith(".gs")):
            continue
        filepath = os.path.join(dirpath, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue
        
        for kw in keywords:
            if kw.lower() in content.lower():
                lines = content.splitlines()
                out.append(f"\n=== Found in {os.path.relpath(filepath, root_dir)} ===\n")
                for idx, line in enumerate(lines):
                    if any(k.lower() in line.lower() for k in keywords):
                        out.append(f"Line {idx+1}: {line.strip()[:180]}\n")
                break

with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/search_prompt_gpt.txt", "w", encoding="utf-8") as f_out:
    f_out.writelines(out)

print("Search completed.")
