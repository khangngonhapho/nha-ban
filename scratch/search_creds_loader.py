with open('curator_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'CREDENTIALS' in line or 'credentials' in line or 'get_google_credentials' in line:
        clean_line = line.strip().encode('ascii', errors='replace').decode('ascii')
        print(f"{idx+1}: {clean_line}")
