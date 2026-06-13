# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
import re

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    with open("curator.html", "r", encoding="utf-8") as f:
        html = f.read()

    # Find all input elements in curator.html
    soup = BeautifulSoup(html, "html.parser")
    inputs = soup.find_all("input")
    print("=== All Input Elements in curator.html ===")
    for inp in inputs:
        print(f"<{inp.name} id={inp.get('id')} class={inp.get('class')} placeholder={repr(inp.get('placeholder'))}>")

    # Search the javascript script block inside curator.html for url processing
    # Search for patterns like match(/3d296527/) or match(/sources/) or data.thienkhoi.com
    print("\n=== Javascript mentions of thienkhoi or url parsing ===")
    scripts = soup.find_all("script")
    for idx, s in enumerate(scripts):
        js = s.string or ""
        if not js:
            continue
        # check if it mentions url, link, thienkhoi, sources, or matches
        lines = js.split("\n")
        for line_no, line in enumerate(lines):
            if any(kw in line.lower() for kw in ["thienkhoi", "sources", "hang/detail", "regex", "uuid", "parseurl", "extract"]):
                print(f"Line {line_no}: {line.strip()}")

if __name__ == "__main__":
    main()
