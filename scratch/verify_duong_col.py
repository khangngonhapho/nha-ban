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
    print("Mentions of duong_col or hardcoded Duong column queries in manager.py:")
    for idx, line in enumerate(lines):
        if "duong_col" in line or "listings_v2.Duong" in line:
            print(f"Line {idx+1}: {line.strip()}")

if __name__ == "__main__":
    main()
