# -*- coding: utf-8 -*-
import sys

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    with open("manager.py", "r", encoding="utf-8") as f:
        manager = f.read()

    lines = manager.split("\n")
    print("Found mentions of automation error:")
    for idx, line in enumerate(lines):
        if "Curation & Xuất bản" in line or "near \",\"" in line or "tự động hóa Curation" in line:
            print(f"Line {idx+1}: {line.strip()}")

if __name__ == "__main__":
    main()
