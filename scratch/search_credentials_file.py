with open("manager.py", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "CREDENTIALS_FILE" in line:
            print(f"Line {i+1}: {line.strip()}")
