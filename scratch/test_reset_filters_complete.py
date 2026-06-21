# -*- coding: utf-8 -*-
import os
import sys
import time
import socket
import threading
import http.server
import socketserver
import json
from oauth2client.service_account import ServiceAccountCredentials
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def run_server(port, directory):
    class Handler(QuietHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
    server = socketserver.TCPServer(("", port), Handler)
    server.serve_forever()

def main():
    creds_file = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/khangngo-admin-a96043c2f638.json"
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    token = ""
    
    if os.path.exists(creds_file):
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        creds.get_access_token()
        token = creds.access_token
        print(f"Generated OAuth token: {token[:20]}...")
    else:
        print("Credentials file not found, token auth might fail.")

    project_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    
    time.sleep(1.0)
    
    with sync_playwright() as p:
        print("Launching Chromium for E2E Reset Filter test...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        page.on("console", lambda msg: print(f"[Console {msg.type}] {msg.text}"))
        
        # Inject initial states: activeCollectionName = 'favorites' and showFavOnly = true
        # Also mock Admin Session
        page.add_init_script(f"""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', '{token}');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600*1000).toString());
            localStorage.setItem('activeCollectionName', 'favorites');
            localStorage.setItem('favs', '["SYS-20262320-305"]');
            
            // Mock state with districts: q1
            const state = {{
              districts: ["q1"],
              wards: [],
              duongs: [],
              huongs: [],
              gia: [],
              danhGia: [],
              selectedIds: [],
              favOnly: true,
              showOnAirOnly: false,
              search: '',
              adv: {{}}
            }};
            localStorage.setItem('adminState', JSON.stringify(state));
            window.confirm = () => true;
            window.alert = () => {{}};
        """)
        
        # Load settings.json to mock /api/config
        with open('settings.json', 'r', encoding='utf-8') as f:
            settings_cfg = json.load(f)
            
        def handle_api_config(route):
            mock_config = {
                "status": "success",
                "config": settings_cfg
            }
            route.fulfill(content_type="application/json", body=json.dumps(mock_config))
            
        page.route("**/api/config**", handle_api_config)
        
        # Navigate to admin view (index.html is the main entry)
        url = f"http://localhost:{port}/index.html"
        print(f"Navigating to: {url}")
        page.goto(url, wait_until="load")
        
        time.sleep(5) # Wait for parallel data load
        
        # Check initial filter summary
        summary_text = page.locator("#filterSummary").text_content()
        print(f"Initial summary text on DOM: '{summary_text}'")
        
        # Check if reset button is visible (since districts or collection is active)
        reset_visible = page.locator("#resetBtn").is_visible()
        print(f"Is reset button visible? {reset_visible}")
        
        # Execute reset
        print("Clicking reset button...")
        try:
            page.locator("#resetBtn").click(timeout=5000)
            time.sleep(1)
        except Exception as e:
            print(f"Failed to click resetBtn: {e}")
        
        # Verify states in localStorage
        active_col = page.evaluate("() => localStorage.getItem('activeCollectionName')")
        print(f"LocalStorage activeCollectionName after reset: {active_col}")
        
        final_summary = page.locator("#filterSummary").text_content()
        print(f"Filter summary text after reset: '{final_summary}'")
        
        # Verification
        success = True
        # NOTE: At this point, since we haven't applied the code changes,
        # we expect the test to fail.
        if active_col is not None:
            print("FAILURE/UNFIXED: activeCollectionName was not removed from localStorage!")
            success = False
        if final_summary != "Tất cả":
            print(f"FAILURE/UNFIXED: Filter summary is not 'Tất cả' (got: '{final_summary}')!")
            success = False
            
        if success:
            print("VERIFICATION SUCCESS: Reset filters now correctly clears hidden collections and updates summary!")
        else:
            print("VERIFICATION FAILURE (EXPECTED BEFORE FIX): Reset filters logic still has issues.")
            
        browser.close()

if __name__ == "__main__":
    main()
