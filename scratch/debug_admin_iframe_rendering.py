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
    
    # Dummy headers for Google Sheets parsing
    source_headers = [""] * 46
    pool_headers = [""] * 96
    
    # ── Define Mock Data for Published Listing (renders iframe) ──
    mock_source_row_1 = [""] * 46
    mock_source_row_1[0] = "2001" # ID (sr[0] is not mapped as id, sr[3] is)
    mock_source_row_1[1] = "CP"
    mock_source_row_1[3] = "2001" # ID (sr[3] is mapped as id)
    mock_source_row_1[4] = "Căn Cách Mạng Tháng Tám Quận 3 VIP"
    mock_source_row_1[5] = "100"
    mock_source_row_1[8] = "8.5"
    mock_source_row_1[9] = "Q3"
    mock_source_row_1[10] = "Phường 11"
    mock_source_row_1[19] = "Mô tả chi tiết CMT8 Q3 VIP..." # Description
    mock_source_row_1[37] = "SYS-1001" # system_id

    mock_pool_row_1 = [""] * 96
    mock_pool_row_1[0] = "2001"
    mock_pool_row_1[5] = "Cách Mạng Tháng Tám"
    mock_pool_row_1[6] = "123"
    mock_pool_row_1[9] = "Nội dung chính CMT8 Q3 VIP"
    mock_pool_row_1[10] = "Mô tả chi tiết CMT8 Q3 VIP"
    mock_pool_row_1[11] = "8.5"
    mock_pool_row_1[13] = "100"
    mock_pool_row_1[27] = "https://res.cloudinary.com/demo/image/upload/sodo1_123.jpg"
    mock_pool_row_1[28] = "https://res.cloudinary.com/demo/image/upload/sodo2_123.jpg"
    mock_pool_row_1[29] = "https://res.cloudinary.com/demo/image/upload/mat_tien_123.jpg"
    mock_pool_row_1[40] = "https://res.cloudinary.com/demo/image/upload/interior_1.jpg"
    mock_pool_row_1[55] = "2001"
    mock_pool_row_1[72] = "SYS-1001"

    # Define public mock data for the fallback client GViz call
    mock_public_row = [None] * 45
    mock_public_row[0] = {"v": "2001"}
    mock_public_row[1] = {"v": "Căn Cách Mạng Tháng Tám Quận 3 VIP"}
    mock_public_row[2] = {"v": 100}
    mock_public_row[3] = {"v": 4}
    mock_public_row[4] = {"v": 5}
    mock_public_row[5] = {"v": 8.5}
    mock_public_row[6] = {"v": "q3"}
    mock_public_row[7] = {"v": "Phường 11"}
    mock_public_row[8] = {"v": "Mặt tiền"}
    mock_public_row[9] = {"v": "Đông Nam"}
    mock_public_row[10] = {"v": 15}
    mock_public_row[11] = {"v": 0}
    mock_public_row[12] = {"v": "Bình thường"}
    mock_public_row[13] = {"v": "Hàng Ngon"}
    mock_public_row[14] = {"v": "Không"}
    mock_public_row[15] = {"v": "Không"}
    mock_public_row[16] = {"v": "Mô tả chi tiết căn nhà CMT8..."}
    mock_public_row[17] = {"v": "https://res.cloudinary.com/demo/image/upload/interior_1.jpg"}
    mock_public_row[34] = {"v": "SYS-1001"}

    console_logs = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Increase viewport height to see the iframe fully expanded
        context = browser.new_context(viewport={"width": 1280, "height": 1300})
        page = context.new_page()
        
        page.on("console", lambda msg: console_logs.append(f"[Main Console {msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: console_logs.append(f"[Main Page Error] {err}"))
        page.on("requestfailed", lambda req: console_logs.append(f"[Request Failed] {req.url} - {req.failure}"))
        
        # Inject admin credentials
        page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
        """)
        
        # Mock Sheets API returning the published listing
        def handle_sheets(route):
            url = route.request.url
            if "Source" in url:
                route.fulfill(content_type="application/json", body=json.dumps({"values": [source_headers, mock_source_row_1]}))
            else:
                route.fulfill(content_type="application/json", body=json.dumps({"values": [pool_headers, mock_pool_row_1]}))
        
        def handle_public_gviz(route):
            mock_data = {
                "version": "0.6",
                "status": "ok",
                "table": {
                    "cols": [],
                    "rows": [{"c": mock_public_row}]
                }
            }
            mock_jsonp = f"__gsCallback({json.dumps(mock_data)});"
            route.fulfill(content_type="application/javascript", body=mock_jsonp)

        page.route(lambda url: "spreadsheets" in url and "values" in url, handle_sheets)
        page.route("**/gviz/tq**", handle_public_gviz)
        page.route("**/maps.google.com/**", lambda route: route.fulfill(status=200, body="<html>Dummy Maps</html>"))
        page.route("**/res.cloudinary.com/**", lambda route: route.fulfill(status=200, body="Dummy Image"))
        
        try:
            page.goto(target_url, wait_until="load", timeout=30000)
            page.wait_for_function("window.isSecureLoaded === true", timeout=10000)
            
            # Print parsed data listing array length
            data_len = page.evaluate("DATA.length")
            print(f"Parsed DATA array length: {data_len}")
            
            # Open curation drawer for the published listing
            print("Opening curation drawer for published SYS-1001 listing...")
            page.evaluate("openS('2001')")
            
            # Wait for preview accordion element
            page.wait_for_selector("#accPreview", timeout=5000)
            
            # Print HTML inside #accPreview to see what is generated
            html_content = page.locator("#accPreview").inner_html()
            print("HTML of #accPreview:", html_content)
            
            # Click Preview header to expand the accordion and render the iframe
            print("Expanding Preview accordion header...")
            page.locator("#accPreview .accordion-header").click()
            
            # Wait for the iframe element to appear in DOM
            print("Waiting for iframe element...")
            page.wait_for_selector("#accPreview iframe", timeout=5000)
            
            # Give the iframe 4 seconds to boot up and fetch details from parent memory
            print("Waiting for iframe client webpage to render details...")
            time.sleep(4.0)
            
            # Take a screenshot showing the curation drawer with the active client webpage inside the iframe
            screenshot_path = os.path.join(artifacts_dir, "admin_iframe_curation_view.png")
            page.screenshot(path=screenshot_path)
            print(f"Iframe Curation View screenshot saved to: {screenshot_path}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            print("\n=== CONSOLE LOGS ===")
            for log in console_logs:
                print(log)
            print("====================\n")
            browser.close()

if __name__ == "__main__":
    main()
