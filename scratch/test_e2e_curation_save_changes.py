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
    assets_dir = os.path.join(project_dir, "docs/workflows/assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    
    time.sleep(1.5) # Allow server to bind
    
    test_success = True
    
    # ── Define Mock Data for Client View ──
    mock_public_row_1 = [None] * 45
    mock_public_row_1[0] = {"v": "1002"} # id
    mock_public_row_1[1] = {"v": "Căn Ba Tháng Hai Q10"} # t
    mock_public_row_1[2] = {"v": 100} # dt
    mock_public_row_1[3] = {"v": 4} # tang
    mock_public_row_1[4] = {"v": 5} # mat
    mock_public_row_1[5] = {"v": 12.0} # gia
    mock_public_row_1[6] = {"v": "q10"} # q
    mock_public_row_1[7] = {"v": "Phường 12"} # phuong
    mock_public_row_1[8] = {"v": "Mặt tiền"} # loai_hinh
    mock_public_row_1[9] = {"v": "Đông Nam"} # huong
    mock_public_row_1[10] = {"v": 15} # duong_truoc_nha
    mock_public_row_1[11] = {"v": 0} # rong_hem
    mock_public_row_1[12] = {"v": "Bình thường"} # tinh_trang
    mock_public_row_1[13] = {"v": ""} # danh_gia
    mock_public_row_1[14] = {"v": "Không"} # ngu_tang_tret
    mock_public_row_1[15] = {"v": "Không"} # chdv
    mock_public_row_1[16] = {"v": "Mô tả chi tiết căn Ba Tháng Hai..."} # m
    mock_public_row_1[17] = {"v": "https://res.cloudinary.com/demo/image/upload/sample.jpg"} # img 1
    mock_public_row_1[34] = {"v": "SYS-1002"} # system_id
    mock_public_row_1[35] = {"v": "https://res.cloudinary.com/demo/image/upload/mat_tien_123.jpg"} # img_mat_tien

    # ── Define Mock Data for Admin View ──
    mock_source_row_2 = [""] * 47
    mock_source_row_2[0] = "1"
    mock_source_row_2[1] = "CP"
    mock_source_row_2[3] = "SYS-1002" # system_id
    mock_source_row_2[4] = "Căn Ba Tháng Hai Q10"
    mock_source_row_2[5] = "100"
    mock_source_row_2[8] = "12.0"
    mock_source_row_2[9] = "Q10"
    mock_source_row_2[10] = "Phường 12"
    mock_source_row_2[37] = "SYS-1002"
    mock_source_row_2[38] = "https://res.cloudinary.com/demo/image/upload/mat_tien_123.jpg"

    mock_pool_row_2 = [""] * 96
    mock_pool_row_2[0] = "2002"
    mock_pool_row_2[5] = "Ba Tháng Hai"
    mock_pool_row_2[6] = "456"
    mock_pool_row_2[9] = "Nội dung chính Ba Tháng Hai Q10"
    mock_pool_row_2[10] = "Mô tả chi tiết Ba Tháng Hai Q10"
    mock_pool_row_2[11] = "11.5"
    mock_pool_row_2[13] = "100"
    mock_pool_row_2[27] = "https://res.cloudinary.com/demo/image/upload/sodo1_456.jpg"
    mock_pool_row_2[28] = "https://res.cloudinary.com/demo/image/upload/sodo2_456.jpg"
    mock_pool_row_2[29] = "https://res.cloudinary.com/demo/image/upload/mat_tien_123.jpg"
    mock_pool_row_2[40] = "https://res.cloudinary.com/demo/image/upload/interior_1.jpg"
    mock_pool_row_2[55] = "2002"
    mock_pool_row_2[72] = "SYS-1002"

    console_errors = []
    captured_sheets_calls = []

    def handle_public_gviz(route):
        mock_data = {
            "version": "0.6",
            "status": "ok",
            "table": {
                "cols": [],
                "rows": [
                    {"c": mock_public_row_1}
                ]
            }
        }
        mock_jsonp = f"__gsCallback({json.dumps(mock_data)});"
        route.fulfill(content_type="application/javascript", body=mock_jsonp)

    is_headed = "--headed" in sys.argv
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=not is_headed)
        
        # --- DESKTOP VIEWPORT TEST (1280x800) ---
        print("\n--- Running Desktop Curation Save Changes Test (1280x800) ---")
        admin_context = browser.new_context(viewport={"width": 1280, "height": 800})
        admin_page = admin_context.new_page()
        
        admin_page.on("dialog", lambda dialog: dialog.accept())
        admin_page.on("console", lambda msg: (
            print(f"[Admin Console {msg.type}] {msg.text}"),
            console_errors.append(msg.text) if msg.type == "error" else None
        ))
        admin_page.on("pageerror", lambda err: (
            print(f"[Admin Page Error] {err}"),
            console_errors.append(str(err))
        ))
        
        # Inject admin session
        admin_page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
        """)
        
        # Intercept and mock Admin Sheets API
        def handle_admin_sheets(route):
            url = route.request.url
            method = route.request.method
            print(f"[Sheets Mock API] Intercepted {method} {url}")
            
            if method == "GET":
                if "Source" in url:
                    response_body = {"values": [["header_row"] * 46, mock_source_row_2]}
                else:
                    response_body = {"values": [["header_row"] * 96, mock_pool_row_2]}
                route.fulfill(content_type="application/json", body=json.dumps(response_body))
            elif method in ("PUT", "POST"):
                payload = route.request.post_data_json
                print(f"[Sheets Mock API] Captured writing request payload: {payload}")
                captured_sheets_calls.append(payload)
                route.fulfill(content_type="application/json", body=json.dumps({"updatedRange": "Source!A4:AU4"}))
        
        admin_page.route(lambda url: "spreadsheets" in url and "values" in url, handle_admin_sheets)
        admin_page.route("**/gviz/tq**", handle_public_gviz)
        admin_page.route("**/maps.google.com/**", lambda route: route.fulfill(status=200, body="<html>Dummy Maps</html>"))
        admin_page.route("**/res.cloudinary.com/**", lambda route: route.fulfill(status=200, body="Dummy Image"))
        
        try:
            admin_url = f"http://localhost:{port}/index.html"
            print(f"Navigating admin page to: {admin_url}")
            admin_page.goto(admin_url, wait_until="load", timeout=30000)
            
            # Wait for data to load
            admin_page.wait_for_function("window.isSecureLoaded === true", timeout=10000)
            print("Curation pool cards count:", admin_page.locator(".card").count())
            
            # Click on the card to open detail view (curated listing view)
            print("Opening detail view for listing #SYS-1002...")
            admin_page.locator(".card").first.click()
            
            # Wait for Curation editor accordion to be attached and expand it
            admin_page.wait_for_selector("#accSource", timeout=5000)
            admin_page.locator("#accSource .accordion-header").click()
            
            # Wait for fields to load
            admin_page.wait_for_selector("#editTieuDeBds", timeout=5000, state="attached")
            
            # Modify note field to trigger a save
            print("Modifying note and title fields...")
            admin_page.locator("#editNote").fill("Ghi chú mới từ E2E test", force=True)
            admin_page.locator("#editTieuDeBds").fill("Căn Ba Tháng Hai Q10 - Sửa từ E2E test", force=True)
            
            # Click dial main button to expand actions
            print("Expanding admin speed dial...")
            admin_page.locator("#dialMainBtn").click()
            admin_page.wait_for_timeout(300)
            
            # Find and click save button
            print("Clicking save changes button...")
            save_btn = admin_page.locator("#saveSourceBtn")
            save_btn.click()
            
            # Wait for Sheets API PUT request to be completed
            admin_page.wait_for_timeout(2000)
            
            # Check for console errors or red toast
            print("Verifying if any error toast is shown...")
            toast = admin_page.locator(".toast.error")
            if toast.is_visible():
                toast_text = toast.inner_text()
                print(f"[ERROR] Error toast is visible: {toast_text}")
                test_success = False
            else:
                print("[SUCCESS] No error toast shown. Save succeeded!")

            # Verify that no console errors containing 'img_mat_tien' or 'undefined' were thrown
            for err in console_errors:
                if "img_mat_tien" in err or "undefined" in err:
                    print(f"[ERROR] Console error detected: {err}")
                    test_success = False
            
            # Save Desktop Screenshot
            screenshot_path = os.path.join(assets_dir, "US-108_desktop.png")
            admin_page.screenshot(path=screenshot_path)
            print(f"Desktop curation save changes screenshot saved to {screenshot_path}")
            
        except Exception as e:
            print(f"[ERROR] Desktop Curation Save Flow Failed: {e}")
            test_success = False
        finally:
            admin_context.close()

        # --- MOBILE VIEWPORT TEST (375x812) ---
        print("\n--- Running Mobile Curation Save Changes Test (375x812) ---")
        mobile_context = browser.new_context(
            viewport={"width": 375, "height": 812},
            has_touch=True,
            is_mobile=True
        )
        mobile_page = mobile_context.new_page()
        
        mobile_page.on("dialog", lambda dialog: dialog.accept())
        mobile_page.on("console", lambda msg: (
            print(f"[Mobile Console {msg.type}] {msg.text}"),
            console_errors.append(msg.text) if msg.type == "error" else None
        ))
        
        # Inject admin session
        mobile_page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
        """)
        
        mobile_page.route(lambda url: "spreadsheets" in url and "values" in url, handle_admin_sheets)
        mobile_page.route("**/gviz/tq**", handle_public_gviz)
        mobile_page.route("**/maps.google.com/**", lambda route: route.fulfill(status=200, body="<html>Dummy Maps</html>"))
        mobile_page.route("**/res.cloudinary.com/**", lambda route: route.fulfill(status=200, body="Dummy Image"))
        
        try:
            print(f"Navigating mobile page to: {admin_url}")
            mobile_page.goto(admin_url, wait_until="load", timeout=30000)
            
            # Wait for data to load
            mobile_page.wait_for_function("window.isSecureLoaded === true", timeout=10000)
            
            # Open detail view
            print("Opening detail view for listing #SYS-1002 on mobile...")
            mobile_page.locator(".card").first.click()
            
            mobile_page.wait_for_selector("#accSource", timeout=5000)
            mobile_page.locator("#accSource .accordion-header").click()
            mobile_page.wait_for_selector("#editTieuDeBds", timeout=5000, state="attached")
            
            # Save Mobile Screenshot
            screenshot_path = os.path.join(assets_dir, "US-108_mobile.png")
            mobile_page.screenshot(path=screenshot_path)
            print(f"Mobile Curation save changes screenshot saved to {screenshot_path}")
            
        except Exception as e:
            print(f"[ERROR] Mobile Curation Flow Failed: {e}")
            test_success = False
        finally:
            mobile_context.close()
            
        browser.close()
        
    if test_success:
        print("\n[🎉 ALL US-108 E2E TESTS PASSED SUCCESSFULLY]")
        sys.exit(0)
    else:
        print("\n[❌ SOME US-108 E2E TESTS FAILED]")
        sys.exit(1)

if __name__ == "__main__":
    main()
