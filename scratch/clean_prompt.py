import re

path = "d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\system_prompt.txt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the start keyword (case-insensitive)
start_keyword = "Bạn hãy đóng vai là"
idx = content.lower().find(start_keyword.lower())

if idx != -1:
    clean_content = content[idx:].strip()
    with open(path, "w", encoding="utf-8") as f:
        f.write(clean_content)
    print("Prompt cleaned successfully!")
    print(f"Cleaned content length: {len(clean_content)}")
    print("Start of cleaned content:")
    print(clean_content[:150])
else:
    print("Could not find start keyword!")
