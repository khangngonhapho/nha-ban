import os
import sys
import requests

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

cookie_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/thienkhoi_cookie.txt"

if not os.path.exists(cookie_path):
    print("[❌] Không tìm thấy file cookie!")
    sys.exit(1)

with open(cookie_path, 'r', encoding='utf-8') as f:
    cookie = f.read().strip()

# Next.js App Router RSC headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Cookie": cookie,
    "RSC": "1", # CRITICAL: Tells Next.js to return the React Server Component payload instead of full HTML
    "Accept": "text/x-component",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://proptech.thienkhoi.com/warehouse"
}

# Try different pagination parameters
paging_candidates = [
    "https://proptech.thienkhoi.com/warehouse?page=2",
    "https://proptech.thienkhoi.com/warehouse?Page=2",
    "https://proptech.thienkhoi.com/warehouse?pageIndex=2",
    "https://proptech.thienkhoi.com/warehouse?p=2",
    "https://proptech.thienkhoi.com/warehouse?offset=20",
    "https://proptech.thienkhoi.com/warehouse?page=2&pageSize=20",
    
    # Let's also check if they use paths like /warehouse/page/2
    "https://proptech.thienkhoi.com/warehouse/page/2"
]

print("=== Probing Next.js RSC Pagination ===")
for url in paging_candidates:
    print(f"\nProbing URL: {url}")
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"  Status: {r.status_code}")
        print(f"  Content-Length: {len(r.text)}")
        print(f"  Content-Type: {r.headers.get('Content-Type')}")
        
        # Next.js RSC text/x-component payload contains text lines starting with a number and colon
        # E.g. "1:I[...]" or "2:{"id":...}"
        snippet = r.text[:300].strip()
        print(f"  Snippet: {snippet}...")
        
        # Check if the snippet contains typical house listings text or address
        # Let's see if it has the keyword "trần" or "phạm" or "đường" or "tỷ" or "trần văn đang"
        # We can scan the entire body for keywords
        found_kw = []
        for kw in ["trần", "phạm", "đường", "tỷ", "trần văn đang", "phạm văn hai"]:
            if kw in r.text.lower():
                found_kw.append(kw)
        if found_kw:
            print(f"  [🎉 FOUND REAL ESTATE DATA!] Matches: {found_kw}")
            out_path = f"scratch/rsc_match_{url.split('?')[-1].replace('&', '_').replace('=', '_')}.txt"
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(r.text)
            print(f"    Saved matching RSC response to {out_path}")
            
    except Exception as e:
        print(f"  [❌] Error: {e}")
