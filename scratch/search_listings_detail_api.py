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
    start_line = -1
    for idx, line in enumerate(lines):
        if "@app.route('/api/listings/<" in line:
            start_line = idx
            break

    if start_line != -1:
        print("Found endpoint starting at line:", start_line + 1)
        for idx in range(start_line, min(len(lines), start_line + 50)):
            print(f"{idx+1}: {lines[idx]}")
    else:
        print("Not found detail endpoint")

if __name__ == "__main__":
    main()
