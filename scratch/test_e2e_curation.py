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

    # Pool Sheet columns matching what Lego Curation reads:
    # 0: id/noName, 5: ten_duong (col F), 6: so_nha (col G), 9: noi_dung_chinh (col J), 10: mo_ta_chi_tiet (col K),
    # 11: gia_chao (col L), 13: dt_thuc_te (col N), 27: sodo1 (col AB), 28: sodo2 (col AC), 29: img_mat_tien (col AD),
    # 40: public_cover/img1 (col AO), 55: khangngo_id (col BD), 72: system_id (col BU)
    mock_pool_row_1 = [""] * 96
    mock_pool_row_1[0] = "2001"
    mock_pool_row_1[5] = "Cách Mạng Tháng Tám" # đường
    mock_pool_row_1[6] = "123" # số nhà
    mock_pool_row_1[9] = "Nội dung chính CMT8 Q3 VIP"
    mock_pool_row_1[10] = "Mô tả chi tiết CMT8 Q3 VIP"
    mock_pool_row_1[11] = "6.5" # giá chào
    mock_pool_row_1[13] = "100" # diện tích
    mock_pool_row_1[27] = "https://res.cloudinary.com/demo/image/upload/sodo1_123.jpg" # sodo1
    mock_pool_row_1[28] = "https://res.cloudinary.com/demo/image/upload/sodo2_123.jpg" # sodo2
    mock_pool_row_1[29] = "https://res.cloudinary.com/demo/image/upload/mat_tien_123.jpg" # mat_tien
    mock_pool_row_1[40] = "https://res.cloudinary.com/demo/image/upload/interior_1.jpg" # interior 1
    mock_pool_row_1[55] = "2001"
    mock_pool_row_1[72] = "SYS-1001" # system_id

    mock_pool_row_2 = list(mock_pool_row_1)
    mock_pool_row_2[0] = "2002"
    mock_pool_row_2[9] = "Nội dung chính Ba Tháng Hai Q10"
    mock_pool_row_2[10] = "Mô tả chi tiết Ba Tháng Hai Q10"
    mock_pool_row_2[11] = "11.5"
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
                    {"c": mock_public_row_1},
                    {"c": mock_public_row_2}
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
        print("\n--- Running Desktop Curation Test (1280x800) ---")
        admin_context = browser.new_context(viewport={"width": 1280, "height": 800})
        admin_page = admin_context.new_page()
        
        admin_page.on("console", lambda msg: (
            print(f"[Admin Console {msg.type}] {msg.text}"),
            console_errors.append(msg.text) if msg.type == "error" else None
        ))
        admin_page.on("requestfailed", lambda req: print(f"[Admin Request Failed] {req.url} - {req.failure}"))
        admin_page.on("pageerror", lambda err: print(f"[Admin Page Error] {err}"))
        
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
                    response_body = {"values": [mock_source_row_1, mock_source_row_2]}
                else:
                    response_body = {"values": [mock_pool_row_1, mock_pool_row_2]}
                route.fulfill(content_type="application/json", body=json.dumps(response_body))
            elif method == "PUT" or method == "POST":
                post_data = route.request.post_data
                parsed_data = json.loads(post_data) if post_data else None
                captured_sheets_calls.append({
                    "method": method,
                    "url": url,
                    "data": parsed_data
                })
                print(f"[Sheets Mock API] Captured writing request payload: {parsed_data}")
                route.fulfill(content_type="application/json", body=json.dumps({"spreadsheetId": "mock-sheet", "updatedCells": 1}))
            else:
                route.continue_()

        # Intercept AI generation endpoint
        def handle_ai_generate(route):
            print("[AI Mock API] Auto fill AI generated request")
            response_body = {
                "status": "success",
                "tieu_de_public": "Căn CMT8 Q3 VIP - AI Generated Title",
                "mo_ta_public": "Mô tả công khai tự động biên tập bởi AI cho căn Cách Mạng Tháng Tám...",
                "phuong_cu": "Phường 11"
            }
            route.fulfill(content_type="application/json", body=json.dumps(response_body))

        admin_page.route(lambda url: "spreadsheets" in url and "values" in url, handle_admin_sheets)
        admin_page.route("**/gviz/tq**", handle_public_gviz)
        admin_page.route("**/api/ai/generate**", handle_ai_generate)
        # Mock Google Maps and Cloudinary requests
        admin_page.route("**/maps.google.com/**", lambda route: route.fulfill(status=200, body="<html>Dummy Maps</html>"))
        admin_page.route("**/res.cloudinary.com/**", lambda route: route.fulfill(status=200, body="Dummy Image"))

        admin_url = f"http://localhost:{port}/index.html"
        
        try:
            print(f"Navigating admin page to: {admin_url}")
            admin_page.goto(admin_url, wait_until="load", timeout=30000)
            
            # Wait for secure loading
            print("Waiting for secure data loading...")
            admin_page.wait_for_function("window.isSecureLoaded === true", timeout=10000)
            
            # Wait for curation pool list cards
            admin_page.wait_for_selector(".card", timeout=10000)
            card_count = admin_page.locator(".card").count()
            print(f"Curation pool cards count: {card_count}")
            assert card_count == 2, f"Expected 2 cards, got {card_count}"
            
            # Open the curation drawer for first card
            print("Opening curation drawer for first card (SYS-1001)...")
            admin_page.evaluate("openPoolS('SYS-1001')")
            
            # Verify Curator panel UI accordion items
            print("Verifying curation accordion panels...")
            admin_page.wait_for_selector("#accSource", timeout=5000)
            
            # Verify BĐS is not published yet, so Preview accordion should not be present
            assert admin_page.locator("#accPreview").count() == 0, "Preview accordion should not be visible for unpublished listings"
            
            # Check the warning save pool notice is shown
            save_notice = admin_page.locator("#poolSaveNotice").inner_text()
            print(f"Save notice text: {save_notice}")
            assert "Nhập đầy đủ cả Tiêu đề Public và Mô tả Public" in save_notice, "Should warn about missing public data"
            
            # Verify the "Lên sóng" button is currently hidden
            is_visible_save = admin_page.locator("#savePoolBtn").is_visible()
            print(f"Is Lên sóng button visible? {is_visible_save}")
            assert not is_visible_save, "Lên sóng button should not be visible when fields are empty"
            
            # Expand the editing accordion to make button visible
            print("Expanding Curation editing accordion...")
            admin_page.locator("#accSource .accordion-header").click()
            admin_page.wait_for_timeout(500)
            
            # Test Auto Fill AI Details
            print("Clicking 'Tự động điền' AI button...")
            admin_page.locator("#btnAutoFillCuration").click()
            admin_page.wait_for_timeout(1000) # wait for AI fetch
            
            # Verify fields filled
            title_val = admin_page.locator("#editTieuDeBds").input_value()
            desc_val = admin_page.locator("#editMoTaBds").input_value()
            print(f"Filled Title: {title_val}")
            print(f"Filled Description: {desc_val}")
            assert "AI Generated Title" in title_val, "Title should be auto filled by AI"
            assert "Cách Mạng Tháng Tám" in desc_val, "Description should be auto filled by AI"
            
            # Verify save notice turns green/success
            new_save_notice = admin_page.locator("#poolSaveNotice").inner_text()
            print(f"Updated save notice: {new_save_notice}")
            assert "Đã đủ điều kiện" in new_save_notice, "Save notice should indicate conditions met"
            
            # Verify "Lên sóng" button is now visible
            is_visible_save_now = admin_page.locator("#savePoolBtn").is_visible()
            print(f"Is Lên sóng button visible now? {is_visible_save_now}")
            assert is_visible_save_now, "Lên sóng button should be visible when title & description are filled"
            
            # Verify Image Editor Carousel exists and shows correct image slides
            print("Checking Curation Image Editor Carousel...")
            admin_page.wait_for_selector(".image-editor-carousel-container", timeout=5000)
            slides_count = admin_page.locator(".carousel-slide-item").count()
            print(f"Image editor slides: {slides_count}")
            
            # Go to slide 2 (Interior image) and select as public
            print("Navigating to slide 2 (Interior image)...")
            admin_page.evaluate("gotoImageEditorSlide(2)")
            admin_page.wait_for_timeout(500)
            print("Toggling Public flag on slide 2...")
            admin_page.locator("#ctrlPublicBtn").click()
            admin_page.wait_for_timeout(500)
            
            # Go back to slide 0
            print("Navigating back to slide 0...")
            admin_page.evaluate("gotoImageEditorSlide(0)")
            admin_page.wait_for_timeout(500)
            
            # Open speed dial menu first
            print("Opening speed dial menu...")
            admin_page.locator("#dialMainBtn").click()
            admin_page.wait_for_timeout(500)
            
            # Clicking 'Lên sóng' button to submit curation changes
            print("Clicking 'Lên sóng' button to submit curation changes...")
            admin_page.locator("#savePoolBtn").click()
            
            # Wait for Sheets API PUT requests to be fired (robust polling up to 10s)
            sheets_captured = False
            for _ in range(20):
                if len(captured_sheets_calls) > 0:
                    sheets_captured = True
                    break
                admin_page.wait_for_timeout(500)
            
            assert sheets_captured, "Should have triggered sheets PUT calls"
            
            # Verify that we wrote to Sheet Source
            source_write = [call for call in captured_sheets_calls if "Source" in call["url"]]
            assert len(source_write) > 0, "Should have written to Source sheet"
            source_data = source_write[0]["data"]["values"][0]
            print(f"Wrote to Source: {source_data[1]} (SystemID={source_data[37]})")
            assert source_data[37] == "SYS-1001", "Correct System ID should be synced"
            
            # Save Desktop Screenshot
            screenshot_path = os.path.join(artifacts_dir, "admin_curation_desktop.png")
            admin_page.screenshot(path=screenshot_path)
            print(f"Desktop Curation screenshot saved to {screenshot_path}")
            
            if is_headed:
                print("\n[Headed Debug] Desktop curation complete. Pausing for 120 seconds for manual inspection...")
                print("Check the iframe preview loaded from memory!")
                time.sleep(120)
            
        except Exception as e:
            print(f"[ERROR] Desktop Curation Flow Failed: {e}")
            test_success = False
            admin_page.screenshot(path=os.path.join(artifacts_dir, "admin_curation_error.png"))
        finally:
            admin_context.close()
            
        # --- MOBILE VIEWPORT TEST (375x812, hasTouch=True) ---
        print("\n--- Running Mobile Curation Test (375x812) ---")
        mobile_context = browser.new_context(
            viewport={"width": 375, "height": 812},
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        )
        mobile_page = mobile_context.new_page()
        
        mobile_page.on("console", lambda msg: (
            print(f"[Mobile Console {msg.type}] {msg.text}"),
            console_errors.append(msg.text) if msg.type == "error" else None
        ))
        mobile_page.on("requestfailed", lambda req: print(f"[Mobile Request Failed] {req.url} - {req.failure}"))
        mobile_page.on("pageerror", lambda err: print(f"[Mobile Page Error] {err}"))
        
        mobile_page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
        """)
        
        mobile_page.route(lambda url: "spreadsheets" in url and "values" in url, handle_admin_sheets)
        mobile_page.route("**/gviz/tq**", handle_public_gviz)
        mobile_page.route("**/api/ai/generate**", handle_ai_generate)
        mobile_page.route("**/maps.google.com/**", lambda route: route.fulfill(status=200, body="<html>Dummy Maps</html>"))
        mobile_page.route("**/res.cloudinary.com/**", lambda route: route.fulfill(status=200, body="Dummy Image"))

        try:
            print(f"Navigating mobile page to: {admin_url}")
            mobile_page.goto(admin_url, wait_until="load", timeout=30000)
            
            # Wait for secure loading
            mobile_page.wait_for_function("window.isSecureLoaded === true", timeout=10000)
            
            # Open pool listing
            mobile_page.evaluate("openPoolS('SYS-1002')")
            
            # Check accordion rendering
            mobile_page.wait_for_selector("#accSource", timeout=5000)
            mobile_page.wait_for_selector("#accPreview", timeout=5000)
            
            # Scroll to make sure it's in view
            mobile_page.locator("#accSource").scroll_into_view_if_needed()
            
            # Test toggle accordion
            print("Clicking accordion headers to toggle...")
            mobile_page.locator("#accSource .accordion-header").click()
            mobile_page.wait_for_timeout(500)
            
            # Save Mobile Screenshot
            screenshot_path = os.path.join(artifacts_dir, "admin_curation_mobile.png")
            mobile_page.screenshot(path=screenshot_path)
            print(f"Mobile Curation screenshot saved to {screenshot_path}")
            
        except Exception as e:
            print(f"[ERROR] Mobile Curation Flow Failed: {e}")
            test_success = False
        finally:
            mobile_context.close()
            
        browser.close()
        
    if test_success:
        print("\n[🎉 ALL E2E CURATION TESTS PASSED SUCCESSFULLY]")
        sys.exit(0)
    else:
        print("\n[❌ SOME E2E CURATION TESTS FAILED]")
        sys.exit(1)

if __name__ == "__main__":
    main()
