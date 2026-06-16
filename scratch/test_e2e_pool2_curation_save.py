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
    artifacts_dir = r"C:\Users\Khang Ngo\.gemini\antigravity\brain\0fdb4d89-b92f-4650-8554-318e53f44db2"
    repo_assets_dir = r"d:\LHTBrain\01_PROJECTS/BDS-KhangNgo/docs/workflows/assets"
    
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    
    time.sleep(1.5) # Allow server to bind
    
    # Define Mock Data matching Pool 2
    mock_public_row_1 = [None] * 45
    mock_public_row_1[0] = {"v": "2001"} # id
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

    # Pool 2 Columns: Listings
    mock_pool_row_1 = [""] * 96
    mock_pool_row_1[0] = "2001" # tk_id
    mock_pool_row_1[1] = "active" # status
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
    mock_pool_row_1[60] = "5.5" # Đường trước nhà (m)
    mock_pool_row_1[72] = "SYS-1001" # system_id

    console_errors = []
    test_success = True
    captured_put_payload = []

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
        if "Custom" in url or "Source" in url:
            response_body = {"values": [["header_row"] * 46, mock_source_row_1]}
        else:
            response_body = {"values": [mock_pool_row_1]}
        route.fulfill(content_type="application/json", body=json.dumps(response_body))

    def handle_api_config(route):
        route.fulfill(content_type="application/json", body=json.dumps({
            "active_pool_system": "Pool2",
            "pool2_raw_sheet_id": "mock_pool2_raw_sheet_id",
            "pool2_custom_sheet_id": "mock_pool2_custom_sheet_id",
            "pool2_public_sheet_id": "mock_pool2_public_sheet_id"
        }))

    def handle_put_listing(route):
        print(f"[Mock PUT API] Intercepted {route.request.method} {route.request.url}")
        post_data = route.request.post_data
        parsed_data = json.loads(post_data) if post_data else None
        captured_put_payload.append(parsed_data)
        route.fulfill(content_type="application/json", body=json.dumps({"status": "success", "message": "Saved successfully"}))

    is_headed = "--headed" in sys.argv
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=not is_headed)
        admin_context = browser.new_context(viewport={"width": 1280, "height": 950})
        
        # Grant clipboard access
        admin_context.grant_permissions(["clipboard-read", "clipboard-write"])
        
        admin_page = admin_context.new_page()
        
        admin_page.on("console", lambda msg: (
            print(f"[Admin Console {msg.type}] {msg.text}"),
            console_errors.append(msg.text) if msg.type == "error" else None
        ))
        admin_page.on("requestfailed", lambda req: print(f"[Admin Request Failed] {req.url} - {req.failure}"))
        admin_page.on("pageerror", lambda err: print(f"[Admin Page Error] {err}"))
        
        # Inject admin session
        admin_page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
            window.alert = function(msg) { console.log("ALERT DIALOG: " + msg); };
            window.confirm = function(msg) { console.log("CONFIRM DIALOG: " + msg); return true; };
        """)
        
        admin_page.route("**/api/config", handle_api_config)
        admin_page.route(lambda url: "spreadsheets" in url and "values" in url, handle_admin_sheets)
        admin_page.route("**/gviz/tq**", handle_public_gviz)
        admin_page.route(lambda url: "/api/listings/" in url, handle_put_listing)
        
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
            
            # Verify script is loaded
            detail_script_src = admin_page.evaluate("document.getElementById('lego_detail_admin_script').src")
            print(f"Loaded detail script: {detail_script_src}")
            assert "lego_detail_admin_pool2.js" in detail_script_src, "Should load Pool2 detail script"
            
            # Wait for card
            admin_page.wait_for_selector(".card", timeout=10000)
            
            # Open the curation drawer for the card
            print("Opening curation drawer for SYS-1001...")
            admin_page.evaluate("openPoolS('SYS-1001')")
            
            # Expand the editing accordion
            print("Expanding Curation editing accordion...")
            admin_page.locator("#accSource .accordion-header").click()
            admin_page.wait_for_timeout(500)

            # Wait for the form fields
            admin_page.wait_for_selector("#editSoNha", state="visible", timeout=5000)
            
            # Fill out form fields
            print("Filling curation form fields (Groups 1, 2, 3)...")
            
            # Group 1: Địa chỉ cụ thể
            admin_page.locator("#editSoNha").fill("456")
            admin_page.locator("#editTenDuong").fill("Ba Tháng Hai")
            admin_page.locator("#editPhuong").fill("Phường 12")
            admin_page.locator("#editQuan").fill("Quận 10")
            admin_page.locator("#editDiaChiThat").fill("456 Ba Tháng Hai, Phường 12, Quận 10")
            
            # Group 2: Thông số kỹ thuật & Giá
            admin_page.locator("#editDtThucTe").fill("85")
            admin_page.locator("#editDtTrenSo").fill("80")
            admin_page.locator("#editMatTien").fill("4.2")
            admin_page.locator("#editChieuDai").fill("19")
            admin_page.locator("#editHuong").select_option("Tây Nam")
            admin_page.locator("#editSoTang").fill("3")
            admin_page.locator("#editSoPn").fill("4")
            admin_page.locator("#editSoWc").fill("3")
            admin_page.locator("#editGiaChao").fill("12.5")
            
            # Group 3: Thông số khác
            admin_page.locator("#editMaKhangNgo").fill("M456IBTH")
            admin_page.locator("#editTieuDeBds").fill("Cực phẩm mặt tiền Ba Tháng Hai Q10 kinh doanh tốt")
            admin_page.locator("#editMoTaBds").fill("Mô tả chi tiết nhà Ba Tháng Hai...")
            admin_page.locator("#editGiaPublic").fill("12.3")
            admin_page.locator("#editNote").fill("Ghi chú nội bộ admin...")
            admin_page.locator("#editTinhTrang").select_option("Đang bán")
            admin_page.locator("#editDanhGia").select_option("Hàng Ngon")
            admin_page.locator("#editPhanLoaiHem").select_option("Mặt tiền đường")
            admin_page.locator("#editDuongTruocNha").fill("20")
            
            # Criteria dropdowns
            admin_page.locator("#editCriteriaNoiThat").select_option("Đầy đủ")
            admin_page.locator("#editCriteriaThangMay").select_option("Không")
            admin_page.locator("#editCriteriaLoaiNgo").select_option("Thông")
            admin_page.locator("#editCriteriaBaiDoXe").select_option("Gần")
            admin_page.locator("#editCriteriaKinhDoanh").select_option("Có")
            admin_page.locator("#editCriteriaHuong").select_option("Tây Tứ Trạch")
            admin_page.locator("#editCriteriaDuongOto").select_option("Đỗ cửa")
            
            # Checkboxes
            admin_page.locator("#editNguTret").check()
            admin_page.locator("#editChdv").check()
            
            # Scroll to top of form for screenshot
            admin_page.locator("#editSoNha").scroll_into_view_if_needed()
            admin_page.wait_for_timeout(300)
            
            # Save curation screen capture
            os.makedirs(repo_assets_dir, exist_ok=True)
            screenshot_path_repo = os.path.join(repo_assets_dir, "admin_curation_pool2_specs.png")
            screenshot_path_artifact = os.path.join(artifacts_dir, "admin_curation_pool2_specs.png")
            admin_page.screenshot(path=screenshot_path_repo)
            admin_page.screenshot(path=screenshot_path_artifact)
            print(f"Pool2 curation form screenshot saved to {screenshot_path_repo}")
            
            # Open speed dial menu first
            print("Opening speed dial menu...")
            admin_page.locator("#dialMainBtn").click()
            admin_page.wait_for_timeout(500)
            
            # Click Save button
            print("Clicking save changes button...")
            admin_page.locator("#saveSourceBtn").click()
            admin_page.wait_for_timeout(1000)
            
            # Assert PUT payload
            assert len(captured_put_payload) == 1, "PUT request should be intercepted once"
            payload = captured_put_payload[0]
            print(f"Asserting PUT payload fields: {json.dumps(payload, indent=2)}")
            assert payload["ngo_so_nha"] == "456"
            assert payload["duong"] == "Ba Tháng Hai"
            assert payload["phuong"] == "Phường 12"
            assert payload["quan"] == "Quận 10"
            assert payload["dia_chi_that"] == "456 Ba Tháng Hai, Phường 12, Quận 10"
            assert payload["dt_thuc_te"] == "85"
            assert payload["dt_tren_so"] == "80"
            assert payload["mat_tien"] == "4.2"
            assert payload["chieu_dai"] == "19"
            assert payload["huong"] == "Tây Nam"
            assert payload["so_tang"] == "3"
            assert payload["so_phong_ngu"] == "4"
            assert payload["so_nha_ve_sinh"] == "3"
            assert payload["gia_chao"] == "12.5"
            assert payload["ma_khang_ngo"] == "M456IBTH"
            assert payload["tieu_de_public"] == "Cực phẩm mặt tiền Ba Tháng Hai Q10 kinh doanh tốt"
            assert payload["mo_ta_public"] == "Mô tả chi tiết nhà Ba Tháng Hai..."
            assert payload["gia_public"] == "12.3"
            assert payload["note_noi_bo"] == "Ghi chú nội bộ admin..."
            assert payload["tinh_trang_nha"] == "Đang bán"
            assert payload["danh_gia"] == "Hàng Ngon"
            assert payload["phan_loai_hem"] == "Mặt tiền đường"
            assert payload["custom_rong_hem"] == "20"
            assert payload["criteria_noi_that"] == "Đầy đủ"
            assert payload["criteria_thang_may"] == "Không"
            assert payload["criteria_loai_ngo"] == "Thông"
            assert payload["criteria_khoang_cach_bai_do_xe"] == "Gần"
            assert payload["criteria_kinh_doanh_dong_tien"] == "Có"
            assert payload["criteria_huong_nha"] == "Tây Tứ Trạch"
            assert payload["criteria_khoang_cach_duong_oto"] == "Đỗ cửa"
            assert payload["ngu_tret"] == "Có"
            assert payload["chdv"] == "Có"
            print("All assertions PASSED successfully!")
            
        except Exception as e:
            print(f"Test failed with exception: {e}")
            test_success = False
            
        finally:
            browser.close()
            
    if test_success:
        print("E2E Test PASS!")
        sys.exit(0)
    else:
        print("E2E Test FAIL!")
        sys.exit(1)

if __name__ == "__main__":
    main()
