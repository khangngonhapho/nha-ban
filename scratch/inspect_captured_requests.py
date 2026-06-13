import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/captured_requests.json"
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        reqs = json.load(f)
        
    print(f"Total captured requests: {len(reqs)}")
    print("\n=== All Captured Requests ===")
    for idx, r in enumerate(reqs):
        url = r.get("url", "")
        method = r.get("method", "")
        # Filter out webpack, css, static chunks to focus on data fetches
        if "_next/static" in url or "rum?" in url:
            continue
        print(f"[{idx+1}] {method} {url}")
        if r.get("post_data"):
            print(f"    Post Data: {r.get('post_data')[:300]}")
        headers = r.get("headers", {})
        # Print custom headers like Next-Action or RSC or Authorization
        interesting_headers = {k: v for k, v in headers.items() if k.lower() in ["next-action", "rsc", "accept", "content-type"]}
        if interesting_headers:
            print(f"    Headers: {interesting_headers}")
        print("-" * 50)
else:
    print("File not found")
