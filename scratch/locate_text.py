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

    # Find the string "phạm văn hai"
    # Note: earlier we found that it was in the HTML
    matches = [m.start() for m in re.finditer("phạm văn hai", html, re.I)]
    print(f"Found {len(matches)} matches in raw HTML:")
    for idx, pos in enumerate(matches):
        print(f"Match {idx}: ... {html[max(0, pos-150):min(len(html), pos+250)]} ...")

if __name__ == '__main__':
    main()
