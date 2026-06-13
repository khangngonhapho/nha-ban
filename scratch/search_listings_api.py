with open('curator_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'def get_listings' in line or '/api/listings' in line:
        for i in range(max(0, idx-2), min(len(lines), idx+60)):
            clean_line = lines[i].strip().encode('ascii', errors='replace').decode('ascii')
            print(f"{i+1}: {clean_line}")
        break
