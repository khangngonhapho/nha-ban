import sys

sys.stdout.reconfigure(encoding='utf-8')
content = open('index.html', encoding='utf-8').read()
for i, line in enumerate(content.splitlines()):
    if 'loaddata' in line.lower():
        print(f"{i+1}: {line}")
