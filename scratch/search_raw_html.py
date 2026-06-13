import sys
import re

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    path = r'D:\LHTBrain\01_PROJECTS\BDS-KhangNgo\Thien Khoi Group - Nguon Hang - Chi Tiet New.html'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Let's search for some typical keywords that are in the screenshot, e.g. "Phan Tây Hồ", "mặt thoáng", "Dưới 100m"
    # But wait, let's search for "Phan" or "Hồ" or "Tây"
    for term in ["Phan", "Hồ", "Tây", "Tỷ", "Triệu", "Độ rộng", "mặt thoáng", "Đường trước nhà"]:
        matches = [m.start() for m in re.finditer(term, html, re.I)]
        print(f"Term '{term}': found {len(matches)} matches")
        for idx, pos in enumerate(matches[:3]):
            print(f"  Match {idx}: ... {html[max(0, pos-100):min(len(html), pos+100)]} ...")

if __name__ == '__main__':
    main()
