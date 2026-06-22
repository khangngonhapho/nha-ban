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
    artifacts_dir = r"C:\Users\Khang Ngo\.gemini\antigravity\brain\98e9c411-d16e-4cb5-a567-0ed9e98b708f"
    
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    
    time.sleep(1.5) # Allow server to bind
    
    test_success = True
    
    # ── Define Mock Data for SQLite APIs ──
    mock_listing = {
        "tk_id": "SYS-1001",
        "Ma_Khang_Ngo_ID": "KN-1001",
        "Tieu_de_Public": "Căn Cách Mạng Tháng Tám Quận 3 VIP",
        "Gia_Public": 8.5,
        "status": "published",
        "Quan": "Q3",
        "Phuong": "Phường 11",
        "Ngo_So_nha": "123",
        "custom_So_Nha": "123 Bis",
        "Duong": "Cách Mạng Tháng Tám",
        "custom_Ten_Duong": "Cách Mạng Tháng Tám",
        "Phuong_cu_AI": "Phường 10",
        "DT_Thuc_te": 100,
        "DT_Tren_so": 98,
        "Mat_Tien": 5.0,
        "Chieu_dai": 20.0,
        "So_Tang": 4,
        "So_phong_ngu": 4,
        "So_nha_ve_sinh": 5,
        "Huong": "Đông Nam",
        "Ngu_tret_Admin": "Không",
        "CHDV_Admin": "Không",
        "Gia_chao": 9.0,
        "Phan_lo_i_Hem": "Xe hơi",
        "Duong_truoc_nha_m": 6,
        "Tinh_trang_nha": "Đẹp ở ngay",
        "Danh_gia_Admin": "Hàng Ngon",
        "Ten_Chu_Nha": "Nguyễn Văn A",
        "Dien_thoai_1": "0901234567",
        "Ten_Dau_Chu": "Đầu Chủ B",
        "Dien_thoai_Dau_Chu": "0987654321",
        "Note_Noi_Bo": "Chủ hợp tác bán nhanh",
        "Phan_loai": "Hàng Ngon",
        "System_ID": "SYS-1001",
        "Ma_Hang": "SYS-1001",
        "Last_Crawl": "2026-06-22",
        "Last_Sync": "2026-06-22",
        "Link_Goc": "https://example.com/sys-1001",
        "images": [
            { "r2_url": "https://res.cloudinary.com/demo/image/upload/sodo.jpg", "role": "sodo" },
            { "r2_url": "https://res.cloudinary.com/demo/image/upload/facade.jpg", "role": "cover" },
            { "r2_url": "https://res.cloudinary.com/demo/image/upload/interior.jpg", "role": "interior" }
        ]
    }
    
    mock_listings_list = {
        "status": "success",
        "listings": [mock_listing]
    }
    
    mock_listings_detail = {
        "status": "success",
        "listing": mock_listing
    }
    
    console_errors = []
    
    is_headed = "--headed" in sys.argv
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=not is_headed)
        
        print("\n--- Running Canvas View E2E Test ---")
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        page.on("dialog", lambda dialog: dialog.accept())
        page.on("console", lambda msg: (
            print(f"[Console {msg.type}] {msg.text}"),
            console_errors.append(msg.text) if msg.type == "error" else None
        ))
        page.on("requestfailed", lambda req: print(f"[Request Failed] {req.url} - {req.failure}"))
        page.on("pageerror", lambda err: print(f"[Page Error] {err}"))
        
        # Intercept listings and details API
        def handle_listings_api(route):
            print(f"[Mock API] Intercepted {route.request.method} {route.request.url}")
            route.fulfill(content_type="application/json", body=json.dumps(mock_listings_list))
            
        def handle_listings_detail_api(route):
            print(f"[Mock API] Intercepted {route.request.method} {route.request.url}")
            route.fulfill(content_type="application/json", body=json.dumps(mock_listings_detail))
            
        page.route("**/api/listings", handle_listings_api)
        page.route("**/api/listings/SYS-1001", handle_listings_detail_api)
        page.route("**/res.cloudinary.com/**", lambda route: route.fulfill(status=200, body="Dummy Image"))
        
        canvas_url = f"http://localhost:{port}/canvas.html"
        try:
            print(f"Navigating to Canvas URL: {canvas_url}")
            page.goto(canvas_url, wait_until="load", timeout=30000)
            
            # Wait for data mode switch and loading (default is SQLite)
            page.wait_for_selector(".listing-card", timeout=10000)
            print("Listing cards loaded in sidebar!")
            
            # Select the mock card
            page.locator(".listing-card").first.click()
            print("Selected first card SYS-1001")
            
            # Verify Canvas dashboard detail elements are populated
            page.wait_for_selector("#view-header-id", timeout=5000)
            header_id = page.locator("#view-header-id").inner_text()
            header_title = page.locator("#view-header-title").inner_text()
            print(f"Loaded details for: {header_id} - {header_title}")
            
            if "KN-1001" not in header_id:
                raise Exception("System ID mismatch in detail header")
                
            # Verify comparing fields
            so_nha_cur = page.locator("#loc-so-nha-cur").inner_text()
            print(f"Verified cur address: {so_nha_cur}")
            if "123 Bis" not in so_nha_cur:
                raise Exception("Address value was not correctly comparison-mapped")
            
            # Click Tab 2: Thư viện hình ảnh
            print("Switching to Image Gallery Tab...")
            page.locator(".detail-tab", has_text="Thư viện hình ảnh").click()
            page.wait_for_selector(".gallery-item", timeout=5000)
            print("Gallery items rendered!")
            
            # Switch to 'sodo' gallery filter
            page.locator("#gallery-tab button", has_text="Sổ đỏ").click()
            page.wait_for_timeout(300)
            
            # Click first sodo image to trigger Lightbox
            page.locator(".gallery-item").first.click()
            page.wait_for_selector("#lightbox-modal", timeout=5000)
            print("Lightbox opened successfully!")
            
            # Click rotate button in lightbox
            page.locator(".lightbox-rotate").click()
            page.wait_for_timeout(200)
            print("Lightbox rotate action triggered.")
            
            # Close Lightbox
            page.locator(".lightbox-close").click()
            page.wait_for_timeout(200)
            
            # Click Tab 3: Chi tiết Pool (Thô)
            print("Switching to Pool Detail Tab...")
            page.locator(".detail-tab", has_text="Chi tiết Pool (Thô)").click()
            page.wait_for_selector("#pool-raw-list .raw-row", timeout=5000)
            
            # Search column filter in Pool Tab
            page.locator("#pool-col-search").fill("dt")
            page.wait_for_timeout(300)
            print("Searched columns with query 'dt'")
            
            # Save Desktop Screenshot
            screenshot_path = os.path.join(artifacts_dir, "canvas_view_desktop.png")
            page.screenshot(path=screenshot_path)
            print(f"Canvas View screenshot saved to {screenshot_path}")
            
        except Exception as e:
            print(f"[ERROR] Canvas View E2E Test Failed: {e}")
            test_success = False
        finally:
            context.close()
            browser.close()
            
    if test_success:
        print("\n[🎉 CANVAS VIEW E2E TEST PASSED SUCCESSFULLY]")
        sys.exit(0)
    else:
        print("\n[❌ CANVAS VIEW E2E TEST FAILED]")
        sys.exit(1)

if __name__ == "__main__":
    main()
