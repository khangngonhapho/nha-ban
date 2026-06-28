with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\manager.py", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if "openai_system_prompt" in line:
            print(f"{idx}: {line.strip()}")
