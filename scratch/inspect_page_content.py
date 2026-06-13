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

if not os.path.exists(cookie_path):
    print("Cookie file not found")
    sys.exit(1)

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
    
    print("Navigating to https://proptech.thienkhoi.com/warehouse ...")
    page.goto("https://proptech.thienkhoi.com/warehouse", wait_until="networkidle", timeout=60000)
    print(f"Current URL: {page.url}")
    
    # Wait for the page content to load fully
    time.sleep(5)
    
    # Check page title
    print(f"Page Title: {page.title()}")
    
    # Check if there is any visible text
    body_text = page.locator("body").inner_text()
    print(f"Body text length: {len(body_text)}")
    print("First 500 chars of body text:")
    print(body_text[:500])
    
    # Save HTML and screenshot
    os.makedirs("scratch", exist_ok=True)
    page.screenshot(path="scratch/page_screenshot.png")
    print("Saved screenshot to scratch/page_screenshot.png")
    
    with open("scratch/page_body.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    print("Saved page content to scratch/page_body.html")
    
    # Let's count how many property cards or titles are shown
    # In the detail page, titles are matching p[data-testid='title-property'] or similar
    # Let's find all elements containing 'Trần Văn Đang' or similar
    titles = page.locator("p").all_inner_texts()
    property_titles = [t for t in titles if "trần" in t.lower() or "đường" in t.lower() or "tỷ" in t.lower()]
    print(f"Found {len(property_titles)} matching titles:")
    for t in property_titles[:5]:
        print(f"  - {t}")
        
    browser.close()
