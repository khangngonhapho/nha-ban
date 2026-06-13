# -*- coding: utf-8 -*-
import sys
import re

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    with open("Thien Khoi Group - Nguon Hang - Chi Tiet New.html", "r", encoding="utf-8") as f:
        html = f.read()

    print(f"File size: {len(html)} bytes")
    
    keywords = ["chính chủ", "hiếm", "thang máy", "ngõ thông", "đông nam", "đông bắc", "mặt phố", "sổ hồng", "sổ đỏ"]
    for kw in keywords:
        matches = [m.start() for m in re.finditer(kw, html, re.IGNORECASE)]
        print(f"Keyword '{kw}': found {len(matches)} times. Context around first match:")
        for idx in matches[:1]:
            start = max(0, idx - 100)
            end = min(len(html), idx + 200)
            print(html[start:end])
            print("="*60)

if __name__ == "__main__":
    main()
