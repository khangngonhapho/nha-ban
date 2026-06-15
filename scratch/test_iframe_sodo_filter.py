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
    print(f"Local test server started on port {port}")
    server.serve_forever()
    return server

def main():
    project_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
    artifacts_dir = r"C:\Users\Khang Ngo\.gemini\antigravity\brain\595fc691-aac4-4d6b-9257-a1e94612755c"
    
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    
    time.sleep(1.5)
    
    test_success = True
    
    # Mock Sheets data matching the curation page setup
    mock_source_row = [""] * 46
    mock_source_row[0] = "1"
    mock_source_row[1] = "CP"
    mock_source_row[3] = "SYS-1001"
    mock_source_row[4] = "Căn CMT8 Q3 VIP"
    mock_source_row[5] = "100"
    mock_source_row[8] = "8.5"
    mock_source_row[9] = "Q3"
    mock_source_row[10] = "Phường 11"
    mock_source_row[37] = "SYS-1001"

    mock_pool_row = [""] * 96
    mock_pool_row[0] = "2001"
    mock_pool_row[5] = "Cách Mạng Tháng Tám"
    mock_pool_row[6] = "123"
    mock_pool_row[9] = "Nội dung chính CMT8 Q3 VIP"
    mock_pool_row[10] = "Mô tả chi tiết CMT8 Q3 VIP"
    mock_pool_row[11] = "6.5"
    mock_pool_row[13] = "100"
    # Sodo images
    mock_pool_row[27] = "https://res.cloudinary.com/demo/image/upload/sodo1_123.jpg"
    mock_pool_row[28] = "https://res.cloudinary.com/demo/image/upload/sodo2_123.jpg"
    mock_pool_row[29] = "https://res.cloudinary.com/demo/image/upload/mat_tien_123.jpg" # Facade
    mock_pool_row[40] = "https://res.cloudinary.com/demo/image/upload/interior_1.jpg" # Interior 1
    mock_pool_row[41] = "https://res.cloudinary.com/demo/image/upload/interior_2.jpg" # Interior 2
    mock_pool_row[55] = "2001"
    mock_pool_row[72] = "SYS-1001"

    def handle_admin_sheets(route):
        url = route.request.url
        if "Source" in url:
            route.fulfill(content_type="application/json", body=json.dumps({"values": [[""] * 46, mock_source_row]}))
        elif "Pool" in url:
            route.fulfill(content_type="application/json", body=json.dumps({"values": [[""] * 96, mock_pool_row]}))
        else:
            route.fulfill(status=404)

    def handle_public_gviz(route):
        mock_public_row = [None] * 45
        mock_public_row[0] = {"v": "1001"}
        mock_public_row[1] = {"v": "Căn CMT8 Q3 VIP"}
        mock_public_row[2] = {"v": 100}
        mock_public_row[5] = {"v": 8.5}
        mock_public_row[6] = {"v": "q3"}
        mock_public_row[7] = {"v": "Phường 11"}
        mock_public_row[34] = {"v": "SYS-1001"}
        
        mock_data = {
            "version": "0.6",
            "status": "ok",
            "table": {"cols": [], "rows": [{"c": mock_public_row}]}
        }
        route.fulfill(content_type="application/javascript", body=f"__gsCallback({json.dumps(mock_data)});")

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        admin_context = browser.new_context(viewport={"width": 1280, "height": 800})
        admin_page = admin_context.new_page()
        
        admin_page.on("console", lambda msg: print(f"[Console {msg.type}] {msg.text}"))
        admin_page.on("pageerror", lambda err: print(f"[Page Error] {err}"))
        
        admin_page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
        """)
        
        admin_page.route(lambda url: "spreadsheets" in url and "values" in url, handle_admin_sheets)
        admin_page.route("**/gviz/tq**", handle_public_gviz)
        admin_page.route("**/maps.google.com/**", lambda route: route.fulfill(status=200, body="<html>Dummy Maps</html>"))
        admin_page.route("**/res.cloudinary.com/**", lambda route: route.fulfill(status=200, body="Dummy Image"))

        admin_url = f"http://localhost:{port}/index.html"
        
        try:
            print(f"Navigating to: {admin_url}")
            admin_page.goto(admin_url, wait_until="load", timeout=30000)
            admin_page.wait_for_function("window.isSecureLoaded === true", timeout=10000)
            
            # Open pool listing
            print("Opening pool curation drawer for SYS-1001...")
            admin_page.evaluate("openPoolS('SYS-1001')")
            
            # Verify Curation panels exist
            admin_page.wait_for_selector("#accSource", timeout=5000)
            admin_page.wait_for_selector("#accPreview", timeout=5000)
            
            # Expand the editing accordion to make inputs editable
            admin_page.locator("#accSource .accordion-header").click()
            admin_page.wait_for_timeout(500)
            
            # Expose cover image and sodo values in inputs
            print("Updating inputs with custom sodo and cover images...")
            admin_page.evaluate("""
                document.getElementById('editCoverImgUrl').value = 'https://res.cloudinary.com/demo/image/upload/custom_facade_file.jpg';
                document.getElementById('editSodo3Url').value = 'https://res.cloudinary.com/demo/image/upload/custom_sodo_file.jpg';
            """)
            admin_page.fill("#editTieuDeBds", "Căn VIP CMT8 Test")
            admin_page.fill("#editMoTaBds", "Mô tả chi tiết test...")
            admin_page.wait_for_timeout(500)
            
            # Expand Client Preview accordion
            print("Expanding Preview accordion...")
            admin_page.locator("#accPreview .accordion-header").click()
            admin_page.wait_for_timeout(1000)
            
            # Check the iframe's content
            print("Accessing iframe...")
            iframe = admin_page.frame_locator("#accPreview iframe")
            
            # Wait for the client detail page to render inside iframe
            iframe.locator("#carouselClientDetail").wait_for(timeout=5000)
            
            # Get the images loaded in the customer preview carousel
            carousel_imgs = iframe.locator("#carouselClientDetail img")
            img_srcs = [carousel_imgs.nth(i).get_attribute("src") for i in range(carousel_imgs.count())]
            print(f"Iframe Carousel Images: {img_srcs}")
            
            # ASSERTIONS
            print("Verifying no sodo or facade images are present in the carousel...")
            for src in img_srcs:
                assert "custom_sodo_file.jpg" not in src, "Error: Sodo image must be filtered out!"
                assert "sodo1_123.jpg" not in src, "Error: Default Sodo 1 image must be filtered out!"
                assert "sodo2_123.jpg" not in src, "Error: Default Sodo 2 image must be filtered out!"
                assert "custom_facade_file.jpg" not in src, "Error: Custom Facade image must be filtered out!"
                assert "mat_tien_123.jpg" not in src, "Error: Default Facade image must be filtered out!"
            
            # Ensure the allowed interior image is present
            interior_present = any("interior_1.jpg" in src for src in img_srcs)
            assert interior_present, "Interior image should be present in customer view!"
            
            print("[🎉 SUCCESS] Custom sodo and facade images are correctly filtered out from Customer Preview!")
            
        except Exception as e:
            print(f"[FAIL] Iframe Sodo Filter E2E Test Failed: {e}")
            test_success = False
            admin_page.screenshot(path=os.path.join(artifacts_dir, "iframe_filter_error.png"))
        finally:
            admin_context.close()
            browser.close()
            
    if test_success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
