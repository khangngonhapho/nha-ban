import os
import sys
import glob

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

import shutil
from google.oauth2 import service_account
import google.auth.transport.requests

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CREDENTIALS_FILE = os.path.join(PROJECT_ROOT, "credentials.json")

def test_selection_logic():
    home_dir = os.path.expanduser("~")
    bds_home_dir = os.path.join(home_dir, ".bds_khangngo")
    home_credentials_path = os.path.abspath(os.path.join(bds_home_dir, "credentials.json"))

    target_dirs = [
        PROJECT_ROOT,
        os.path.dirname(home_credentials_path),
        os.path.abspath(os.path.join(PROJECT_ROOT, "..")),
        os.path.abspath(os.path.join(PROJECT_ROOT, "..", "..")),
        os.path.abspath(os.path.join(PROJECT_ROOT, "..", "admin-nha-ban", "automation")),
        os.getcwd(),
        os.path.abspath(os.path.join(os.getcwd(), ".."))
    ]
    
    # Collect all candidate files
    candidates = []
    for d in target_dirs:
        if not os.path.exists(d):
            continue
        # Check credentials.json
        p_cred = os.path.abspath(os.path.join(d, "credentials.json"))
        if os.path.exists(p_cred):
            candidates.append(p_cred)
        # Check khangngo-admin-*.json
        for p_wild in glob.glob(os.path.join(d, "khangngo-admin-*.json")):
            candidates.append(os.path.abspath(p_wild))
            
    # De-duplicate while preserving order
    candidates = list(dict.fromkeys(candidates))
    print("Found candidate files:", candidates)
    
    req = google.auth.transport.requests.Request()
    valid_creds = None
    working_path = None
    
    for path in candidates:
        print(f"Checking candidate: {path}...")
        try:
            scopes = [
                'https://www.googleapis.com/auth/drive.file',
                'https://www.googleapis.com/auth/spreadsheets'
            ]
            creds = service_account.Credentials.from_service_account_file(path, scopes=scopes)
            # Try to verify online
            try:
                creds.refresh(req)
                print(f"  -> SUCCESS: Valid credentials key!")
                valid_creds = creds
                working_path = path
                break
            except Exception as e_refresh:
                err_msg = str(e_refresh)
                print(f"  -> Refresh error: {err_msg}")
                if "invalid_grant" in err_msg or "invalid_client" in err_msg or "signature" in err_msg.lower():
                    print("  -> Confirmed BAD key. Skipping.")
                    continue
                else:
                    # Network or other error, assume it might be valid
                    print("  -> Network/other error. Keeping as fallback.")
                    valid_creds = creds
                    working_path = path
                    break
        except Exception as e_load:
            print(f"  -> Load error: {e_load}")
            
    if valid_creds and working_path:
        print(f"Selected working credentials from: {working_path}")
        # Copy to default credentials.json if it is not already
        if working_path != CREDENTIALS_FILE:
            print(f"Copying working file to {CREDENTIALS_FILE}...")
            shutil.copy2(working_path, CREDENTIALS_FILE)
            shutil.copy2(working_path, CREDENTIALS_FILE + ".bak")
            
        # Copy to Home Cache
        if working_path != home_credentials_path:
            print(f"Copying working file to Home Cache: {home_credentials_path}...")
            os.makedirs(os.path.dirname(home_credentials_path), exist_ok=True)
            shutil.copy2(working_path, home_credentials_path)
            shutil.copy2(working_path, home_credentials_path + ".bak")
    else:
        print("No working credentials found!")

test_selection_logic()
