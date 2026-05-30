import os
import re

def search_keywords(directory, keywords):
    for root, dirs, files in os.walk(directory):
        # Ignore git, cache, and dist directories
        if any(ignored in root for ignored in ['.git', '__pycache__', 'dist', 'build', '.gemini', 'node_modules']):
            continue
        for file in files:
            if file.endswith(('.html', '.js', '.py', '.gs')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for kw in keywords:
                            if re.search(r'\b' + re.escape(kw) + r'\b', content, re.I):
                                print(f"Match found for '{kw}' in: {filepath}")
                except Exception as e:
                    pass

if __name__ == '__main__':
    search_keywords('.', ['upload', 'file', 'multipart', 'uploader', 'multer'])
