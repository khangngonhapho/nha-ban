import sys
import re
import json

def decode_next_f_payloads(html):
    payloads = []
    # Find all self.__next_f.push([1, "..."]) or push([1, "..."])
    # Next.js format: self.__next_f.push([1,"payload_text"])
    for match in re.finditer(r'self\.__next_f\.push\(\[\s*\d+\s*,\s*\"(.*?)\"\s*\]\)', html, re.S):
        payload_part = match.group(1)
        # Unescape quotes and newlines
        payload_part = payload_part.replace('\\"', '"').replace('\\n', '\n').replace('\\/', '/')
        # Decode unicode escapes like \u1ea1
        try:
            payload_part = payload_part.encode('utf-8').decode('unicode_escape')
        except Exception:
            pass
        payloads.append(payload_part)
    return "".join(payloads)

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    path = r'D:\LHTBrain\01_PROJECTS\BDS-KhangNgo\Thien Khoi Group - Nguon Hang - Chi Tiet New.html'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    full_payload = decode_next_f_payloads(html)
    print("Full decoded RSC payload length:", len(full_payload))
    
    # Save the decoded payload to a scratch file so we can view it
    with open('D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/decoded_rsc_payload.txt', 'w', encoding='utf-8') as out:
        out.write(full_payload)
        
    print("Saved decoded RSC payload to scratch/decoded_rsc_payload.txt")
    
    # Search for behindOpenSpace, minimumRoadWidth, or open spaces
    for term in ["behindOpenSpace", "sideOpenSpace", "minimumRoadWidth", "mặt thoáng", "mạt thoang", "độ rộng mặt thoáng"]:
        matches = [m.start() for m in re.finditer(term, full_payload, re.I)]
        print(f"Search for '{term}': found {len(matches)} matches")
        for idx, pos in enumerate(matches[:3]):
            print(f"  Match {idx}: ... {full_payload[max(0, pos-150):min(len(full_payload), pos+150)]} ...")

if __name__ == '__main__':
    main()
