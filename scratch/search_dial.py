import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

def find_context(path, word):
    if not os.path.exists(path):
        return
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if word.lower() in line.lower():
                print(f'{path}:{i+1}: {line.strip()}')
    except Exception:
        pass

find_context('./static/css/global.css', 'carousel-slide-item')
