import os
import sys
import time
import json
import urllib.parse
from playwright.sync_api import sync_playwright

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
    cookie_str = f.read().strip()

# Parse cookie string into key-value pairs
cookies_list = []
for part in cookie_str.split(";"):
    part = part.strip()
    if not part:
        continue
    if "=" in part:
        name, val = part.split("=", 1)
        cookies_list.append({
            "name": name.strip(),
            "value": val.strip(),
            "domain": "proptech.thienkhoi.com",
            "path": "/"
        })

print(f"[i] Parsed {len(cookies_list)} cookies.")

print("Launching browser via Playwright...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies(cookies_list)
    
    captured_requests = []
    page = context.new_page()
    
    def handle_request(request):
        url = request.url
        if not any(ext in url.lower() for ext in [".css", ".png", ".jpg", ".jpeg", ".svg", ".woff", ".woff2", ".js.tải xuống"]) or "api" in url.lower():
            if "proptech.thienkhoi.com" in url:
                req_info = {
                    "method": request.method,
                    "url": url,
                    "headers": request.headers,
                    "post_data": request.post_data
                }
                captured_requests.append(req_info)
                print(f"[🌐 Network Request] {request.method} {url}")
                if request.post_data:
                    print(f"  Post Data: {request.post_data}")
                if request.headers.get("next-action"):
                    print(f"  Next-Action Header: {request.headers.get('next-action')}")
                print("-" * 50)
                
    page.on("request", handle_request)
    
    print("\nNavigating to warehouse...")
    page.goto("https://proptech.thienkhoi.com/warehouse", wait_until="networkidle", timeout=60000)
    print(f"Current page URL: {page.url}")
    
    if "login" in page.url.lower() or "security" in page.url.lower():
        print("[⚠️ WARNING] Browser redirected to login or check security. Cookie might be expired!")
    
    print("\nScrolling down to trigger infinite scroll...")
    for i in range(3):
        print(f"  Scroll {i+1}...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        
    print("\nScroll complete. Saving captured network log...")
    
    with open("scratch/captured_requests.json", "w", encoding="utf-8") as out:
        json.dump(captured_requests, out, indent=2, ensure_ascii=False)
        
    print("Saved network log to scratch/captured_requests.json")
    browser.close()
