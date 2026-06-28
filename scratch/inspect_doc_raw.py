import sys

sys.stdout.reconfigure(encoding='utf-8')

path = "d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\system_prompt.txt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

print(f"Content length: {len(content)}")
print("Does it contain 'Bạn hãy đóng vai là'? ", "Bạn hãy đóng vai là" in content)
print("Index of 'Bạn hãy đóng vai là':", content.find("Bạn hãy đóng vai là"))
print("First 500 characters of file:")
print(repr(content[:500]))
