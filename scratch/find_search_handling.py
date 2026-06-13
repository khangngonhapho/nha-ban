# -*- coding: utf-8 -*-
import sys

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    with open("curator.html", "r", encoding="utf-8") as f:
        html = f.read()

    lines = html.split("\n")
    print("Mentions of thienkhoi.com or sidebar-search in JS:")
    for idx, line in enumerate(lines):
        if "thienkhoi.com" in line or "sidebar-search" in line or "query.includes" in line:
            print(f"Line {idx+1}: {line.strip()}")

if __name__ == "__main__":
    main()
