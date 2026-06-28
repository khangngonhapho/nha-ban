import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

def main():
    pattern = re.compile(r'dt_thuc_te|dt_tren_so|diện tích thực tế|thông tin', re.IGNORECASE)
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
                    
    print(f"Found {len(results)} matches:")
    for r in results:
        print(f"File: {r[0]} | Line {r[1]}: {r[2]}")

if __name__ == '__main__':
    main()
