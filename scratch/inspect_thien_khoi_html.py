import os
import sys
import json
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

fn = "Thien Khoi Group - Nguon Hang - Danh Sach.html"
path = f"d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/{fn}"

if os.path.exists(path):
    print(f"=== File: {fn} ===")
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Search for script with id="__NEXT_DATA__"
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        print("[+] Found __NEXT_DATA__!")
        try:
            js_data = json.loads(next_data.string)
            print(f"Keys in __NEXT_DATA__: {list(js_data.keys())}")
            # Print a snippet of the data structure
            with open("scratch/next_data_keys.json", "w", encoding="utf-8") as out:
                json.dump(js_data, out, indent=2, ensure_ascii=False)
            print("Saved __NEXT_DATA__ structure to scratch/next_data_keys.json")
        except Exception as e:
            print(f"Error parsing __NEXT_DATA__: {e}")
    else:
        print("[-] __NEXT_DATA__ script tag not found.")
        
    # 2. Search for other script tags with json data (e.g. self.__next_f.push)
    next_f_scripts = [s for s in soup.find_all('script') if s.string and 'self.__next_f.push' in s.string]
    print(f"[i] Found {len(next_f_scripts)} scripts with self.__next_f.push")
    
    # Let's search if there's any listing data in text
    # (e.g. a list of street names, house details, etc.)
    # Let's find some typical numbers/texts that might be in a listing
    text_content = soup.get_text()
    print(f"Text content length: {len(text_content)}")
    
    # Let's inspect some of the self.__next_f.push scripts
    if next_f_scripts:
        print("Writing a sample of self.__next_f.push scripts to scratch/next_f_sample.txt")
        with open("scratch/next_f_sample.txt", "w", encoding="utf-8") as out:
            for idx, s in enumerate(next_f_scripts[:5]):
                out.write(f"--- Script {idx} ---\n")
                out.write(s.string[:1000] + "...\n\n")
else:
    print(f"File {fn} does not exist.")
