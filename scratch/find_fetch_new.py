with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\manager.py", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f, 1):
        if "def fetch_google_doc_content" in line:
            print(f"new line index: {idx}")
