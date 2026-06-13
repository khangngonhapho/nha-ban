import re

with open('curator_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'POOL_HEADERS\s*=\s*\[(.*?)\]', content, re.DOTALL)
if match:
    headers_str = match.group(1)
    headers = [h.strip().strip("'\"") for h in headers_str.split(',') if h.strip()]
    print("Google Sheets Pool Headers:")
    for idx, h in enumerate(headers):
        # Convert non-ascii characters to ascii-safe form
        safe_h = ''.join(c if ord(c) < 128 else '?' for c in h)
        print(f"  {idx+1}: {safe_h}")
else:
    print("POOL_HEADERS not found")
