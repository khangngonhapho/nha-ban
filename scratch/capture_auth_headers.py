import os
import sys
import time
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

cookie_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/thienkhoi_cookie.txt"

with open(cookie_path, 'r', encoding='utf-8') as f:
    cookie_str = f.read().strip()

cookies = []
for part in cookie_str.split(";"):
    part = part.strip()
    if not part:
        continue
    if "=" in part:
        name, val = part.split("=", 1)
        cookies.append({
            "name": name.strip(),
            "value": val.strip(),
            "domain": "proptech.thienkhoi.com",
            "path": "/"
        })

output_file = "scratch/auth_headers_captured.txt"
if os.path.exists(output_file):
    os.remove(output_file)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies(cookies)
    page = context.new_page()
    
    def on_request(req):
        url = req.url
        # If it's a backend request, log its headers to file
        if "backend.thienkhoi.com" in url:
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(f"\n[Request] {req.method} {url}\n")
                f.write("Headers:\n")
                for k, v in req.headers.items():
                    f.write(f"  {k}: {v}\n")
                f.write("-" * 50 + "\n")
            
    page.on("request", on_request)
    
    page.goto("https://proptech.thienkhoi.com/warehouse/sources", wait_until="networkidle", timeout=60000)
    time.sleep(5)
    browser.close()

if os.path.exists(output_file):
    print("Success! Logged headers to scratch/auth_headers_captured.txt")
else:
    print("No backend requests captured.")
