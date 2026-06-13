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
    
    # Print all text that might look like criteria or badges
    # Let's search for some known criteria words like "Đường trước nhà", "Hướng nhà", "Pháp lý", "Hẻm", "Mặt tiền", etc.
    keywords = ["ngõ", "đường trước nhà", "hẻm", "thang máy", "hướng", "lô góc", "thoáng", "chính chủ", "hiếm", "pháp lý", "sổ đỏ", "sổ hồng", "kinh doanh", "dòng tiền"]
    for tag in soup.find_all(['span', 'div', 'p', 'button', 'label']):
        text = tag.text.strip()
        if len(text) > 0 and len(text) < 150:
            text_lower = text.lower()
            if any(kw in text_lower for kw in keywords):
                # Print tag name, attributes, and text
                print(f"<{tag.name} class={tag.get('class')}> text: {text}")

if __name__ == "__main__":
    main()
