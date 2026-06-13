import os

for root, dirs, files in os.walk('.'):
    if '.git' in root or '__pycache__' in root or 'dist' in root or 'build' in root or 'scratch' in root:
        continue
    for file in files:
        if file.endswith('.py') or file.endswith('.js') or file.endswith('.html') or file.endswith('.gs'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for idx, line in enumerate(lines):
                    if 'SYS-' in line:
                        clean_line = line.strip().encode('ascii', errors='replace').decode('ascii')
                        print(f"{path}:{idx+1}: {clean_line}")
            except Exception as e:
                pass
