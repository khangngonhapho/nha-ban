import os

paths = [
    "d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\dist\\KhangNgoCurator\\system_prompt.txt",
    "d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\dist\\KhangNgoCurator\\_internal\\system_prompt.txt"
]

for p in paths:
    if os.path.exists(p):
        print(f"FOUND: {p} exists! Size: {os.path.getsize(p)} bytes")
    else:
        print(f"NOT FOUND: {p}")
