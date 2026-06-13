import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

log_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/full_sources_load_log.txt"

if not os.path.exists(log_path):
    print("Log file not found")
    sys.exit(1)

with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== Looking for backend.thienkhoi.com/product/v1/property requests ===")
for idx, line in enumerate(lines):
    if "backend.thienkhoi.com/product/v1/property" in line and "[Req]" in line:
        print(f"Line {idx+1}: {line.strip()}")
        # Let's print the next few lines in case headers are logged or let's read the logs
        # Actually our script inspect_full_loading.py logs:
        # log(f"[Req] {req.method} {req.url}")
        # But it does not log headers to console/log directly.
        # Oh, wait! In inspect_full_loading.py:
        # page.on("request", lambda req: log(f"[Req] {req.method} {req.url}"))
        # It did not log headers.
        # But wait! We can write a script to load page and log the headers specifically for this URL.
        # Let's write a script to find the request in page.on("request") and print headers.
