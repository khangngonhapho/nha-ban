import os
import sys
import time
import socket
import threading
import http.server
import socketserver
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

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Inject global error logger before script loads
        page.add_init_script("""
            window.onerror = function(message, source, lineno, colno, error) {
                console.log("SYNTAX ERROR DETECTED: " + message + " at " + source + " line " + lineno + ":" + colno);
            };
        """)
        
        page.on("pageerror", lambda err: print(f"PAGE ERROR MESSAGE: {err.message}\nSTACK:\n{err.stack}"))
        page.on("console", lambda msg: print(f"CONSOLE [{msg.type}]: {msg.text}"))
        
        print("Navigating to index.html...")
        page.goto(f"http://localhost:{port}/index.html")
        time.sleep(2)
        browser.close()

if __name__ == '__main__':
    main()
