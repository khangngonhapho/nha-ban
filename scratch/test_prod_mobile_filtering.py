# -*- coding: utf-8 -*-
import os
import sys
import time
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

creds_file = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/khangngo-admin-a96043c2f638.json"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def main():
    token = ""
    if os.path.exists(creds_file):
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        creds.get_access_token()
        token = creds.access_token
        print(f"Generated OAuth token: {token[:20]}...")
    else:
        print("Credentials file not found.")
        sys.exit(1)
        
    with sync_playwright() as p:
        print("Launching Chromium with Mobile Viewport (Pixel 5)...")
        pixel_5 = p.devices['Pixel 5']
        browser = p.chromium.launch(headless=True)
        # Create context simulating a mobile device
        context = browser.new_context(**pixel_5)
        page = context.new_page()
        
        page.on("console", lambda msg: print(f"[JS Console] {msg.text}"))
        
        # Inject Auth token and bypasses
        page.add_init_script(f"""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', '{token}');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600*1000).toString());
            window.confirm = () => true;
            window.alert = () => {{}};
        """)
        
        print("Navigating to production Vercel app...")
        page.goto("https://khangngonhapho.vercel.app/index.html", wait_until="networkidle")
        time.sleep(5)
        
        status = page.evaluate("""() => {
            return {
                isAdmin: window.isAdmin,
                activeMode: window.activeMode,
                dataLength: window.DATA.length,
                poolRowsLength: window.POOL_ROWS.length
            };
        }""")
        print("Initial Load Status on Mobile:", status)
        
        # Capture screenshot of initial screen
        initial_shot = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/mobile_0_initial.png"
        page.screenshot(path=initial_shot)
        print(f"Initial screenshot saved to: {initial_shot}")
        
        # Check if we are in Pool mode (based on green circle icon or switcher)
        # We need to make sure we switch to Pool Mode if we are in standard mode
        print("Switching mode to Pool Mode (click green circle/admin mode)...")
        # In Admin view, the green circle or pool mode button can be clicked
        # Let's check active mode
        if status['activeMode'] != 'pool':
            # Let's click the switch mode button
            page.evaluate("""() => {
                if (typeof window.switchMode === 'function') {
                    window.switchMode('pool');
                }
            }""")
            time.sleep(2)
            print("Mode after switch:", page.evaluate("window.activeMode"))

        # Click the filterBtn to open the filter panel
        print("Clicking Filter Button...")
        page.locator("#filterBtn").click()
        time.sleep(2)
        
        # Capture screenshot of opened filter panel
        filter_shot = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/mobile_1_filter_panel.png"
        page.screenshot(path=filter_shot)
        print(f"Filter panel screenshot saved to: {filter_shot}")
        
        # In the filter panel, select District: "Quận 1" (q1)
        # Because District dropdown is a custom multi-select, let's open it
        print("Opening District Multi-select...")
        page.locator("#districtMulti").click()
        time.sleep(1)
        
        # Click the checkbox with value="q1"
        print("Checking 'Quận 1' checkbox...")
        checkbox = page.locator('#districtOptions input[value="q1"]')
        if checkbox.count() > 0:
            checkbox.check()
            time.sleep(1)
        else:
            print("Quận 1 checkbox not found!")
            # Fallback direct JS injection just in case, but we want to simulate UI
            page.evaluate("""() => {
                window.selDistricts.clear();
                window.selDistricts.add('q1');
                window.updateSelectionFromCheckboxes('district');
            }""")
            
        # Select "Ngõ ngách (2 - 2.5m)" from dynamic filter select
        print("Selecting 'Ngõ ngách (2 - 2.5m)' from dropdown...")
        page.select_option("#filter_Criteria_Duong_truoc_nha", "Ngõ ngách (2 - 2.5m)")
        time.sleep(1)
        
        # Take a screenshot of filters selected
        filter_selected_shot = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/mobile_2_filters_selected.png"
        page.screenshot(path=filter_selected_shot)
        print(f"Filters selected screenshot saved to: {filter_selected_shot}")
        
        # Close the filter panel using the back button or apply button
        print("Closing filter panel via back button...")
        back_btn = page.locator(".mobile-filter-back-btn")
        if back_btn.count() > 0:
            back_btn.click()
        else:
            # Fallback to apply button
            apply_btn = page.locator(".btn-filter-apply")
            if apply_btn.count() > 0:
                apply_btn.click()
            else:
                page.evaluate("toggleFilter()")
        time.sleep(2)
        
        # Check results
        results = page.evaluate("""() => {
            return {
                filteredLength: window.getFiltered().length,
                summaryText: document.getElementById('filterSummary').textContent,
                visibleCards: Array.from(document.querySelectorAll('.card .ititle')).map(el => el.textContent.trim())
            };
        }""")
        print("Results on Mobile viewport:", results)
        
        # Take final screenshot of the result screen
        final_shot = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/mobile_3_final_result.png"
        page.screenshot(path=final_shot)
        print(f"Final result screenshot saved to: {final_shot}")
        
        browser.close()

if __name__ == "__main__":
    main()
