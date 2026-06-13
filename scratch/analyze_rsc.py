import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

for fn in ["probe__warehouse__rsc_1.txt", "probe__warehouse_sources__rsc_1.txt"]:
    path = f"d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/{fn}"
    if os.path.exists(path):
        print(f"=== File: {fn} ===")
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        print(f"Length: {len(content)}")
        
        # Decode Unicode escape sequences
        decoded = content
        try:
            decoded = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), decoded)
        except Exception:
            pass
            
        print("First 1000 characters (decoded):")
        print(decoded[:1000])
        print("\nSearching for 'phạm' or 'trần' or 'tỷ' or 'triệu' in decoded:")
        matches = []
        for kw in ["trần", "phạm", "đường", "tỷ", "triệu", "nhà", "quận"]:
            if kw in decoded.lower():
                matches.append(kw)
        print(f"Matches found: {matches}")
        print("-" * 50)
else:
    print("Files check complete")
