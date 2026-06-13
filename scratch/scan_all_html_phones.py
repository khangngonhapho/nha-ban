import os
import sys
import re
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

for f in os.listdir("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"):
    if f.endswith(".html"):
        path = os.path.join("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo", f)
        with open(path, 'r', encoding='utf-8', errors='ignore') as file_in:
            content = file_in.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()
        phones = re.findall(r'0\d{9}|0\d{2}\s\d{3}\s\d{4}|0\d{3}\s\d{3}\s\d{3}', text)
        phones_unique = list(set(phones))
        
        if phones_unique:
            print(f"\n[📄 File] {f} contains phone numbers:")
            for p in phones_unique:
                # Find context
                pos = text.find(p)
                context = text[max(0, pos-40):min(len(text), pos+60)].replace('\n', ' ')
                print(f"  - {p}: ... {context} ...")
