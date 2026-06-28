import re

with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\api\\index.js", "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'const DEFAULT_SYSTEM_PROMPT = `([\s\S]+?)`;', content)
if match:
    prompt = match.group(1).strip()
    with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\system_prompt.txt", "w", encoding="utf-8") as out:
        out.write(prompt)
    print("Successfully extracted prompt to system_prompt.txt")
else:
    print("Failed to extract prompt!")
