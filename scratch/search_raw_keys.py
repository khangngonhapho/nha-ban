import sys
import re

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    path = r'D:\LHTBrain\01_PROJECTS\BDS-KhangNgo\scratch\decoded_rsc_payload.txt'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Let's search for standard keys
    keys = ["floors", "area", "wide", "depth", "description", "offeringPrice", "minimumRoadWidth", "behindOpenSpace", "sideOpenSpace"]
    for k in keys:
        matches = [m.start() for m in re.finditer(r'"' + k + r'"', text)]
        print(f"Key '{k}': found {len(matches)} matches")
        for idx, pos in enumerate(matches[:3]):
            print(f"  Match {idx}: ... {text[max(0, pos-50):min(len(text), pos+150)]} ...")

if __name__ == '__main__':
    main()
