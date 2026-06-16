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
    
    time.sleep(1.5) # Allow server to bind
    
    # Define Mock Data
    mock_public_row_1 = [None] * 45
    mock_public_row_1[0] = {"v": "1001"} # id
    mock_public_row_1[1] = {"v": "Căn CMT8 Q3 VIP"} # t
    mock_public_row_1[2] = {"v": 100} # dt
    mock_public_row_1[3] = {"v": 4} # tang
    mock_public_row_1[4] = {"v": 5} # mat
    mock_public_row_1[5] = {"v": 8.5} # gia
    mock_public_row_1[6] = {"v": "q3"} # q
    mock_public_row_1[7] = {"v": "Phường 11"} # phuong
    mock_public_row_1[8] = {"v": "Mặt tiền"} # loai_hinh
    mock_public_row_1[9] = {"v": "Đông Nam"} # huong
    mock_public_row_1[10] = {"v": 15} # duong_truoc_nha
    mock_public_row_1[11] = {"v": 0} # rong_hem
    mock_public_row_1[12] = {"v": "Bình thường"} # tinh_trang
    mock_public_row_1[13] = {"v": "Hàng Ngon"} # danh_gia
    mock_public_row_1[14] = {"v": "Không"} # ngu_tang_tret
    mock_public_row_1[15] = {"v": "Không"} # chdv
    mock_public_row_1[16] = {"v": "Mô tả chi tiết căn nhà CMT8..."} # m
    mock_public_row_1[17] = {"v": "https://res.cloudinary.com/demo/image/upload/sample.jpg"} # img 1
    mock_public_row_1[34] = {"v": "SYS-1001"} # system_id

    mock_source_row_1 = [""] * 46
    mock_source_row_1[0] = "1"
    mock_source_row_1[1] = "CP"
    mock_source_row_1[3] = "SYS-1001" # system_id
    mock_source_row_1[4] = "Căn CMT8 Q3 VIP"
    mock_source_row_1[5] = "100"
    mock_source_row_1[8] = "8.5"
    mock_source_row_1[9] = "Q3"
    mock_source_row_1[10] = "Phường 11"
    mock_source_row_1[37] = "SYS-1001"

    mock_pool_row_1 = [""] * 96
    mock_pool_row_1[5] = "CMT8"
    mock_pool_row_1[6] = "123"
    mock_pool_row_1[9] = "Nội dung chính CMT8 Q3"
    mock_pool_row_1[10] = "Mô tả chi tiết CMT8 Q3"
    mock_pool_row_1[11] = "6.5"
    mock_pool_row_1[13] = "100"
    mock_pool_row_1[40] = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
    mock_pool_row_1[55] = "2001"
    mock_pool_row_1[72] = "SYS-1001"

    console_errors = []
    test_success = True

    def handle_public_gviz(route):
        mock_data = {
            "version": "0.6",
            "status": "ok",
            "table": {
                "cols": [],
                "rows": [{"c": mock_public_row_1}]
            }
        }
        mock_jsonp = f"__gsCallback({json.dumps(mock_data)});"
        route.fulfill(content_type="application/javascript", body=mock_jsonp)

    def handle_admin_sheets(route):
        url = route.request.url
        if "Source" in url:
            response_body = {"values": [["header_row"] * 46, mock_source_row_1]}
        else:
            response_body = {"values": [mock_pool_row_1]}
        route.fulfill(content_type="application/json", body=json.dumps(response_body))

    with sync_playwright() as p:
        print("Launching headless browser...")
        browser = p.chromium.launch(headless=True)
        admin_context = browser.new_context(viewport={"width": 1280, "height": 800})
        
        # Grant clipboard access
        admin_context.grant_permissions(["clipboard-read", "clipboard-write"])
        
        admin_page = admin_context.new_page()
        
        admin_page.on("console", lambda msg: (
            print(f"[Console {msg.type}] {msg.text}"),
            console_errors.append(msg.text) if msg.type == "error" else None
        ))
        admin_page.on("requestfailed", lambda req: print(f"[Request Failed] {req.url} - {req.failure}"))
        
        # Inject isAdminSession
        admin_page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
            // Mock alert and confirm to avoid dialog block
            window.alert = function(msg) { console.log("ALERT DIALOG: " + msg); };
            window.confirm = function(msg) { console.log("CONFIRM DIALOG: " + msg); return true; };
        """)
        
        admin_page.route(lambda url: "spreadsheets" in url and "values" in url, handle_admin_sheets)
        admin_page.route("**/gviz/tq**", handle_public_gviz)
        
        admin_url = f"http://localhost:{port}/index.html"
        try:
            print(f"Navigating admin page to: {admin_url}")
            admin_page.goto(admin_url, wait_until="load", timeout=30000)
            
            # Wait for secure loading
            print("Waiting for secure loaded status...")
            admin_page.wait_for_function("window.isSecureLoaded === true", timeout=10000)
            
            # Wait for card
            admin_page.wait_for_selector(".card", timeout=10000)
            print("Card loaded. Selecting card...")
            admin_page.locator(".card-sel").first.check(force=True)
            
            # Open Speed dial
            print("Opening speed dial menu...")
            admin_page.locator("#dialMainBtn").click()
            admin_page.wait_for_selector("#dialActions.open", timeout=5000)
            admin_page.wait_for_timeout(350) # wait for transition
            
            # Click share button
            print("Clicking share button...")
            admin_page.locator(".share-btn-float").click()
            admin_page.wait_for_selector("#linkModal.open", timeout=5000)
            print("Share link modal is open successfully.")
            
            # Click quick share link button
            print("Clicking '⚡ Tạo Link Công Khai Nhanh' button...")
            admin_page.locator("text=⚡ Tạo Link Công Khai Nhanh").click()
            
            # Wait for modal to close
            print("Waiting for share link modal to close...")
            admin_page.wait_for_selector("#linkModal", state="hidden", timeout=5000)
            print("Modal closed successfully.")
            
            # Wait a small delay to capture any console errors that might have been fired asynchronously
            time.sleep(1)
            
            # Check for console errors
            if len(console_errors) > 0:
                print(f"❌ Test FAILED: Console errors detected during test: {console_errors}")
                test_success = False
            else:
                print("✅ Test PASSED: Quick link generated and modal closed without console errors!")
                
        except Exception as e:
            print(f"❌ Test FAILED with exception: {e}")
            test_success = False
        finally:
            browser.close()
            
    if not test_success:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
