with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\curator.html", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if "openai_system_prompt" in line:
            print(f"curator.html:{idx}: {line.strip()}")
