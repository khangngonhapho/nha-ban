# -*- coding: utf-8 -*-
import sys
from bs4 import BeautifulSoup
import os
import sys
sys.path.insert(0, os.getcwd())
from pool_lego import remove_accents

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    html_file = "Thien Khoi Group - Nguon Hang - Chi Tiet New.html"
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    
    print("Searching for section headings (unaccented)...")
    keywords = ["tieu chi", "tiem nang", "tien ich", "kinh doanh", "mat thoang", "thoang", "vi tri", "duong truoc"]
    
    # Let's search all tags that contain text
    for tag in soup.find_all(True):
        # We only want elements that have text directly (no child elements, or text is short)
        if tag.string or (len(tag.find_all()) == 0 and tag.text):
            text = tag.text.strip()
            text_no_accent = remove_accents(text).lower()
            if any(kw in text_no_accent for kw in keywords):
                print(f"Tag: <{tag.name}> class={tag.get('class')}: {text}")
                # print parent chain
                parent = tag.parent
                print(f"  Parent: <{parent.name}> class={parent.get('class')}")
                if parent.parent:
                    print(f"    G-parent: <{parent.parent.name}> class={parent.parent.get('class')}")
                    print(f"    G-parent snippet: {str(parent.parent)[:300]}")
                print("-" * 50)

if __name__ == "__main__":
    main()
