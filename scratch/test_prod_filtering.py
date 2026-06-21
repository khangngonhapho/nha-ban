# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')

def run_test():
    with sync_playwright() as p:
        print("Launching Chromium...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        # Inject client bypass credentials for lead capture
        page.add_init_script("""
            localStorage.setItem('client_name', 'Test Customer');
            localStorage.setItem('client_phone', '0901234567');
        """)
        
        # Navigate to shared link using the public ID HWMHIMBZINVN
        url = "https://khangngonhapho.vercel.app/?s=HWMHIMBZINVN"
        print(f"Navigating to: {url}")
        page.goto(url, wait_until="networkidle")
        
        # Wait a bit for JS to execute
        time.sleep(2)
        
        # Check visible card titles
        titles = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.card .ititle')).map(el => el.textContent.trim());
        }""")
        print("Initial visible cards on prod:", titles)
        
        # Open filter panel
        print("Opening filter panel...")
        page.click("#filterBtn")
        time.sleep(0.5)
        
        # Check if dynamic filter select is rendered
        has_select = page.evaluate("() => !!document.getElementById('filter_Criteria_Duong_truoc_nha')")
        print("Has dynamic filter select:", has_select)
        
        if has_select:
            # Select "Ngõ ngách (2 - 2.5m)"
            print("Selecting 'Ngõ ngách (2 - 2.5m)'...")
            page.select_option("#filter_Criteria_Duong_truoc_nha", "Ngõ ngách (2 - 2.5m)")
            time.sleep(2)
            
            # Check visible card titles after filter
            titles_after = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('.card .ititle')).map(el => el.textContent.trim());
            }""")
            print("Cards after dynamic filter:", titles_after)
            
            # Now let's test the F5 restore bug. We'll set admin mode simulation
            print("\n--- Testing F5 restore bug simulation ---")
            page.evaluate("""() => {
                window.isAdmin = true;
                localStorage.setItem('isAdminSession', 'true');
                // Set some filter states
                window.selDistricts.clear();
                window.selDistricts.add('q1');
                window.activeDynamicFilters['Criteria_Duong_truoc_nha'] = 'Ngõ ngách (2 - 2.5m)';
                window.saveState();
            }""")
            
            # Read saved state from localStorage
            saved_state = page.evaluate("() => localStorage.getItem('adminState')")
            print("Saved state in localStorage:", saved_state)
            
        browser.close()

if __name__ == "__main__":
    run_test()
