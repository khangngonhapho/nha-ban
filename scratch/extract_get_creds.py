import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

with open('curator_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

found_idx = -1
for idx, line in enumerate(lines):
    if "def get_google_credentials" in line:
        found_idx = idx
        break

if found_idx != -1:
    print(f"Found def get_google_credentials at line {found_idx+1}")
    for i in range(max(0, found_idx-5), min(len(lines), found_idx + 40)):
        print(f"{i+1}: {lines[i].strip()}")
else:
    print("def get_google_credentials not found")
