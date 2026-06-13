# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
import os

sys.path.insert(0, os.getcwd())
from pool_lego import remove_accents

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    with open("Thien Khoi Group - Nguon Hang - Chi Tiet New.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    
    target = "huong"
    for label in soup.find_all(['label', 'p', 'span', 'div']):
        if label.name == 'div' and len(label.text) > 100:
            continue
        txt = remove_accents(label.text.replace(':', '').strip()).lower()
        if target in txt:
            print(f"Matched tag: <{label.name} class={label.get('class')}> Text: {repr(label.text.strip())}")
            sibling = label.find_next_sibling()
            if sibling:
                print(f"  Direct sibling: <{sibling.name}> Text: {repr(sibling.text.strip())}")
            # print parent chain
            curr = label
            for i in range(3):
                curr = curr.parent
                if curr:
                    print(f"  Parent level {i+1}: <{curr.name} class={curr.get('class')}>")
                    sib = curr.find_next_sibling()
                    if sib:
                        print(f"    Parent level {i+1} sibling: <{sib.name}> Text: {repr(sib.text.strip())}")

if __name__ == "__main__":
    main()
