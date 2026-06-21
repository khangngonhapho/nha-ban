# -*- coding: utf-8 -*-
import os
import sys
import time
import socket
import threading
import http.server
import socketserver
import json
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

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
    project_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    time.sleep(1.0)
    
    # Let's fetch the actual sheet data using gspread first so we can mock the responses
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    
    creds_file = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/khangngo-admin-a96043c2f638.json"
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    
    POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
    SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'
    
    source_sheet = client.open_by_key(SOURCE_SHEET_ID).worksheet("Source")
    source_rows = source_sheet.get_all_values()
    
    pool_sheet = client.open_by_key(POOL_SHEET_ID).worksheet("Pool")
    pool_rows = pool_sheet.get_all_values()
    
    print(f"Server running on port {port}. Mock data loaded.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # Log console messages
        page.on("console", lambda msg: print(f"[JS Console] {msg.text}"))
        
        # Inject admin credentials
        page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600*1000).toString());
        """)
        
        # Mock Google Sheets API requests
        def handle_sheets(route):
            url = route.request.url
            if SOURCE_SHEET_ID in url:
                route.fulfill(content_type="application/json", body=json.dumps({"values": source_rows}))
            elif POOL_SHEET_ID in url:
                route.fulfill(content_type="application/json", body=json.dumps({"values": pool_rows}))
            else:
                route.continue_()
                
        page.route("https://sheets.googleapis.com/**", handle_sheets)
        
        # Navigate to index.html
        page.goto(f"http://localhost:{port}/index.html", wait_until="networkidle")
        time.sleep(2)
        
        # Run diagnostics in the page context
        diagnostics = page.evaluate("""() => {
            const results = {};
            results.isAdmin = window.isAdmin;
            results.activeMode = window.activeMode;
            results.dataLength = window.DATA.length;
            results.poolRowsLength = window.POOL_ROWS.length;
            
            // Switch to pool mode
            if (typeof window.switchMode === 'function') {
                window.switchMode('pool');
            }
            results.modeAfterSwitch = window.activeMode;
            
            const poolData = window.getMappedPoolData();
            results.mappedPoolLength = poolData.length;
            
            // Find Nguyễn Văn Nguyễn in mapped pool data
            const nvn = poolData.find(p => p.id === 'HWMHIMBZINVN' || (p.t && p.t.includes('Nguyễn Văn Nguyễn')));
            if (nvn) {
                results.nvn_found = {
                    id: nvn.id,
                    system_id: nvn.system_id,
                    q: nvn.q,
                    phuong: nvn.phuong,
                    json_ui: nvn.json_ui_parsed,
                    is_invisible: nvn.is_invisible
                };
            } else {
                results.nvn_found = "Not found in mapped pool data";
            }
            
            // Set filter manually
            window.selDistricts.clear();
            window.selDistricts.add('q1');
            window.activeDynamicFilters['Criteria_Duong_truoc_nha'] = 'Ngõ ngách (2 - 2.5m)';
            
            const filtered = window.getFiltered();
            results.filteredLength = filtered.length;
            results.filteredItems = filtered.map(p => ({id: p.id, q: p.q, json_ui: p.json_ui_parsed}));
            
            return results;
        }""")
        
        print("\n=== DIAGNOSTICS RESULTS ===")
        print(json.dumps(diagnostics, ensure_ascii=False, indent=2))
        
        browser.close()

if __name__ == "__main__":
    main()
