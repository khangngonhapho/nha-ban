import os

found = False
for root, dirs, files in os.walk('.'):
    if '.git' in root or '__pycache__' in root or 'dist' in root or 'build' in root or 'scratch' in root:
        continue
    for file in files:
        if file.endswith('.py'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'curator_html_data' in content and 'write' in content:
                    print(f"Generator found: {path}")
                    found = True
            except Exception:
                pass

if not found:
    print("No auto-generator found. curator_html_data.py is likely updated manually or by a simple script.")
