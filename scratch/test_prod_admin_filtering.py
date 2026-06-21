# -*- coding: utf-8 -*-
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright
import time
import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

creds_file = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/khangngo-admin-a96043c2f638.json"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if os.path.exists(creds_file):
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    creds.get_access_token()
    token = creds.access_token
    print(f"Generated OAuth token: {token[:20]}...")
    
    with sync_playwright() as p:
        print("Launching Chromium...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        page.on("console", lambda msg: print(f"[JS Console] {msg.text}"))
        
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
                isSecureLoaded: window.isSecureLoaded,
                isDataLoaded: window.isDataLoaded,
                dataLength: window.DATA.length,
                poolRowsLength: window.POOL_ROWS.length
            };
        }""")
        print("Load Status on Prod:", status)
        
        diag = page.evaluate("""() => {
            const res = {};
            res.activeMode = window.activeMode;
            
            const poolData = window.getMappedPoolData();
            res.poolLength = poolData.length;
            
            // Set Q.1 and Ngõ ngách (2 - 2.5m)
            window.selDistricts.clear();
            window.selDistricts.add('q1');
            window.activeDynamicFilters['Criteria_Duong_truoc_nha'] = 'Ngõ ngách (2 - 2.5m)';
            
            const filtered = window.getFiltered();
            res.filteredLength = filtered.length;
            res.filteredItems = filtered.map(p => ({
                id: p.id,
                system_id: p.system_id,
                q: p.q,
                phuong: p.phuong,
                json_ui: p.json_ui_parsed,
                is_invisible: p.is_invisible
            }));
            
            return res;
        }""")
        
        print("\n=== PROD DIAGNOSTICS ===")
        print(json.dumps(diag, ensure_ascii=False, indent=2))
        
        page.evaluate("""() => {
            window.applyFilter();
        }""")
        time.sleep(2)
        
        visible_cards = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.card .ititle')).map(el => el.textContent.trim());
        }""")
        print("Visible card titles in DOM on Prod:", visible_cards)
        
        screenshot_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/prod_filter_screenshot.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to: {screenshot_path}")
        
        browser.close()
else:
    print("Credentials file does not exist")
