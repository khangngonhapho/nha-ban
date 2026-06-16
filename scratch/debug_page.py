import sys
import os
import time
import socket
import threading
import http.server
import socketserver
from playwright.sync_api import sync_playwright

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
    server.serve_forever()

def main():
    project_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
    port = get_free_port()
    server_thread = threading.Thread(target=run_server, args=(port, project_dir), daemon=True)
    server_thread.start()
    time.sleep(1.0)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Print all console messages and page errors
        page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

        # Inject admin session
        page.add_init_script("""
            localStorage.setItem('isAdminSession', 'true');
            localStorage.setItem('g_access_token', 'mock_google_oauth_token');
            localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
        """)

        url = f"http://localhost:{port}/index.html"
        print(f"Navigating to {url}...")
        try:
            page.goto(url, wait_until="load", timeout=10000)
            print("Page loaded. Checking global variables after 2 seconds...")
            time.sleep(2.0)
            
            # Print state of window variables
            vars_state = page.evaluate("""() => {
                return {
                    isAdmin: window.isAdmin,
                    initLegoApp: typeof window.initLegoApp,
                    LegoState: typeof window.LegoState,
                    isSecureLoaded: window.isSecureLoaded,
                    isDataLoaded: window.isDataLoaded,
                    DATA_length: window.DATA ? window.DATA.length : null,
                    activeMode: window.activeMode
                };
            }""")
            print("Globals:", vars_state)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
