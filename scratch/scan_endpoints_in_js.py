import os
import sys
import re

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

folder = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/Thien Khoi Group - Nguon Hang - Chi Tiet New_files"

if not os.path.exists(folder):
    print("Folder does not exist")
    sys.exit(1)

# Look for any URL paths like /auth/... or auth/... or /refresh
for f in os.listdir(folder):
    if f.endswith((".js", "tải xuống")):
        fpath = os.path.join(folder, f)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_in:
                content = file_in.read()
            
            # Search for pattern auth/ or refresh
            matches_auth = re.findall(r'["\'][a-zA-Z0-9_\-\/]*auth\/[a-zA-Z0-9_\-\/]+["\']', content)
            matches_refresh = re.findall(r'["\'][a-zA-Z0-9_\-\/]*refresh[a-zA-Z0-9_\-\/]*["\']', content)
            
            if matches_auth or matches_refresh:
                print(f"\n[📄 File] {f}")
                if matches_auth:
                    print(f"  Auth matches: {list(set(matches_auth))[:5]}")
                if matches_refresh:
                    print(f"  Refresh matches: {list(set(matches_refresh))[:5]}")
        except Exception as e:
            print(f"Error reading {f}: {e}")
