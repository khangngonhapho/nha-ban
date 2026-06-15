import os
import sys
import time
import socket
import threading
import http.server
import socketserver
from playwright.sync_api import sync_playwright

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Find a free port
def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

# Simple HTTP request handler serving BDS-KhangNgo
class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging to keep output clean
        pass

def run_server(port, directory):
    # Change current working directory to serve files correctly
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
    
    # 1. Start local server
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    
    # Give the server a moment to start
    time.sleep(1)
    
    url = f"http://localhost:{port}/index.html"
    print(f"Testing URL: {url}")
    
    test_success = True
    
    # 2. Run Playwright Tests
    with sync_playwright() as p:
        # Launch Browser headless
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        
        # --- DESKTOP VIEWPORT TEST (1280x800) ---
        print("\n--- Running Desktop Test (1280x800) ---")
        desktop_context = browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        desktop_page = desktop_context.new_page()
        
        try:
            print(f"Navigating to {url} ...")
            response = desktop_page.goto(url, wait_until="networkidle", timeout=30000)
            print(f"Response status: {response.status}")
            
            # Check title
            title = desktop_page.title()
            print(f"Page Title: {title}")
            assert title == "Khang Ngô Nhà Phố", f"Expected title 'Khang Ngô Nhà Phố', got '{title}'"
            
            # Check CSS variables (proves global.css is loaded and parsed)
            red_color = desktop_page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--red').trim()")
            print(f"CSS Variable --red value: {red_color}")
            assert red_color == "#c0392b", f"Expected --red to be '#c0392b', got '{red_color}'"
            
            # Save Desktop Screenshot
            screenshot_path = os.path.join(artifacts_dir, "desktop_view.png")
            desktop_page.screenshot(path=screenshot_path)
            print(f"Desktop screenshot saved to {screenshot_path}")
            
        except Exception as e:
            print(f"[ERROR] Desktop Test Failed: {e}")
            test_success = False
        finally:
            desktop_context.close()
            
        # --- MOBILE VIEWPORT TEST (375x812, hasTouch=True) ---
        print("\n--- Running Mobile Test (375x812) ---")
        mobile_context = browser.new_context(
            viewport={"width": 375, "height": 812},
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        )
        mobile_page = mobile_context.new_page()
        
        try:
            print(f"Navigating to {url} ...")
            response = mobile_page.goto(url, wait_until="networkidle", timeout=30000)
            print(f"Response status: {response.status}")
            
            # Check title
            title = mobile_page.title()
            print(f"Page Title: {title}")
            assert title == "Khang Ngô Nhà Phố", f"Expected title 'Khang Ngô Nhà Phố', got '{title}'"
            
            # Check CSS variables (proves global.css is loaded and parsed)
            red_color = mobile_page.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--red').trim()")
            print(f"CSS Variable --red value: {red_color}")
            assert red_color == "#c0392b", f"Expected --red to be '#c0392b', got '{red_color}'"
            
            # Save Mobile Screenshot
            screenshot_path = os.path.join(artifacts_dir, "mobile_view.png")
            mobile_page.screenshot(path=screenshot_path)
            print(f"Mobile screenshot saved to {screenshot_path}")
            
        except Exception as e:
            print(f"[ERROR] Mobile Test Failed: {e}")
            test_success = False
        finally:
            mobile_context.close()
            
        browser.close()
        
    if test_success:
        print("\n[🎉 ALL E2E TESTS PASSED SUCCESSFULLY]")
        sys.exit(0)
    else:
        print("\n[❌ SOME E2E TESTS FAILED]")
        sys.exit(1)

if __name__ == "__main__":
    main()
