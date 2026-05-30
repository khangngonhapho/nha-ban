import re

keywords = ['drive', 'gapi', 'folder', 'client_id', 'oauth', 'upload']
matches = []

with open('index.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', line, re.I):
                matches.append(f"Line {i+1}: {line.strip()[:150]}")
                break

with open('scratch/matches_drive.txt', 'w', encoding='utf-8') as out:
    for m in matches:
        out.write(m + '\n')

print(f"Drive search complete. Found {len(matches)} matches. Written to scratch/matches_drive.txt")
