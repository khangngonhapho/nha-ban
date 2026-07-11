import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

path = "scratch/decoded_rsc_sources.txt"
if os.path.exists(path):
    content = open(path, encoding='utf-8').read()
    print("Length:", len(content))
    
    # Extract all text in double quotes to see what labels are there
    strings = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', content)
    # Filter out static chunks, numbers, codes
    filtered_strings = []
    for s in strings:
        s = s.strip()
        if len(s) > 10 and not s.startswith("static/") and not s.endswith(".js") and not s.isdigit():
            filtered_strings.append(s)
            
    print(f"Found {len(filtered_strings)} interesting strings:")
    for idx, s in enumerate(list(set(filtered_strings))[:40]):
        # Print with unicode encoding handled
        try:
            print(f"  [{idx+1}] {repr(s)}")
        except Exception:
            pass
else:
    print("File not found")
