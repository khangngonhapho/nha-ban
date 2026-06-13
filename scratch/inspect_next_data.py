import sys
import json
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

    match = re.search(r'<script\s+id=["\']__NEXT_DATA__["\']\s+type=["\']application/json["\']>(.*?)</script>', html, re.S)
    if match:
        print("Found __NEXT_DATA__ script!")
        try:
            data = json.loads(match.group(1))
            # Let's search inside the dictionary for any keys or print its keys
            print("Keys at root:", list(data.keys()))
            if "props" in data:
                props = data["props"]
                print("Keys in props:", list(props.keys()))
                # We can do a recursive search or pretty print a portion
                pretty = json.dumps(props, ensure_ascii=False, indent=2)
                print("Snippet of props (first 2000 chars):")
                print(pretty[:2000])
        except Exception as ex:
            print(f"JSON parsing error: {ex}")
    else:
        print("__NEXT_DATA__ script not found!")

if __name__ == '__main__':
    main()
