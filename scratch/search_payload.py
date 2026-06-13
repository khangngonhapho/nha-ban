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

    # Let's search for "street", "district", "ward", or any uppercase Vietnamese names
    # Let's search for keys and values using a regex
    terms = ["address", "street", "district", "ward", "province", "code", "offeringPrice"]
    for t in terms:
        matches = [m.start() for m in re.finditer(t, text, re.I)]
        print(f"Term '{t}': found {len(matches)} matches")
        for idx, pos in enumerate(matches[:3]):
            print(f"  Match {idx}: ... {text[max(0, pos-100):min(len(text), pos+100)]} ...")

if __name__ == '__main__':
    main()
