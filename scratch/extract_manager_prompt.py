import sys

sys.path.append("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo")
try:
    import manager
    manager_prompt = manager.DEFAULT_CONFIG["openai_system_prompt"].strip()
    with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\system_prompt.txt", "w", encoding="utf-8") as out:
        out.write(manager_prompt)
    print("Successfully extracted complete manager prompt to system_prompt.txt")
except Exception as e:
    print(f"Error: {e}")
