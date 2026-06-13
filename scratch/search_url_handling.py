# -*- coding: utf-8 -*-
import sys
import re

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    print("=== Searching curator.html for URL parsing or paste event ===")
    with open("curator.html", "r", encoding="utf-8") as f:
        curator = f.read()

    # Search for regexes or keywords matching thienkhoi links
    for match in re.finditer(r'(thienkhoi|sources|Detail|Detail_|\.com/Hang)', curator, re.I):
        start = max(0, match.start() - 100)
        end = min(len(curator), match.end() + 200)
        print(f"Match: {match.group()}")
        print(curator[start:end])
        print("-" * 50)

    print("\n=== Searching manager.py for URL parsing or endpoints ===")
    with open("manager.py", "r", encoding="utf-8") as f:
        manager = f.read()
    
    # Search for Detail or sources or warehouse in manager.py
    for match in re.finditer(r'(Detail|sources|warehouse|recrawl|api/listings)', manager, re.I):
        start = max(0, match.start() - 100)
        end = min(len(manager), match.end() + 200)
        print(f"Match: {match.group()}")
        print(manager[start:end])
        print("-" * 50)

if __name__ == "__main__":
    main()
