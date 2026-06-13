import sys

sys.stdout.reconfigure(encoding='utf-8')
content = open('index.html', encoding='utf-8').read()
for i, line in enumerate(content.splitlines()):
    if 'loading' in line.lower() or 'spinner' in line.lower() or 'hide' in line.lower():
        # Only print if it looks relevant to controlling visibility
        if any(term in line.lower() for term in ['document', 'style', 'class', 'remove', 'add', 'hide', 'show']):
            print(f"{i+1}: {line}")
