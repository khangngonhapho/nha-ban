# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    with open("Thien Khoi Group - Nguon Hang - Chi Tiet New.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    
    # search for 'tiêu chí'
    for tag in soup.find_all(True):
        if tag.string and "tiêu chí" in tag.string.lower():
            print(f"Exact tag containing 'tiêu chí': <{tag.name} class={tag.get('class')}> text: {tag.string.strip()}")
            # print siblings and parent contents
            print(f"Parent: <{tag.parent.name} class={tag.parent.get('class')}>")
            for sibling in tag.next_siblings:
                if sibling.name:
                    print(f"Sibling: <{sibling.name} class={sibling.get('class')}> text: {sibling.text.strip()}")
            print("-" * 50)

if __name__ == "__main__":
    main()
