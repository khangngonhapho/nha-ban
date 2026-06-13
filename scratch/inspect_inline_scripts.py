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

    # Find inline scripts
    inline_scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', html, re.S)
    print(f"Found {len(inline_scripts)} inline scripts:")
    for idx, content in enumerate(inline_scripts):
        # Only print first 200 chars to avoid clutter
        snippet = content.strip().replace('\n', ' ')
        print(f"Script {idx}: length={len(content)}")
        print("  Snippet:", snippet[:300])

if __name__ == '__main__':
    main()
