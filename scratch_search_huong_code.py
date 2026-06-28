import sys
import os
import re

sys.stdout.reconfigure(encoding='utf-8')

def search_files(directory):
    pattern = re.compile(r'huong', re.IGNORECASE)
    results = []
    
    for root, dirs, files in os.walk(directory):
        # Exclude node_modules, .git, and build directories
        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'build', 'dist', '__pycache__', 'Thien Khoi Group - Nguon Hang - Huong Jun28_files']]
        for file in files:
            if file.endswith(('.py', '.js', '.html', '.gs')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern.search(line):
                                results.append((path, line_num, line.strip()))
                except Exception as e:
                    pass
    return results

if __name__ == '__main__':
    res = search_files('.')
    print(f"Found {len(res)} matches:")
    # Group by file
    by_file = {}
    for r in res:
        by_file.setdefault(r[0], []).append((r[1], r[2]))
        
    for file, matches in by_file.items():
        print(f"\nFile: {file}")
        for num, line in matches[:15]: # Limit to first 15 matches per file
            print(f"  Line {num}: {line}")
        if len(matches) > 15:
            print(f"  ... and {len(matches) - 15} more matches")
