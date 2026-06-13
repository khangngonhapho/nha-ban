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

print(f"Loading page with cookies. Current time: {time.time()}")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies(cookies)
    page = context.new_page()
    
    # Capture all backend requests to see if any refresh is called or what happens
    def log_request(req):
        if "backend.thienkhoi.com" in req.url:
            print(f"[Req] {req.method} {req.url}")
            # print Authorization header (masked)
            auth = req.headers.get("authorization")
            if auth:
                print(f"  Authorization: {auth[:30]}...")
            else:
                print("  No Authorization header!")
                
    def log_response(res):
        if "backend.thienkhoi.com" in res.url:
            print(f"[Res] {res.status} {res.url}")
            
    page.on("request", log_request)
    page.on("response", log_response)
    
    print("\nNavigating to /warehouse/sources...")
    page.goto("https://proptech.thienkhoi.com/warehouse/sources", wait_until="networkidle", timeout=60000)
    time.sleep(5)
    
    print(f"Current page URL: {page.url}")
    print(f"Page Title: {page.title()}")
    
    # Check if titles exist
    titles = page.locator("p").all_inner_texts()
    property_titles = [t for t in titles if "trần" in t.lower() or "đường" in t.lower() or "tỷ" in t.lower()]
    print(f"Found {len(property_titles)} listings on the page.")
    
    # Capture screenshot
    page.screenshot(path="scratch/post_expiration_screenshot.png")
    print("Saved screenshot to scratch/post_expiration_screenshot.png")
    
    # Check cookies again
    updated_cookies = context.cookies()
    new_cookies_dict = {c["name"]: c["value"] for c in updated_cookies}
    print(f"Cookies after page load: {list(new_cookies_dict.keys())}")
    
    browser.close()
