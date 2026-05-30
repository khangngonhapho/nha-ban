import re

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

patterns = [
    r'edit-img-card',
    r'edit-img-pub-cb',
    r'edit-img-mattien-btn',
    r'edit-img-cover-btn',
    r'edit-img-pub-cb',
]

with open('search_results.txt', 'w', encoding='utf-8') as out:
    for idx, line in enumerate(lines, 1):
        for pattern in patterns:
            if re.search(pattern, line):
                out.write(f"{idx}: {line.strip()}\n")
                break
print("Done! Results in search_results.txt")
