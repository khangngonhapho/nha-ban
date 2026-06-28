import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

def main():
    pattern = re.compile(r'/api/listings', re.IGNORECASE)
    results = []
    
    for root, dirs, files in os.walk('static/js'):
        for file in files:
            if file.endswith('.js'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern.search(line):
                                results.append((path, line_num, line.strip()))
                except Exception:
                    pass
                    
    # Also check curator.html and index.html in the root
    for file in ['curator.html', 'index.html']:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if pattern.search(line):
                        results.append((file, line_num, line.strip()))
        except Exception:
            pass

    print(f"Found {len(results)} matches for /api/listings:")
    for r in results:
        print(f"File: {r[0]} | Line {r[1]}: {r[2]}")

if __name__ == '__main__':
    main()
