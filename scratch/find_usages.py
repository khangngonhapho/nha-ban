import sys
# Set console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\api\\index.js", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if "DEFAULT_SYSTEM_PROMPT" in line:
            print(f"api/index.js:{idx}: {line.strip()}")

with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\manager.py", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if "openai_system_prompt" in line:
            print(f"manager.py:{idx}: {line.strip()}")
