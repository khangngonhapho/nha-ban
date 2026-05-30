import sys

# Configure stdout to use utf-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open("curator.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

search_ids = ["edit-tieu-de-public", "edit-mo-ta-public", "edit-phuong-cu-ai"]
for idx, line in enumerate(lines):
    for s_id in search_ids:
        if s_id in line:
            print(f"Line {idx+1}: {line.strip()}")

