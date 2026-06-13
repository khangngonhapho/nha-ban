# -*- coding: utf-8 -*-
import os
import sys

def main():
    html_file = "Thien Khoi Group - Nguon Hang - Chi Tiet New.html"
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()

    print("Searching raw HTML...")
    keys = ["behindOpenSpace", "sideOpenSpace", "minimumRoadWidth", "restrooms", "bedrooms", "criteria", "homeOwner"]
    for k in keys:
        print(f"Key '{k}': {k in html}")

    # Let's search case-insensitively for 'hẻm' or 'phòng ngủ' inside script tags
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")
    print(f"Total script tags: {len(scripts)}")
    
    # Check if there is a JSON string in any script tag
    for idx, s in enumerate(scripts):
        content = s.string or ""
        if "behindOpenSpace" in content or "criteria" in content:
            print(f"Found match in script {idx} (type={s.get('type')}, class={s.get('class')}):")
            print(content[:500])
            print("...")

if __name__ == "__main__":
    main()
