import os

for root, dirs, files in os.walk('.'):
    if '.git' in root or '__pycache__' in root or 'dist' in root or 'build' in root or 'scratch' in root:
        continue
    for file in files:
        if file.endswith('.py') or file.endswith('.md') or file.endswith('.txt'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'chép đè chỉ dành riêng' in content or 'chép đè hình ảnh' in content.lower():
                    print(f"Found in {path}")
            except Exception:
                pass
