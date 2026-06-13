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

log_lines = []
def log(msg):
    log_lines.append(msg)
    print(msg)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies(cookies)
    page = context.new_page()
    
    # Register events
    page.on("console", lambda msg: log(f"[Console {msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: log(f"[Page Error] {err.message}\n{err.stack}"))
    
    def on_request(req):
        url = req.url
        if any(ext in url.lower() for ext in [".css", ".png", ".jpg", ".jpeg", ".svg", ".woff", ".woff2", "_next/static"]):
            return
        log(f"[Req] {req.method} {url}")
        
    def on_response(res):
        url = res.url
        if any(ext in url.lower() for ext in [".css", ".png", ".jpg", ".jpeg", ".svg", ".woff", ".woff2", "_next/static"]):
            return
        log(f"[Res] {res.status} {url}")
        try:
            if "application/json" in res.headers.get("content-type", ""):
                log(f"  JSON Response: {res.text()[:500]}")
        except Exception:
            pass
        
    page.on("request", on_request)
    page.on("response", on_response)
    
    log("\n=== Starting navigation to /warehouse/sources ===")
    try:
        page.goto("https://proptech.thienkhoi.com/warehouse/sources", wait_until="networkidle", timeout=60000)
    except Exception as e:
        log(f"[Goto Error] {e}")
        
    log("\n=== Navigation completed. Waiting 10s ===")
    time.sleep(10)
    
    # Check what is rendered
    body_text = page.locator("body").inner_text()
    log(f"Text length: {len(body_text)}")
    log("First 1000 characters of body text:")
    log(body_text[:1000])
    
    # Check if there are titles
    titles = page.locator("p").all_inner_texts()
    property_titles = [t for t in titles if "trần" in t.lower() or "đường" in t.lower() or "tỷ" in t.lower()]
    log(f"Found {len(property_titles)} matching titles:")
    for t in property_titles[:10]:
        log(f"  - {t}")
        
    # Let's save a screenshot and the HTML
    page.screenshot(path="scratch/sources_page_screenshot.png")
    log("Saved screenshot to scratch/sources_page_screenshot.png")
    
    with open("scratch/sources_page_body.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    log("Saved page content to scratch/sources_page_body.html")
    
    # Let's write the logs to file
    with open("scratch/full_sources_load_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))
        
    browser.close()
