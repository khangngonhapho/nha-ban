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

print(f"Original cookies parsed: {len(cookies)}")
orig_access_token = next((c["value"] for c in cookies if c["name"] == "TKG_accessToken"), None)
print(f"Original TKG_accessToken snippet: {orig_access_token[:50]}...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies(cookies)
    page = context.new_page()
    
    print("\nNavigating to warehouse/sources to trigger middleware cookie refresh...")
    page.goto("https://proptech.thienkhoi.com/warehouse/sources", wait_until="networkidle", timeout=60000)
    time.sleep(5)
    
    print("\nReading updated cookies from browser context...")
    updated_cookies = context.cookies()
    print(f"Total updated cookies: {len(updated_cookies)}")
    
    new_cookies_dict = {}
    for c in updated_cookies:
        new_cookies_dict[c["name"]] = c["value"]
        
    new_access_token = new_cookies_dict.get("TKG_accessToken")
    print(f"New TKG_accessToken snippet: {new_access_token[:50]}...")
    
    if new_access_token != orig_access_token:
        print("[🎉 SUCCESS] Token refreshed successfully by middleware!")
        
        # Construct the new cookie string
        new_parts = []
        for name, val in new_cookies_dict.items():
            new_parts.append(f"{name}={val}")
        new_cookie_str = "; ".join(new_parts) + ";"
        
        # Save new cookies to thienkhoi_cookie.txt
        with open(cookie_path, "w", encoding="utf-8") as f:
            f.write(new_cookie_str)
        print(f"Saved refreshed cookies back to {cookie_path}!")
    else:
        print("[!] Token did not change. It might still be valid or refresh failed.")
        
    browser.close()
