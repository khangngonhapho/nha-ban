import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

folder = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New_files"

if not os.path.exists(folder):
    print("Folder does not exist")
    sys.exit(1)

# Let's search for endpoints patterns, e.g. /product/v1/...
# or any paths called in fetch/axios
# We can find all string literals in JS that look like URLs or paths
pattern = re.compile(r'["\']/[a-zA-Z0-9_\-\/]+["\']')

print("=== Scanning JS Files for URL Paths ===")
for f in os.listdir(folder):
    if f.endswith((".js", "tải xuống")) and "places" not in f and "map" not in f and "util" not in f:
        fpath = os.path.join(folder, f)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_in:
                content = file_in.read()
            
            # Find all path literals
            paths = pattern.findall(content)
            interesting = []
            for p in paths:
                p_clean = p.strip('"\'')
                # If path contains property, owner, phone, warehouse, sources, client, v1, auth, legal
                if any(term in p_clean.lower() for term in ["property", "owner", "phone", "warehouse", "sources", "v1", "auth", "legal", "contact"]):
                    interesting.append(p_clean)
                    
            if interesting:
                print(f"\n[📄 File] {f} (matched {len(interesting)} paths)")
                for p in list(set(interesting))[:15]:
                    print(f"  - {p}")
        except Exception as e:
            print(f"Error reading {f}: {e}")
