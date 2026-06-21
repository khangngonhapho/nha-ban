# -*- coding: utf-8 -*-
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
    print(f"Local server started on port {port}")
    server.serve_forever()
    return server

def main():
    project_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    
    time.sleep(1.5)
    
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        # Log all console messages
        page.on("console", lambda msg: print(f"[Console {msg.type}] {msg.text}"))
        
        # Inject admin bypass
        page.add_init_script("""
            localStorage.setItem('g_access_token', 'mock-admin-token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600000).toString());
            localStorage.setItem('client_name', 'Test Admin');
            localStorage.setItem('client_phone', '0901234567');
        """)
        
        # Mock Google Sheets API responses for Admin mode
        # We need mock responses for both Source and Pool sheets.
        # Let's fetch them from public sheet or mock them.
        # Wait, since the page will call sheets.googleapis.com, we can route those requests!
        
        # Let's load the actual public sheet rows first to use them as realistic test data
        public_sheet_id = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0'
        url = f"https://docs.google.com/spreadsheets/d/{public_sheet_id}/gviz/tq?tqx=out:json"
        res = requests = __import__('requests').get(url)
        match = __import__('re').search(r'google\.visualization\.Query\.setResponse\((.*)\);', res.text)
        public_rows = json.loads(match.group(1))['table']['rows'] if match else []
        
        # Let's construct mock Source rows and Pool rows from public rows
        mock_source_values = [[]] # Header row first
        # Header for Source (46 columns)
        mock_source_values[0] = ["Hinh_mat_tien", "Cu_phap", "Note", "id", "tieu_de", "dien_tich", "so_tang", "mat_tien", "gia", "quan", "phuong", "loai_hinh", "huong_nha", "duong_truoc_nha", "do_rong_hem", "tinh_trang_nha", "danh_gia", "ngu_tang_tret", "chdv", "mo_ta", "anh_1", "anh_2", "anh_3", "anh_4", "anh_5", "anh_6", "anh_7", "anh_8", "anh_9", "anh_10", "Last updated", "phuong_cu", "so_pn", "so_wc", "ten_duong", "gio_dang", "trang_thai", "System ID", "Hình Mặt Tiền", "Tiêu đề BDS", "Đăng BDS", "anh_11", "anh_12", "anh_13", "anh_14", "anh_15", "JSON_UI"]
        
        mock_pool_values = [[]] # Header row first
        # Header for Pool (94 columns)
        mock_pool_values[0] = ["Header"] * 94
        mock_pool_values[0][0] = "Mã Hàng"
        mock_pool_values[0][55] = "Mã Khang Ngô (ID)"
        mock_pool_values[0][72] = "System ID"
        mock_pool_values[0][93] = "JSON_UI"
        
        # Map Row 161 (Nguyễn Văn Nguyễn) to Source and Pool formats
        # We need its system_id = "SYS-20262320-305", id = "HWMHIMBZINVN"
        # Let's find Row 161
        target_public_row = None
        for r in public_rows:
            cells = r.get('c', [])
            row_str = " | ".join([str(c.get('v') if c else '') for c in cells])
            if "Nguyễn Văn Nguyễn" in row_str:
                target_public_row = r
                break
                
        if target_public_row:
            cells = target_public_row.get('c', [])
            def cv(cell):
                if not cell: return ''
                return cell.get('v') if cell.get('v') is not None else ''
            
            # Map to mock Source row
            sr = [""] * 47
            sr[3] = cv(cells[0]) # id
            sr[4] = cv(cells[1]) # tieu_de
            sr[5] = cv(cells[2]) # dien_tich
            sr[6] = cv(cells[3]) # so_tang
            sr[7] = cv(cells[4]) # mat_tien
            sr[8] = cv(cells[5]) # gia
            sr[9] = cv(cells[6]) or "q1" # quan (We force q1 to simulate correct input or mock)
            sr[10] = cv(cells[7]) # phuong
            sr[37] = cv(cells[34]) # System ID
            sr[46] = cv(cells[43]) # JSON_UI (col 47, index 46)
            mock_source_values.append(sr)
            
            # Map to mock Pool row
            pr = [""] * 94
            pr[0] = "TKW7F7IJ" # Mã Hàng
            pr[55] = "TKW7F7IJ" # Mã Khang Ngô (ID)
            pr[72] = cv(cells[34]) # System ID
            pr[93] = cv(cells[43]) # JSON_UI
            mock_pool_values.append(pr)
            
        print("Mock Source rows:", len(mock_source_values))
        print("Mock Pool rows:", len(mock_pool_values))
        
        # Route Google Sheets API
        def handle_sheets_api(route):
            url = route.request.url
            if "Source" in url:
                print("Mocking Source Sheet API call...")
                route.fulfill(content_type="application/json", body=json.dumps({"values": mock_source_values}))
            elif "Pool" in url:
                print("Mocking Pool Sheet API call...")
                route.fulfill(content_type="application/json", body=json.dumps({"values": mock_pool_values}))
            else:
                route.continue_()
                
        page.route("**/spreadsheets/**", handle_sheets_api)
        
        # Mock config
        with open('settings.json', 'r', encoding='utf-8') as f:
            settings_cfg = json.load(f)
            
        def handle_api_config(route):
            route.fulfill(content_type="application/json", body=json.dumps({"status": "success", "config": settings_cfg}))
            
        page.route("**/api/config**", handle_api_config)
        
        client_url = f"http://localhost:{port}/index.html"
        print(f"Navigating to {client_url}")
        page.goto(client_url, wait_until="networkidle")
        
        # Verify cards
        page.wait_for_selector(".card", timeout=10000)
        cards_count = page.locator(".card").count()
        print(f"Admin mode loaded cards: {cards_count}")
        
        # Inspect window.DATA
        data_state = page.evaluate("""() => {
            return window.DATA.map(p => ({
                id: p.id,
                t: p.t,
                json_ui_parsed: p.json_ui_parsed,
                q: p.q,
                duong_truoc_nha: p.duong_truoc_nha
            }));
        }""")
        print("Admin DATA in window.DATA:", json.dumps(data_state, ensure_ascii=False, indent=2))
        
        browser.close()

if __name__ == "__main__":
    main()
