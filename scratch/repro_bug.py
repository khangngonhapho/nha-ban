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
    print(f"Local server started on port {port} serving {directory}")
    server.serve_forever()
    return server

def main():
    project_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    
    time.sleep(1.5)
    
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        # Log all console messages
        page.on("console", lambda msg: print(f"[Console {msg.type}] {msg.text}"))
        page.on("requestfailed", lambda req: print(f"[Request Failed] {req.url}"))
        
        # Inject client bypass
        page.add_init_script("""
            localStorage.setItem('client_name', 'Test Customer');
            localStorage.setItem('client_phone', '0901234567');
        """)
        
        # Mock /api/config to return config from settings.json
        with open('settings.json', 'r', encoding='utf-8') as f:
            settings_cfg = json.load(f)
            
        def handle_api_config(route):
            mock_config = {
                "status": "success",
                "config": settings_cfg
            }
            route.fulfill(content_type="application/json", body=json.dumps(mock_config))
            
        page.route("**/api/config**", handle_api_config)
        
        # Navigate to target listing page
        client_url = f"http://localhost:{port}/index.html?s=HWMHIMBZINVN"
        print(f"Navigating to {client_url}")
        page.goto(client_url, wait_until="load")
        
        print("Waiting for cards to load...")
        page.wait_for_selector(".card", timeout=15000)
        
        initial_cards = page.locator(".card").count()
        print(f"Initial cards count: {initial_cards}")
        
        # Let's inspect the loaded window.DATA
        data_state = page.evaluate("""() => {
            return window.DATA.map(p => ({
                id: p.id,
                t: p.t,
                json_ui_parsed: p.json_ui_parsed,
                is_invisible: p.is_invisible,
                q: p.q,
                duong_truoc_nha: p.duong_truoc_nha
            }));
        }""")
        print("DATA in window.DATA:", json.dumps(data_state, ensure_ascii=False, indent=2))
        
        # Open filter panel
        print("Opening filter panel...")
        page.locator("#filterBtn").click()
        page.wait_for_selector("#filterPanel.open", timeout=5000)
        
        # Check if the dynamic filter select is present
        dynamic_select_selector = "#filter_Criteria_Duong_truoc_nha"
        page.wait_for_selector(dynamic_select_selector, timeout=5000)
        print("Dynamic select is visible.")
        
        # Print select options
        options = page.evaluate(f"""() => {{
            const select = document.querySelector('{dynamic_select_selector}');
            return Array.from(select.options).map(opt => opt.value);
        }}""")
        print("Select options:", options)
        
        # Select "Ngõ ngách (2 - 2.5m)"
        print("Selecting 'Ngõ ngách (2 - 2.5m)'...")
        page.select_option(dynamic_select_selector, "Ngõ ngách (2 - 2.5m)")
        
        # Wait a bit for filter to apply
        time.sleep(2)
        
        # Verify filtered cards
        after_filter_cards = page.locator(".card").count()
        print(f"Cards count after filter: {after_filter_cards}")
        
        # Get active filters on page
        active_filters = page.evaluate("() => window.activeDynamicFilters")
        print("Active filters:", active_filters)
        
        # Print the filtered window.DATA or applyFilter evaluation result
        eval_result = page.evaluate("""() => {
            let a = [...window.DATA];
            const activeDynamicFilters = window.activeDynamicFilters;
            const log = [];
            for (const [field, filterVal] of Object.entries(activeDynamicFilters)) {
                if (filterVal) {
                    a = a.filter(p => {
                        const jsonUiObj = p.json_ui_parsed || {};
                        const valInListing = jsonUiObj[field] || '';
                        const matched = String(valInListing).toLowerCase().includes(String(filterVal).toLowerCase());
                        log.push({
                            pid: p.id,
                            field: field,
                            valInListing: valInListing,
                            filterVal: filterVal,
                            matched: matched
                        });
                        return matched;
                    });
                }
            }
            return { log: log, remaining: a.length };
        }""")
        print("Client filter evaluation debug:", json.dumps(eval_result, ensure_ascii=False, indent=2))
        
        browser.close()

if __name__ == "__main__":
    main()
