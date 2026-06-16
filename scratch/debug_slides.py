import os
import sys
import time
import socket
import threading
import http.server
import socketserver
import json
from playwright.sync_api import sync_playwright

class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def run_server(port, directory):
    class Handler(QuietHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
    server = socketserver.TCPServer(("", port), Handler)
    server.serve_forever()

def main():
    project_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    time.sleep(1.0)

    # ── Define Mock Data ──
    mock_public_row_1 = [None] * 45
    mock_public_row_1[0] = {"v": "1001"}
    mock_public_row_1[1] = {"v": "Căn CMT8 Q3 VIP"}
    mock_public_row_1[2] = {"v": 100}
    mock_public_row_1[3] = {"v": 4}
    mock_public_row_1[4] = {"v": 5}
    mock_public_row_1[5] = {"v": 8.5}
    mock_public_row_1[6] = {"v": "q3"}
    mock_public_row_1[7] = {"v": "Phường 11"}
    mock_public_row_1[8] = {"v": "Mặt tiền"}
    mock_public_row_1[9] = {"v": "Đông Nam"}
    mock_public_row_1[10] = {"v": 15}
    mock_public_row_1[11] = {"v": 0}
    mock_public_row_1[12] = {"v": "Bình thường"}
    mock_public_row_1[13] = {"v": "Hàng Ngon"}
    mock_public_row_1[14] = {"v": "Không"}
    mock_public_row_1[15] = {"v": "Không"}
    mock_public_row_1[16] = {"v": "Mô tả chi tiết căn nhà CMT8..."}
    mock_public_row_1[17] = {"v": "https://res.cloudinary.com/demo/image/upload/sample.jpg"}
    mock_public_row_1[34] = {"v": "SYS-1001"}

    mock_public_row_2 = list(mock_public_row_1)
    mock_public_row_2[0] = {"v": "1002"}
    mock_public_row_2[1] = {"v": "Căn Ba Tháng Hai Q10"}
    mock_public_row_2[5] = {"v": 12.0}
    mock_public_row_2[6] = {"v": "q10"}
    mock_public_row_2[7] = {"v": "Phường 12"}
    mock_public_row_2[34] = {"v": "SYS-1002"}

    mock_source_row_1 = [""] * 46
    mock_source_row_1[0] = "1"
    mock_source_row_1[1] = "CP"
    mock_source_row_1[3] = "SYS-1001"
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
    mock_pool_row_1[0] = "2001"
    mock_pool_row_1[5] = "Cách Mạng Tháng Tám"
    mock_pool_row_1[6] = "123"
    mock_pool_row_1[9] = "Nội dung chính CMT8 Q3 VIP"
    mock_pool_row_1[10] = "Mô tả chi tiết CMT8 Q3 VIP"
    mock_pool_row_1[11] = "6.5"
    mock_pool_row_1[13] = "100"
    mock_pool_row_1[27] = "https://res.cloudinary.com/demo/image/upload/sodo1_123.jpg"
    mock_pool_row_1[28] = "https://res.cloudinary.com/demo/image/upload/sodo2_123.jpg"
    mock_pool_row_1[29] = "https://res.cloudinary.com/demo/image/upload/mat_tien_123.jpg"
    mock_pool_row_1[40] = "https://res.cloudinary.com/demo/image/upload/interior_1.jpg"
    mock_pool_row_1[55] = "2001"
    mock_pool_row_1[72] = "SYS-1001"

    mock_pool_row_2 = list(mock_pool_row_1)
    mock_pool_row_2[0] = "2002"
    mock_pool_row_2[72] = "SYS-1002"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
        """)
        
        def handle_admin_sheets(route):
            url = route.request.url
            method = route.request.method
            if method == "GET":
                if "Source" in url:
                    response_body = {"values": [mock_source_row_1, mock_source_row_2]}
                else:
                    response_body = {"values": [mock_pool_row_1, mock_pool_row_2]}
                route.fulfill(content_type="application/json", body=json.dumps(response_body))
            else:
                route.continue_()

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

        page.route(lambda url: "spreadsheets" in url and "values" in url, handle_admin_sheets)
        page.route("**/gviz/tq**", handle_public_gviz)
        page.route("**/maps.google.com/**", lambda route: route.fulfill(status=200, body="<html>Dummy Maps</html>"))
        page.route("**/res.cloudinary.com/**", lambda route: route.fulfill(status=200, body="Dummy Image"))

        page.goto(f"http://localhost:{port}/index.html")
        page.wait_for_function("window.isSecureLoaded === true", timeout=5000)
        
        # Open card
        page.evaluate("openPoolS('SYS-1001')")
        
        # Go to slide 3
        page.evaluate("gotoImageEditorSlide(3)")
        
        # Evaluate state
        state = page.evaluate("""() => {
            const slides = window.imageEditorSlides;
            const activeIdx = window.activeImageEditorIndex;
            const activeSlide = slides[activeIdx];
            
            const facadeVal = document.getElementById('editCoverImgUrl')?.value || '';
            const normFacade = window.normalizeImgUrl(facadeVal);
            
            const coverVal = document.getElementById('editPublicCoverUrl')?.value || '';
            const normCover = window.normalizeImgUrl(coverVal);
            
            const sodoInputs = [
                document.getElementById('editSodo1Url'),
                document.getElementById('editSodo2Url'),
                document.getElementById('editSodo3Url'),
                document.getElementById('editSodo4Url'),
                document.getElementById('editSodo5Url')
            ];
            const normSodos = sodoInputs.map(input => window.normalizeImgUrl(input?.value || ''));
            
            const activeUrlNorm = window.normalizeImgUrl(activeSlide.url);
            const isActiveFacade = activeUrlNorm && activeUrlNorm === normFacade;
            const isActiveCover = activeUrlNorm && activeUrlNorm === normCover;
            const isActiveSodo = activeUrlNorm && normSodos.includes(activeUrlNorm);
            
            const btnPublic = document.getElementById('ctrlPublicBtn');
            
            return {
                slides,
                activeIdx,
                activeSlide,
                facadeVal,
                normFacade,
                coverVal,
                normCover,
                activeUrlNorm,
                isActiveFacade,
                isActiveCover,
                isActiveSodo,
                btnPublicDisabled: btnPublic?.disabled,
                btnPublicOpacity: btnPublic?.style.opacity,
                normSodos
            };
        }""")
        
        print("STATE:")
        import pprint
        pprint.pprint(state)
        
        browser.close()

if __name__ == '__main__':
    main()
