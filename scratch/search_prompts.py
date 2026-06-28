import os

search_dir = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo"
keywords = ["openai_system_prompt", "DEFAULT_SYSTEM_PROMPT", "fetch_google_doc_content"]

for root, dirs, files in os.walk(search_dir):
    if any(p in root for p in [".git", "node_modules", "dist", "build", "Backup DB", "__pycache__"]):
        continue
    for file in files:
        if file.endswith((".py", ".js", ".gs", ".json", ".html")):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                for kw in keywords:
                    if kw in content:
                        print(f"Found '{kw}' in {os.path.relpath(path, search_dir)}")
            except Exception as e:
                pass
