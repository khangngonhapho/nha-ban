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
    artifacts_dir = r"C:\Users\Khang Ngo\.gemini\antigravity\brain\c3d4a7c9-e9b6-4f67-9c0a-da95771787dc"
    
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    
    time.sleep(1.5) # Allow server to bind
    
    test_success = True
    
    # Define Mock Data Rows
    mock_public_row = [None] * 45
    mock_public_row[0] = {"v": "1001"} # id
    mock_public_row[1] = {"v": "Nhà đẹp CMT8 Quận 3"} # t
    mock_public_row[2] = {"v": 100} # dt
    mock_public_row[3] = {"v": 4} # tang
    mock_public_row[4] = {"v": 5} # mat
    mock_public_row[5] = {"v": 15} # gia
    mock_public_row[6] = {"v": "Q3"} # q
    mock_public_row[7] = {"v": "Phường 11"} # phuong
    mock_public_row[8] = {"v": "Mặt tiền"} # loai_hinh
    mock_public_row[9] = {"v": "Đông Nam"} # huong
    mock_public_row[10] = {"v": 15} # duong_truoc_nha
    mock_public_row[11] = {"v": 0} # rong_hem
    mock_public_row[12] = {"v": "Bình thường"} # tinh_trang
    mock_public_row[13] = {"v": "Hàng Ngon"} # danh_gia
    mock_public_row[14] = {"v": "Không"} # ngu_tang_tret
    mock_public_row[15] = {"v": "Không"} # chdv
    mock_public_row[16] = {"v": "Mô tả chi tiết căn nhà CMT8..."} # m
    mock_public_row[17] = {"v": "https://res.cloudinary.com/demo/image/upload/sample.jpg"} # img 1
    mock_public_row[18] = {"v": "https://res.cloudinary.com/demo/image/upload/sample2.jpg"} # img 2
    mock_public_row[34] = {"v": "1001"} # system_id

    # Admin Sheet Mock Values
    # Source Columns size must match or exceed 45
    mock_source_cols = [""] * 46
    mock_source_cols[0] = "1"
    mock_source_cols[1] = "CP"
    mock_source_cols[3] = "1001"
    mock_source_cols[4] = "Nhà đẹp CMT8 Quận 3"
    mock_source_cols[5] = "100"
    mock_source_cols[6] = "4"
    mock_source_cols[7] = "5"
    mock_source_cols[8] = "15"
    mock_source_cols[9] = "Q3"
    mock_source_cols[10] = "Phường 11"
    mock_source_cols[11] = "Mặt tiền"
    mock_source_cols[12] = "Đông Nam"
    mock_source_cols[13] = "15"
    mock_source_cols[14] = "0"
    mock_source_cols[15] = "Bình thường"
    mock_source_cols[16] = "Hàng Ngon"
    mock_source_cols[20] = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
    mock_source_cols[21] = "https://res.cloudinary.com/demo/image/upload/sample2.jpg"
    mock_source_cols[34] = "Đường CMT8"
    mock_source_cols[37] = "1001"
    mock_source_cols[38] = "https://res.cloudinary.com/demo/image/upload/sample.jpg"

    # Pool columns size must match or exceed 95
    mock_pool_cols = [""] * 96
    mock_pool_cols[5] = "CMT8"
    mock_pool_cols[6] = "123"
    mock_pool_cols[9] = "Nội dung chính Admin"
    mock_pool_cols[10] = "Mô tả chi tiết Admin"
    mock_pool_cols[13] = "100"
    mock_pool_cols[14] = "95"
    mock_pool_cols[27] = "https://res.cloudinary.com/demo/image/upload/sodo1.jpg"
    mock_pool_cols[28] = "https://res.cloudinary.com/demo/image/upload/sodo2.jpg"
    mock_pool_cols[40] = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
    mock_pool_cols[41] = "https://res.cloudinary.com/demo/image/upload/sample2.jpg"
    mock_pool_cols[55] = "1001"
    mock_pool_cols[72] = "1001"
    mock_pool_cols[74] = "0901234567"
    mock_pool_cols[75] = "Đầu chủ A"
    mock_pool_cols[76] = "fb.com"
    mock_pool_cols[80] = "https://res.cloudinary.com/demo/image/upload/sodo3.jpg"
    mock_pool_cols[81] = "https://res.cloudinary.com/demo/image/upload/sodo4.jpg"
    mock_pool_cols[82] = "https://res.cloudinary.com/demo/image/upload/sodo5.jpg"

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        
        # ==========================================
        # 1. CLIENT DETAIL VIEW TEST
        # ==========================================
        print("\n--- Running Client Detail View E2E Test ---")
        client_context = browser.new_context(viewport={"width": 1280, "height": 800})
        client_page = client_context.new_page()
        
        client_page.on("console", lambda msg: print(f"[Client Console {msg.type}] {msg.text}"))
        client_page.on("pageerror", lambda err: print(f"[Client Page Error] {err}"))
        
        # Inject client name & phone to bypass lead capture modal
        client_page.add_init_script("""
            localStorage.setItem('client_name', 'Test Customer');
            localStorage.setItem('client_phone', '0901234567');
        """)
        
        # Intercept and mock public Sheets JSONP
        def handle_public_gviz(route):
            print("[Client] Intercepted public GViz request, returning mock JSONP...")
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

        def handle_api_config(route):
            mock_config = {
                "status": "success",
                "config": {
                    "sheet_id": "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw",
                    "active_pool_system": "Pool1",
                    "json_ui_filters": [],
                    "json_ui_fields": []
                }
            }
            route.fulfill(content_type="application/json", body=json.dumps(mock_config))

        client_page.route("**/gviz/tq**", handle_public_gviz)
        client_page.route("**/api/config**", handle_api_config)
        
        # Pass s=1 to select the first element in mock_public_row
        client_url = f"http://localhost:{port}/index.html?s=1"
        try:
            print(f"Navigating client page to: {client_url}")
            client_page.goto(client_url, wait_until="load", timeout=30000)
            
            print("Waiting for cards to load...")
            client_page.wait_for_selector(".card", timeout=10000)
            card_count = client_page.locator(".card").count()
            print(f"Found {card_count} listing cards in client view.")
            
            # Click card
            print("Clicking card...")
            client_page.locator(".card").first.click()
            
            # Verify detail modal
            print("Waiting for detail modal (#ov) to open...")
            client_page.wait_for_selector("#ov.open", timeout=5000)
            print("Detail modal opened successfully.")
            
            # Verify detail carousel is populated
            print("Checking client carousel (#carouselClientDetail)...")
            client_page.wait_for_selector("#carouselClientDetail", timeout=5000)
            carousel_items = client_page.locator("#carouselClientDetail .admin-carousel-item")
            carousel_count = carousel_items.count()
            print(f"Client detail carousel has {carousel_count} images.")
            assert carousel_count > 0, "Carousel images not found in client modal!"
            
            # Click image to open Lightbox
            print("Clicking first image in carousel to open Lightbox...")
            carousel_items.first.click()
            
            # Verify Lightbox opens
            client_page.wait_for_selector("#lbOverlay.open", timeout=5000)
            print("Lightbox opened successfully in client view.")
            
            # Close Lightbox (Wait for class removal since opacity:0 is still visible in DOM layout)
            print("Closing Lightbox...")
            client_page.locator(".lb-close").click()
            client_page.wait_for_selector("#lbOverlay:not(.open)", timeout=5000)
            print("Lightbox closed successfully.")
            
            # Close detail modal (Wait for display:none via state="hidden")
            print("Closing detail modal...")
            client_page.locator(".xbtn").click()
            client_page.wait_for_selector("#ov", state="hidden", timeout=5000)
            print("Detail modal closed successfully in client view.")
            
        except Exception as e:
            print(f"[ERROR] Client Modal Test Failed: {e}")
            test_success = False
            client_page.screenshot(path=os.path.join(artifacts_dir, "client_error.png"))
        finally:
            client_context.close()

        # ==========================================
        # 2. ADMIN DETAIL VIEW TEST
        # ==========================================
        print("\n--- Running Admin Detail View E2E Test ---")
        admin_context = browser.new_context(viewport={"width": 1280, "height": 800})
        admin_page = admin_context.new_page()
        
        # Inject isAdminSession & active tokens to localStorage
        admin_page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
        """)
        
        # Intercept and mock Admin Sheets API v4 endpoints
        def handle_admin_sheets(route):
            url = route.request.url
            print(f"[Admin API] Intercepted request to: {url}")
            if "Source" in url:
                # Return Source sheet rows
                response_body = {"values": [["header_row"] * 46, mock_source_cols]}
            else:
                # Return Pool sheet rows
                response_body = {"values": [["header_row"] * 96, mock_pool_cols]}
            route.fulfill(content_type="application/json", body=json.dumps(response_body))

        admin_page.route("**/spreadsheets/**/values/**", handle_admin_sheets)
        
        # Mock public sheets just in case of fallbacks
        admin_page.route("**/gviz/tq**", handle_public_gviz)
        admin_page.route("**/api/config**", handle_api_config)
        
        admin_url = f"http://localhost:{port}/index.html"
        try:
            print(f"Navigating admin page to: {admin_url}")
            admin_page.goto(admin_url, wait_until="load", timeout=30000)
            
            print("Waiting for cards to load...")
            admin_page.wait_for_selector(".card", timeout=10000)
            card_count = admin_page.locator(".card").count()
            print(f"Found {card_count} listing cards in admin view.")
            
            # Click card
            print("Clicking admin card...")
            admin_page.locator(".card").first.click()
            
            # Verify detail modal opens
            print("Waiting for detail modal (#ov) to open...")
            admin_page.wait_for_selector("#ov.open", timeout=5000)
            print("Admin detail modal opened successfully.")
            
            # Verify Admin-specific elements (e.g. quick link bar or Curation info title)
            print("Verifying Admin modal content...")
            admin_page.wait_for_selector(".admin-quick-link-bar", timeout=5000)
            print("Admin quick link bar is present.")
            
            # Check Admin house image carousel (#carouselNha)
            print("Checking admin house image carousel (#carouselNha)...")
            admin_page.wait_for_selector("#carouselNha", timeout=5000)
            nha_items = admin_page.locator("#carouselNha .admin-carousel-item")
            print(f"Admin house carousel has {nha_items.count()} images.")
            assert nha_items.count() > 0, "Admin house carousel has no images!"
            
            # Click first image to open Lightbox
            print("Clicking image in house carousel to open Lightbox...")
            nha_items.first.click()
            
            # Verify Lightbox opens
            admin_page.wait_for_selector("#lbOverlay.open", timeout=5000)
            print("Lightbox opened successfully in admin view.")
            
            # Close Lightbox (Wait for class removal since opacity:0 is still visible in DOM layout)
            print("Closing Lightbox...")
            admin_page.locator(".lb-close").click()
            admin_page.wait_for_selector("#lbOverlay:not(.open)", timeout=5000)
            print("Lightbox closed successfully.")
            
            # Close admin modal (Wait for display:none via state="hidden")
            print("Closing Admin detail modal...")
            admin_page.locator(".xbtn").click()
            admin_page.wait_for_selector("#ov", state="hidden", timeout=5000)
            print("Admin detail modal closed successfully.")
            
        except Exception as e:
            print(f"[ERROR] Admin Modal Test Failed: {e}")
            test_success = False
            admin_page.screenshot(path=os.path.join(artifacts_dir, "admin_error.png"))
        finally:
            admin_context.close()
            
        browser.close()
        
    if test_success:
        print("\n[🎉 ALL MODAL INTERACTION E2E TESTS PASSED SUCCESSFULLY]")
        sys.exit(0)
    else:
        print("\n[❌ E2E MODAL TESTS FAILED]")
        sys.exit(1)

if __name__ == "__main__":
    main()
