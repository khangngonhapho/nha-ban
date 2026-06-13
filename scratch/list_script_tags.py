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

    # Let's find all script tags
    script_tags = re.findall(r'<script\b[^>]*>', html, re.I)
    print(f"Found {len(script_tags)} script tags:")
    for tag in script_tags:
        print("  ", tag)

if __name__ == '__main__':
    main()
