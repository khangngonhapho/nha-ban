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

print(f"Parsed {len(cookies)} cookies.")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies(cookies)
    page = context.new_page()
    
    # Enable console logging
    page.on("console", lambda msg: print(f"[Browser Console {msg.type}] {msg.text}"))
    
    # Capture all network requests
    requests_log = []
    def log_request(request):
        url = request.url
        # Ignore static assets
        if any(ext in url.lower() for ext in [".css", ".png", ".jpg", ".jpeg", ".svg", ".woff", ".woff2", "_next/static"]):
            return
        print(f"[Network Request] {request.method} {url}")
        requests_log.append({
            "method": request.method,
            "url": url,
            "headers": request.headers
        })
        
    def log_response(response):
        url = response.url
        if any(ext in url.lower() for ext in [".css", ".png", ".jpg", ".jpeg", ".svg", ".woff", ".woff2", "_next/static"]):
            return
        print(f"[Network Response] {response.status} {url}")
        try:
            # Print response body preview if it's JSON or small text
            if "application/json" in response.headers.get("content-type", ""):
                print(f"  JSON Response: {response.text()[:500]}")
        except Exception as e:
            pass
            
    page.on("request", log_request)
    page.on("response", log_response)
    
    print("\nNavigating to warehouse...")
    page.goto("https://proptech.thienkhoi.com/warehouse", wait_until="networkidle", timeout=60000)
    print(f"Current page URL: {page.url}")
    
    print("\nWaiting 10 seconds for content to load...")
    time.sleep(10)
    
    print(f"\nFinal Title: {page.title()}")
    text_content = page.locator("body").inner_text()
    print(f"Text length: {len(text_content)}")
    
    # Let's scroll down to see if anything gets triggered
    print("\nScrolling down...")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(5)
    
    browser.close()
