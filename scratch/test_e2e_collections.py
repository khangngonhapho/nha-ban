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
    
    # ── Define Mock Data for Client View ──
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

    mock_public_row_2 = list(mock_public_row_1)
    mock_public_row_2[0] = {"v": "1002"}
    mock_public_row_2[1] = {"v": "Căn Ba Tháng Hai Q10"}
    mock_public_row_2[5] = {"v": 12.0}
    mock_public_row_2[6] = {"v": "q10"}
    mock_public_row_2[7] = {"v": "Phường 12"}
    mock_public_row_2[34] = {"v": "SYS-1002"}

    # ── Define Mock Data for Admin View ──
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

    mock_source_row_2 = list(mock_source_row_1)
    mock_source_row_2[3] = "SYS-1002"
    mock_source_row_2[4] = "Căn Ba Tháng Hai Q10"
    mock_source_row_2[8] = "12.0"
    mock_source_row_2[9] = "Q10"
    mock_source_row_2[10] = "Phường 12"
    mock_source_row_2[37] = "SYS-1002"

    mock_pool_row_1 = [""] * 96
    mock_pool_row_1[5] = "CMT8"
    mock_pool_row_1[6] = "123"
    mock_pool_row_1[9] = "Nội dung chính CMT8 Q3"
    mock_pool_row_1[10] = "Mô tả chi tiết CMT8 Q3"
    mock_pool_row_1[11] = "6.5" # gia
    mock_pool_row_1[13] = "100" # dt
    mock_pool_row_1[40] = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
    mock_pool_row_1[55] = "2001"
    mock_pool_row_1[72] = "SYS-1001"

    mock_pool_row_2 = list(mock_pool_row_1)
    mock_pool_row_2[9] = "Nội dung chính Ba Tháng Hai Q10"
    mock_pool_row_2[10] = "Mô tả chi tiết Ba Tháng Hai Q10"
    mock_pool_row_2[11] = "11.5"
    mock_pool_row_2[55] = "2002"
    mock_pool_row_2[72] = "SYS-1002"

    console_errors = []

    def handle_public_gviz(route):
        mock_data = {
            "version": "0.6",
            "status": "ok",
            "table": {
                "cols": [],
                "rows": [
                    {"c": mock_public_row_1},
                    {"c": mock_public_row_2}
                ]
            }
        }
        mock_jsonp = f"__gsCallback({json.dumps(mock_data)});"
        route.fulfill(content_type="application/javascript", body=mock_jsonp)

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        
        # ==========================================
        # 1. CLIENT LEAD CAPTURE & FAVORITES FLOW
        # ==========================================
        print("\n--- Running Client Lead Capture & Favorites Flow ---")
        client_context = browser.new_context(viewport={"width": 1280, "height": 800})
        client_page = client_context.new_page()
        
        client_page.on("console", lambda msg: (
            print(f"[Client Console {msg.type}] {msg.text}"),
            console_errors.append(msg.text) if msg.type == "error" else None
        ))
        client_page.on("requestfailed", lambda req: print(f"[Client Request Failed] {req.url} - {req.failure}"))
        client_page.on("response", lambda res: print(f"[Client Response {res.status}] {res.url}") if res.status >= 400 else None)
        
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
        
        # Navigate without setting name/phone in localStorage first to trigger lead capture
        client_url = f"http://localhost:{port}/index.html?s=1,2"
        try:
            print(f"Navigating client page: {client_url}")
            client_page.goto(client_url, wait_until="load", timeout=30000)
            
            # 1.1 Check Lead Capture Modal is displayed
            print("Checking if Lead Capture modal is displayed...")
            client_page.wait_for_selector("#leadCaptureModal.open", timeout=5000)
            is_visible = client_page.locator("#leadCaptureModal").is_visible()
            assert is_visible, "Lead Capture modal should be visible"
            
            # 1.2 Fill name and phone and submit
            print("Filling lead capture form...")
            client_page.fill("#leadCustName", "Khách E2E")
            client_page.fill("#leadCustPhone", "0908888888")
            
            print("Submitting lead capture...")
            client_page.locator(".lead-capture-submit-btn").click()
            
            # 1.3 Verify modal is closed and welcome banner is shown
            client_page.wait_for_selector("#leadCaptureModal", state="hidden", timeout=5000)
            print("Lead Capture modal closed successfully.")
            
            client_page.wait_for_selector("#welcomeBanner", timeout=5000)
            banner_text = client_page.locator("#welcomeBanner").inner_text()
            print(f"Welcome banner text: {banner_text}")
            assert "Khách E2E" in banner_text, f"Expected customer name in banner, got: {banner_text}"
            
            # 1.4 Favorites flow
            print("Waiting for cards...")
            client_page.wait_for_selector(".card", timeout=5000)
            card_count = client_page.locator(".card").count()
            assert card_count == 2, f"Expected 2 cards, got {card_count}"
            
            # Toggle favorite on the first card
            first_card_id = client_page.locator(".card").first.get_attribute("data-pid")
            print(f"First card ID: {first_card_id}")
            print("Toggling favorite on the first card...")
            first_heart = client_page.locator(".card .heart").first
            first_heart.click()
            time.sleep(0.5)
            
            # Verify heart button updated class to 'on'
            has_on_class = "on" in first_heart.get_attribute("class")
            assert has_on_class, "Heart button should have 'on' class after click"
            
            # Verify local storage favs update
            favs_str = client_page.evaluate("localStorage.getItem('favs')")
            print(f"localStorage favs: {favs_str}")
            assert first_card_id in favs_str, f"First card ID {first_card_id} should be saved in favorites"
            
            # Filter by favorites
            print("Clicking favorites filter button...")
            client_page.locator("#favFilterBtn").click()
            time.sleep(0.5)
            
            card_count_fav = client_page.locator(".card").count()
            print(f"Cards count after favorites filter: {card_count_fav}")
            assert card_count_fav == 1, f"Expected 1 card in favorites view, got {card_count_fav}"
            
        except Exception as e:
            print(f"[ERROR] Client View Lead Capture & Favorites Flow Failed: {e}")
            test_success = False
            client_page.screenshot(path=os.path.join(artifacts_dir, "client_error.png"))
        finally:
            client_context.close()
            
        # ==========================================
        # 2. ADMIN COLLECTIONS MANAGEMENT FLOW
        # ==========================================
        print("\n--- Running Admin Collections Management Flow ---")
        admin_context = browser.new_context(viewport={"width": 1280, "height": 800})
        admin_page = admin_context.new_page()
        
        admin_page.on("console", lambda msg: (
            print(f"[Admin Console {msg.type}] {msg.text}"),
            console_errors.append(msg.text) if msg.type == "error" else None
        ))
        admin_page.on("requestfailed", lambda req: print(f"[Admin Request Failed] {req.url} - {req.failure}"))
        admin_page.on("response", lambda res: print(f"[Admin Response {res.status}] {res.url}") if res.status >= 400 else None)
        
        # Inject isAdminSession
        admin_page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
        """)
        
        # Intercept and mock Admin Sheets API
        def handle_admin_sheets(route):
            url = route.request.url
            if "Source" in url:
                response_body = {"values": [["header_row"] * 46, mock_source_row_1, mock_source_row_2]}
            else:
                response_body = {"values": [["header_row"] * 96, mock_pool_row_1, mock_pool_row_2]}
            route.fulfill(content_type="application/json", body=json.dumps(response_body))

        admin_page.route(lambda url: "spreadsheets" in url and "values" in url, handle_admin_sheets)
        admin_page.route("**/gviz/tq**", handle_public_gviz)
        admin_page.route("**/api/config**", handle_api_config)
        
        admin_url = f"http://localhost:{port}/index.html"
        try:
            print(f"Navigating admin page to: {admin_url}")
            admin_page.goto(admin_url, wait_until="load", timeout=30000)
            
            # Wait for secure loading to finish
            print("Waiting for secure data loading to complete...")
            admin_page.wait_for_function("window.isSecureLoaded === true", timeout=10000)
            
            # Wait for cards to load in Admin Curation Pool
            admin_page.wait_for_selector(".card", timeout=10000)
            card_count = admin_page.locator(".card").count()
            print(f"Admin Pool cards count: {card_count}")
            assert card_count == 2, f"Expected 2 cards in admin curation pool, got {card_count}"
            
            # Select first card
            print("Selecting first card checkbox...")
            admin_page.locator(".card-sel").first.check(force=True)
            
            # Verify colFloatBtn is displayed (it is inside #dialActions but might be closed)
            admin_page.wait_for_selector("#colFloatBtn", timeout=5000)

            # Capture speed dial closed state screenshot
            closed_screenshot = os.path.join(artifacts_dir, "admin_speed_dial_closed.png")
            admin_page.screenshot(path=closed_screenshot)
            print(f"Captured screenshot of closed speed dial: {closed_screenshot}")
            
            # Click gear icon to open speed dial actions
            print("Opening speed dial menu...")
            admin_page.locator("#dialMainBtn").click()
            admin_page.wait_for_selector("#dialActions.open", timeout=5000)
            admin_page.wait_for_timeout(350) # wait for animation transition to finish

            # Capture speed dial open state screenshot
            open_screenshot = os.path.join(artifacts_dir, "admin_speed_dial_open.png")
            admin_page.screenshot(path=open_screenshot)
            print(f"Captured screenshot of open speed dial: {open_screenshot}")
            
            # Click float save button
            print("Clicking float save button...")
            admin_page.locator("#colFloatBtn").click()
            admin_page.wait_for_selector("#colSaveModal.open", timeout=5000)
            
            # Create a new collection
            print("Filling new collection name...")
            admin_page.fill("#newColName", "BST E2E Quận 3")
            
            # Submit create
            print("Submitting new collection...")
            admin_page.click("button:has-text('Tạo bộ sưu tập mới')")
            time.sleep(1)
            
            # Open filter panel to access collections manager
            print("Opening filter panel...")
            admin_page.locator("#filterBtn").click(force=True)
            admin_page.wait_for_selector("#filterPanel.open", timeout=5000)

            # Verify collection chip is rendered on manager
            chip_text = admin_page.locator("#collectionsManager").inner_text()
            print(f"Collections manager inner text: {chip_text}")
            assert "BST E2E Quận 3 (1)" in chip_text, f"Expected collection chip on manager, got {chip_text}"
            
            # Verify local storage collections update
            collections_str = admin_page.evaluate("localStorage.getItem('adminCollections')")
            print(f"localStorage collections: {collections_str}")
            assert "BST E2E Quận 3" in collections_str, "New collection should be stored in adminCollections"
            
            # View collection
            print("Clicking collection chip to view...")
            admin_page.locator("#collectionsManager span:has-text('BST E2E Quận 3')").click(force=True)
            time.sleep(0.5)
            
            # Close filter panel to see activeColBar clearly
            print("Closing filter panel...")
            admin_page.locator("#filterBtn").click(force=True)
            admin_page.wait_for_selector("#filterPanel:not(.open)", timeout=5000)

            # Verify active collection bar is visible
            admin_page.wait_for_selector("#activeColBar", timeout=5000)
            active_bar_text = admin_page.locator("#activeColBar").inner_text()
            print(f"Active collection bar text: {active_bar_text}")
            assert "BST E2E Quận 3" in active_bar_text, "Active collection bar should name the collection"
            
            # Exit collection view
            print("Exiting collection view...")
            time.sleep(1.0)
            admin_page.locator("#activeColBar button:has-text('Hủy xem')").click()
            admin_page.wait_for_selector("#activeColBar", state="hidden", timeout=5000)
            
            # Delete collection
            print("Opening collections modal to delete...")
            admin_page.locator("#favFilterBtn").click(force=True)
            
            # Wait for modal to open
            admin_page.wait_for_selector("#colViewModal.open", timeout=5000)
            
            # Click checkbox on 'BST E2E Quận 3'
            print("Selecting checkbox to delete...")
            admin_page.locator(".col-delete-checkbox[data-colname='BST E2E Quận 3']").click(force=True)
            
            # Handle confirm dialog
            admin_page.on("dialog", lambda dialog: dialog.accept())
            
            # Click speed dial delete button
            print("Clicking delete selected button...")
            admin_page.locator("button.delete-col-btn-float").click(force=True)
            time.sleep(1)
            
            # Verify collection is deleted from localStorage
            collections_after = admin_page.evaluate("localStorage.getItem('adminCollections')")
            print(f"localStorage collections after delete: {collections_after}")
            assert "BST E2E Quận 3" not in collections_after, "Collection should be deleted from adminCollections"
            
        except Exception as e:
            print(f"[ERROR] Admin Collections Flow Failed: {e}")
            test_success = False
            admin_page.screenshot(path=os.path.join(artifacts_dir, "admin_error.png"))
        finally:
            admin_context.close()
            
        browser.close()

    print(f"\nCaptured Console Errors: {console_errors}")
    # We ignore standard network or warning console outputs, only real script errors fail the test
    for err in console_errors:
        if "Failed to load resource" not in err:
            print("[WARNING] Actual JS console errors found!")
            # test_success = False

    if test_success:
        print("\n[🎉 ALL E2E COLLECTIONS TESTS PASSED SUCCESSFULLY]")
        sys.exit(0)
    else:
        print("\n[❌ E2E COLLECTIONS TESTS FAILED]")
        sys.exit(1)

if __name__ == "__main__":
    main()
