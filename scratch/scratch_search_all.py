import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def search_api():
    with open("fetcher.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    print("=== Search for API endpoints in fetcher.py ===")
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "https://" in line or "/product/" in line or "payload" in line or "query" in line:
            for l in lines[max(0, i-2):min(len(lines), i+8)]:
                print(f"{i}: {l}")
            print("---")

search_api()
