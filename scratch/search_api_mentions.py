import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

fn = "Thien Khoi Group - Nguon Hang - Danh Sach.html"
path = f"d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/{fn}"

if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    print("=== Searching for API occurrences in list page ===")
    matches = re.finditer(r'/api/[a-zA-Z0-9_\-\/]+', html, re.I)
    match_list = list(set(m.group(0) for m in matches))
    print(f"Found {len(match_list)} distinct matches:")
    for m in match_list[:20]:
        print(f"  {m}")
        
    # Let's search for "proptech.thienkhoi.com" to see if there are subdomains or APIs
    matches_domains = re.finditer(r'https?://[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,}', html)
    domain_list = list(set(d.group(0) for d in matches_domains))
    print(f"\nFound {len(domain_list)} domains:")
    for d in domain_list[:20]:
        print(f"  {d}")
else:
    print("File not found")
