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
    artifacts_dir = r"C:\Users\Khang Ngo\.gemini\antigravity\brain\595fc691-aac4-4d6b-9257-a1e94612755c"
    
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    
    time.sleep(1.5) # Allow server to bind
    
    target_url = f"http://localhost:{port}/index.html"
    print(f"Navigating to admin dashboard: {target_url}")
    
    # Define Mock Data for Admin Sheets API
    mock_source_row = [""] * 46
    mock_source_row[0] = "1001"
    mock_source_row[1] = "CP"
    mock_source_row[3] = "SYS-1001"
    mock_source_row[4] = "Căn CMT8 Q3 VIP"
    mock_source_row[5] = "100"
    mock_source_row[8] = "8.5"
    mock_source_row[9] = "Q3"
    mock_source_row[10] = "Phường 11"
    mock_source_row[37] = "SYS-1001"

    mock_pool_row = [""] * 96
    mock_pool_row[0] = "1001"
    mock_pool_row[5] = "Cách Mạng Tháng Tám"
    mock_pool_row[6] = "123"
    mock_pool_row[9] = "Nội dung chính CMT8 Q3 VIP"
    mock_pool_row[10] = "Mô tả chi tiết CMT8 Q3 VIP"
    mock_pool_row[11] = "8.5"
    mock_pool_row[13] = "100"
    mock_pool_row[27] = "https://res.cloudinary.com/demo/image/upload/sodo1_123.jpg"
    mock_pool_row[28] = "https://res.cloudinary.com/demo/image/upload/sodo2_123.jpg"
    mock_pool_row[29] = "https://res.cloudinary.com/demo/image/upload/mat_tien_123.jpg"
    mock_pool_row[40] = "https://res.cloudinary.com/demo/image/upload/interior_1.jpg"
    mock_pool_row[55] = "1001"
    mock_pool_row[72] = "SYS-1001"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 1200})
        page = context.new_page()
        
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        # Inject credentials to bypass auth screen and act as logged in
        page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
        """)
        
        # Intercept API calls to return mock sheets data
        def handle_sheets(route):
            url = route.request.url
            if "Source" in url:
                route.fulfill(content_type="application/json", body=json.dumps({"values": [mock_source_row]}))
            else:
                route.fulfill(content_type="application/json", body=json.dumps({"values": [mock_pool_row]}))
        
        page.route(lambda url: "spreadsheets" in url and "values" in url, handle_sheets)
        page.route("**/maps.google.com/**", lambda route: route.fulfill(status=200, body="<html>Dummy Maps</html>"))
        page.route("**/res.cloudinary.com/**", lambda route: route.fulfill(status=200, body="Dummy Image"))
        
        try:
            page.goto(target_url, wait_until="load", timeout=30000)
            page.wait_for_function("window.isSecureLoaded === true", timeout=10000)
            
            # Open curation drawer
            page.evaluate("openPoolS('SYS-1001')")
            page.wait_for_selector("#accPreview", timeout=5000)
            
            # Click Editor Accordion header to expand it
            print("Expanding Curation editor accordion...")
            page.locator("#accSource .accordion-header").click()
            time.sleep(1.0)
            
            # Click AI auto-fill to activate form details
            print("Clicking auto-fill button...")
            page.locator("#btnAutoFillCuration").click()
            time.sleep(1.5)
            
            # Expand preview accordion tab
            print("Expanding Preview accordion...")
            page.locator("#accPreview .accordion-header").click()
            time.sleep(4.0) # Wait for iframe to render and fetch parent memory listing
            
            # Print console logs
            print("\n=== CONSOLE LOGS ===")
            for log in console_logs:
                print(log)
            print("====================\n")
            
            # Take screenshot of the entire Curation Modal showing the iframe preview inside it
            screenshot_path = os.path.join(artifacts_dir, "admin_curation_preview_full.png")
            page.screenshot(path=screenshot_path)
            print(f"Full curation preview screenshot saved to: {screenshot_path}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
