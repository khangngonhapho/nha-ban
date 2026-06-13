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
        if "backend.thienkhoi.com" in req.url:
            print(f"[Req] {req.method} {req.url}")
            
    def log_response(res):
        if "backend.thienkhoi.com" in res.url:
            print(f"[Res] {res.status} {res.url}")
            try:
                # Print json preview if possible
                if "application/json" in res.headers.get("content-type", ""):
                    print(f"  JSON: {res.text()[:500]}")
            except Exception:
                pass
                
    page.on("request", log_request)
    page.on("response", log_response)
    
    uuid = "19c74ebc-e5a4-4cfb-844b-3ae5365e6318"
    url = f"https://proptech.thienkhoi.com/warehouse/sources/{uuid}"
    print(f"Navigating to detail page: {url}")
    page.goto(url, wait_until="networkidle", timeout=60000)
    time.sleep(3)
    
    # Let's list all elements that look like tab triggers to click them
    # Usually they have role="tab" or text like "Thông tin chi tiết", "Hồ sơ pháp lý"
    # Let's find and click them
    print("\n=== Clicking 'Thông tin chi tiết' ===")
    try:
        # Search for elements containing "Thông tin chi tiết"
        detail_tab = page.locator("role=tab[name='Thông tin chi tiết']").first
        if detail_tab.count() == 0:
            detail_tab = page.locator("text='Thông tin chi tiết'").first
        
        detail_tab.click()
        print("Clicked 'Thông tin chi tiết' tab.")
    except Exception as e:
        print(f"Error clicking detail tab: {e}")
    time.sleep(3)
    
    print("\n=== Clicking 'Hồ sơ pháp lý' ===")
    try:
        legal_tab = page.locator("role=tab[name='Hồ sơ pháp lý']").first
        if legal_tab.count() == 0:
            legal_tab = page.locator("text='Hồ sơ pháp lý'").first
            
        legal_tab.click()
        print("Clicked 'Hồ sơ pháp lý' tab.")
    except Exception as e:
        print(f"Error clicking legal tab: {e}")
    time.sleep(3)
    
    # Capture final page screenshot to confirm what we saw
    page.screenshot(path="scratch/detail_tabs_screenshot.png")
    print("\nSaved screenshot to scratch/detail_tabs_screenshot.png")
    
    browser.close()
