import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\SOURCE_OF_TRUTH.md"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

lines = code.split("\n")
print("--- SEARCH FOR SECTION 7 ---")
for i, line in enumerate(lines):
    if "## 7." in line or "LỊCH SỬ THAY ĐỔI" in line or "## 8." in line:
        print(f"Line {i+1}: {line}")
