with open('curator.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'Notification' in line or 'showBanner' in line or 'toast' in line or 'alert' in line:
        clean_line = line.strip().encode('ascii', errors='replace').decode('ascii')
        if len(clean_line) < 120 and 'function' in clean_line:
            print(f"{idx+1}: {clean_line}")
