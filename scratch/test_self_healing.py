import os
import sys

# Add root folder to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Reconfigure output encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

import curator_server

ws_file = "credentials.json"
ws_bak = "credentials.json.bak"

print("--- STARTING SELF-HEALING TEST ---")

# Backup existing files by renaming
has_ws = os.path.exists(ws_file)
has_bak = os.path.exists(ws_bak)

if has_ws:
    os.rename(ws_file, ws_file + ".test_bak")
    print(f"Temporarily renamed {ws_file}")
if has_bak:
    os.rename(ws_bak, ws_bak + ".test_bak")
    print(f"Temporarily renamed {ws_bak}")

try:
    print("Running get_google_credentials() with missing workspace files...")
    creds = curator_server.get_google_credentials()
    print("Resulting credentials object:", creds)
    print("Does workspace credentials.json exist now?", os.path.exists(ws_file))
finally:
    # Restore workspace files
    if os.path.exists(ws_file):
        os.remove(ws_file)
    if os.path.exists(ws_file + ".test_bak"):
        os.rename(ws_file + ".test_bak", ws_file)
        print("Restored original credentials.json")
    if os.path.exists(ws_bak + ".test_bak"):
        os.rename(ws_bak + ".test_bak", ws_bak)
        print("Restored original credentials.json.bak")
        
print("--- TEST COMPLETED ---")
