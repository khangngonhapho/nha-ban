import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

file_path = r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\crawl_pipeline.py"

with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

lines = code.split("\n")
print("--- SEARCH FOR 'find_next_sibling' or 'find(\'a\')' ---")
for i, line in enumerate(lines):
    if ".find('a')" in line or "get_val_by_label" in line or "def " in line:
        if i > 0:
            print(f"Line {i+1}: {line.strip()}")
