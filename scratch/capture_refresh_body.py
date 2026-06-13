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

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies(cookies)
    page = context.new_page()
    
    def log_request(req):
        if "refresh-token" in req.url:
            print(f"\n[Refresh Request] POST {req.url}")
            print("Headers:")
            for k, v in req.headers.items():
                if k.lower() in ["authorization", "cookie"]:
                    print(f"  {k}: {v[:40]}... (Length: {len(v)})")
                else:
                    print(f"  {k}: {v}")
            print(f"Post Data: {req.post_data}")
            
    def log_response(res):
        if "refresh-token" in res.url:
            print(f"\n[Refresh Response] Status {res.status} {res.url}")
            try:
                print(f"Response text: {res.text()[:1000]}")
            except Exception as e:
                print(f"Could not read response: {e}")
                
    page.on("request", log_request)
    page.on("response", log_response)
    
    print("Navigating to warehouse/sources...")
    try:
        page.goto("https://proptech.thienkhoi.com/warehouse/sources", wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"Navigation error: {e}")
    time.sleep(5)
    browser.close()
