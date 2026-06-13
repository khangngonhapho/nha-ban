import os

def search_text_in_files(text, path='.'):
    results = []
    for root, dirs, files in os.walk(path):
        if 'node_modules' in root or '.git' in root or '__pycache__' in root or 'dist' in root or 'build' in root:
            continue
        for file in files:
            if file.endswith(('.html', '.py', '.js', '.txt')):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            if text.lower() in line.lower():
                                results.append((full_path, i, line.strip()))
                except Exception as e:
                    pass
    return results

if __name__ == '__main__':
    search_queries = ["status 400", "returned status", "Lỗi lưu thay đổi", "Google Sheet API"]
    for query in search_queries:
        print(f"=== Searching for: '{query}' ===")
        res = search_text_in_files(query)
        for filepath, line_no, content in res:
            print(f"{filepath}:{line_no}: {content[:120]}")
        print()
