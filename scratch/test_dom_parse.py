# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup

def main():
    html_file = "Thien Khoi Group - Nguon Hang - Chi Tiet New.html"
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    
    with open("scratch/dom_out.txt", "w", encoding="utf-8") as out:
        for idx, el in enumerate(soup.find_all(text=True)):
            txt = el.strip()
            if txt:
                parent = el.parent
                out.write(f"Line {idx}: [{parent.name}] class={parent.get('class')}: {txt}\n")

if __name__ == "__main__":
    main()
