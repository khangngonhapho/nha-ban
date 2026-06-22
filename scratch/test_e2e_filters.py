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
    artifacts_dir = r"C:\Users\Khang Ngo\.gemini\antigravity\brain\916f8731-ddb9-4d34-87c5-3a0080f87669"
    
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
    mock_public_row_1[44] = {"v": '{"Criteria_Duong_truoc_nha": "Ngõ 1 ô tô ( 2.5 -5m)"}'}

    mock_public_row_2 = list(mock_public_row_1)
    mock_public_row_2[0] = {"v": "1002"}
    mock_public_row_2[1] = {"v": "Căn Ba Tháng Hai Q10"}
    mock_public_row_2[5] = {"v": 12.0}
    mock_public_row_2[6] = {"v": "q10"}
    mock_public_row_2[7] = {"v": "Phường 12"}
    mock_public_row_2[34] = {"v": "SYS-1002"}

    mock_public_row_3 = list(mock_public_row_1)
    mock_public_row_3[0] = {"v": "1003"}
    mock_public_row_3[1] = {"v": "Căn Trường Chinh TB"}
    mock_public_row_3[5] = {"v": 18.5}
    mock_public_row_3[6] = {"v": "tb"}
    mock_public_row_3[7] = {"v": "Phường 2"}
    mock_public_row_3[34] = {"v": "SYS-1003"}

    # ── Define Mock Data for Admin View ──
    # Source rows
    mock_source_row_1 = [""] * 46
    mock_source_row_1[0] = "1"
    mock_source_row_1[1] = "CP"
    mock_source_row_1[3] = "SYS-1001" # system_id
    mock_source_row_1[4] = "Căn CMT8 Q3 VIP"
    mock_source_row_1[5] = "100"
    mock_source_row_1[6] = "4"
    mock_source_row_1[7] = "5"
    mock_source_row_1[8] = "8.5"
    mock_source_row_1[9] = "Q3"
    mock_source_row_1[10] = "Phường 11"
    mock_source_row_1[11] = "Mặt tiền"
    mock_source_row_1[12] = "Đông Nam"
    mock_source_row_1[13] = "15"
    mock_source_row_1[14] = "0"
    mock_source_row_1[15] = "Bình thường"
    mock_source_row_1[16] = "Hàng Ngon"
    mock_source_row_1[20] = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
    mock_source_row_1[34] = "Đường CMT8"
    mock_source_row_1[37] = "SYS-1001"

    mock_source_row_2 = list(mock_source_row_1)
    mock_source_row_2[3] = "SYS-1002"
    mock_source_row_2[4] = "Căn Ba Tháng Hai Q10"
    mock_source_row_2[8] = "12.0"
    mock_source_row_2[9] = "Q10"
    mock_source_row_2[10] = "Phường 12"
    mock_source_row_2[37] = "SYS-1002"

    # Pool rows
    mock_pool_row_1 = [""] * 96
    mock_pool_row_1[5] = "CMT8"
    mock_pool_row_1[6] = "123"
    mock_pool_row_1[9] = "Nội dung chính CMT8 Q3"
    mock_pool_row_1[10] = "Mô tả chi tiết CMT8 Q3"
    mock_pool_row_1[11] = "6.5" # gia
    mock_pool_row_1[13] = "100" # dt
    mock_pool_row_1[14] = "95"
    mock_pool_row_1[40] = "https://res.cloudinary.com/demo/image/upload/sample.jpg"
    mock_pool_row_1[55] = "2001"
    mock_pool_row_1[72] = "SYS-1001"
    mock_pool_row_1[74] = "0901234567"
    mock_pool_row_1[75] = "Đầu chủ A"
    mock_pool_row_1[76] = "fb.com"
    mock_pool_row_1[93] = '{"Criteria_Duong_truoc_nha": "Ngõ 1 ô tô ( 2.5 -5m)"}'

    mock_pool_row_2 = list(mock_pool_row_1)
    mock_pool_row_2[9] = "Nội dung chính Ba Tháng Hai Q10"
    mock_pool_row_2[10] = "Mô tả chi tiết Ba Tháng Hai Q10"
    mock_pool_row_2[11] = "11.5"
    mock_pool_row_2[55] = "2002"
    mock_pool_row_2[72] = "SYS-1002"

    console_errors = []

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        
        # ==========================================
        # 1. CLIENT SEARCH & FILTER E2E TEST
        # ==========================================
        print("\n--- Running Client Search & Filter E2E Test ---")
        client_context = browser.new_context(viewport={"width": 1280, "height": 800})
        client_page = client_context.new_page()
        
        # Capture console errors and print all console logs
        client_page.on("console", lambda msg: (
            print(f"[Client Console {msg.type}] {msg.text}"),
            console_errors.append(msg.text) if msg.type == "error" else None
        ))
        client_page.on("requestfailed", lambda req: print(f"[Client Request Failed] {req.url} - {req.failure}"))
        client_page.on("response", lambda res: print(f"[Client Response {res.status}] {res.url}") if res.status >= 400 else None)
        
        # Inject client name & phone to bypass lead capture modal
        client_page.add_init_script("""
            localStorage.setItem('client_name', 'Test Customer');
            localStorage.setItem('client_phone', '0901234567');
        """)
        
        # Intercept public sheets
        def handle_public_gviz(route):
            mock_data = {
                "version": "0.6",
                "status": "ok",
                "table": {
                    "cols": [],
                    "rows": [
                        {"c": mock_public_row_1},
                        {"c": mock_public_row_2},
                        {"c": mock_public_row_3}
                    ]
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
                    "json_ui_filters": [
                        {
                            "field": "Criteria_Duong_truoc_nha",
                            "label": "Đường trước nhà",
                            "type": "select",
                            "options": [
                                "",
                                "Hẻm xe máy ( <2m)",
                                "Ngõ ngách (2 - 2.5m)"
                            ]
                        }
                    ],
                    "json_ui_fields": ["Criteria_Duong_truoc_nha"]
                }
            }
            route.fulfill(content_type="application/json", body=json.dumps(mock_config))

        client_page.route("**/gviz/tq**", handle_public_gviz)
        client_page.route("**/api/config**", handle_api_config)
        
        # Use s=1,2,3 which will correctly map to first 3 rows in mock table
        client_url = f"http://localhost:{port}/index.html?s=1,2,3"
        try:
            print(f"Navigating client page to: {client_url}")
            client_page.goto(client_url, wait_until="load", timeout=30000)
            
            print("Waiting for cards to load...")
            client_page.wait_for_selector(".card", timeout=10000)
            card_count = client_page.locator(".card").count()
            print(f"Initial listings count: {card_count}")
            assert card_count == 3, f"Expected 3 cards, got {card_count}"
            
            # Open filter panel
            print("Opening filter panel...")
            client_page.locator("#filterBtn").click()
            client_page.wait_for_selector("#filterPanel.open", timeout=5000)
            
            # Select District Filter Q3
            print("Selecting Q3 in District multiselect...")
            client_page.locator("#districtMulti .multiselect-trigger").click()
            client_page.wait_for_selector("#districtOptions .multiselect-option", timeout=5000)
            
            # Check 'q3' checkbox
            client_page.locator("#districtOptions input[value='q3']").check()
            print("Selected Q3 checkbox.")
            
            # Wait for filter to apply
            time.sleep(1)
            
            # Close filter panel
            client_page.locator("#filterBtn").click()
            client_page.wait_for_selector("#filterPanel:not(.open)", timeout=5000)
            
            # Verify filtered cards (Only Q3 card should remain)
            card_count = client_page.locator(".card").count()
            print(f"Listings count after Q3 filter: {card_count}")
            assert card_count == 1, f"Expected 1 card (Q3), got {card_count}"
            
            # Click "Xóa lọc" button to reset
            print("Opening filter panel to reset...")
            client_page.locator("#filterBtn").click()
            client_page.wait_for_selector("#filterPanel.open", timeout=5000)
            
            print("Clicking clear button in filter panel...")
            client_page.locator(".btn-filter-clear").click()
            time.sleep(0.5)
            
            # Close filter panel
            print("Closing filter panel...")
            client_page.locator("#filterBtn").click()
            client_page.wait_for_selector("#filterPanel:not(.open)", timeout=5000)
            
            # Verify restored count
            card_count = client_page.locator(".card").count()
            print(f"Listings count after reset: {card_count}")
            assert card_count == 3, f"Expected 3 cards, got {card_count}"
            
            # Test text search
            print("Testing search toggle and input...")
            client_page.locator("#searchToggleBtn").click()
            client_page.wait_for_selector("#searchBar.open", timeout=5000)
            
            client_page.fill("#bdsSearchInput", "Ba Tháng Hai")
            client_page.evaluate("onSearchInput()")
            time.sleep(1.5) # Wait for search debounce
            
            card_count = client_page.locator(".card").count()
            print(f"Listings count for search 'Ba Tháng Hai': {card_count}")
            assert card_count == 1, f"Expected 1 card for Q10 search, got {card_count}"
            
            # Clear search via cross button
            print("Clearing search via clear button...")
            client_page.locator("#searchClear").click()
            time.sleep(1)
            
            card_count = client_page.locator(".card").count()
            print(f"Listings count after clearing search: {card_count}")
            assert card_count == 3, f"Expected 3 cards after search clear, got {card_count}"
            
        except Exception as e:
            print(f"[ERROR] Client View Search & Filter Failed: {e}")
            test_success = False
            client_page.screenshot(path=os.path.join(artifacts_dir, "client_filter_error.png"))
        finally:
            client_context.close()

        # ==========================================
        # 2. ADMIN ADVANCED FILTER E2E TEST
        # ==========================================
        print("\n--- Running Admin Advanced Filter E2E Test ---")
        admin_context = browser.new_context(viewport={"width": 1280, "height": 800})
        admin_page = admin_context.new_page()
        
        # Capture console errors and print all console logs
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

        # Intercept auth refresh API calls to avoid 404
        def handle_auth_api(route):
            response_body = {
                "access_token": "mock_new_access_token",
                "expires_in": 3600
            }
            route.fulfill(content_type="application/json", body=json.dumps(response_body))

        admin_page.route("**/api/auth/**", handle_auth_api)
        admin_page.route(lambda url: "spreadsheets" in url and "values" in url, handle_admin_sheets)
        admin_page.route("**/gviz/tq**", handle_public_gviz)
        admin_page.route("**/api/config**", handle_api_config)
        
        admin_url = f"http://localhost:{port}/index.html"
        try:
            print(f"Navigating admin page to: {admin_url}")
            admin_page.goto(admin_url, wait_until="load", timeout=30000)
            
            print("Waiting for cards to load in Admin Curation Pool...")
            admin_page.wait_for_selector(".card", timeout=10000)
            card_count = admin_page.locator(".card").count()
            print(f"Initial Pool listings count: {card_count}")
            assert card_count == 2, f"Expected 2 cards in curator pool, got {card_count}"
            
            # Open filter panel
            print("Opening filter panel...")
            admin_page.locator("#filterBtn").click()
            admin_page.wait_for_selector("#filterPanel.open", timeout=5000)
            
            # Type in advanced range price
            print("Filtering price range: 7.0 to 12.0...")
            admin_page.fill("#filterGiaMin", "7.0")
            admin_page.fill("#filterGiaMax", "12.0")
            time.sleep(1.5) # wait for filter apply
            
            card_count = admin_page.locator(".card").count()
            print(f"Listings count after price range [7.0, 12.0]: {card_count}")
            assert card_count == 1, f"Expected 1 card in price range [7.0, 12.0], got {card_count}"
            
            # Clear price range filters while filter panel is open
            print("Clearing price range filters...")
            admin_page.fill("#filterGiaMin", "")
            admin_page.fill("#filterGiaMax", "")
            time.sleep(0.5)

            # Close filter panel to interact with main page elements
            print("Closing filter panel...")
            admin_page.locator("#filterBtn").click()
            admin_page.wait_for_selector("#filterPanel:not(.open)", timeout=5000)
            
            # Check "Chỉ hiện căn Public" toggle programmatically
            print("Testing 'Chỉ hiện căn Public' toggle...")
            admin_page.evaluate("document.getElementById('onAirToggle').checked = true; toggleShowOnAirOnly(true);")
            time.sleep(1.5)
            
            card_count = admin_page.locator(".card").count()
            print(f"Listings count with 'Chỉ hiện căn Public' toggle: {card_count}")
            assert card_count == 2, f"Expected 2 public cards, got {card_count}"
            
        except Exception as e:
            print(f"[ERROR] Admin View Search & Filter Failed: {e}")
            test_success = False
            admin_page.screenshot(path=os.path.join(artifacts_dir, "admin_filter_error.png"))
        finally:
            admin_context.close()
            
        browser.close()
        
    print(f"\nCaptured Console Errors: {console_errors}")
    if len(console_errors) > 0:
        print("[WARNING] Javascript errors detected in console during E2E testing!")
        test_success = False
        
    if test_success:
        print("\n[🎉 ALL E2E FILTERS TESTS PASSED SUCCESSFULLY]")
        sys.exit(0)
    else:
        print("\n[❌ E2E FILTERS TESTS FAILED]")
        sys.exit(1)

if __name__ == "__main__":
    main()
