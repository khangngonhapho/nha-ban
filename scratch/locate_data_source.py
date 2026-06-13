import os
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

fn = "Thien Khoi Group - Nguon Hang - Danh Sach.html"
path = f"d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/{fn}"

if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print(f"Content length: {len(content)}")
    
    # Find positions of "sources/"
    term = "sources/"
    start = 0
    matches_count = 0
    while True:
        pos = content.find(term, start)
        if pos == -1:
            break
        print(f"\n--- Match {matches_count + 1} at position {pos} ---")
        # Print 200 characters before and 300 characters after
        snippet = content[max(0, pos - 150): min(len(content), pos + 250)]
        print(snippet)
        matches_count += 1
        start = pos + len(term)
        if matches_count >= 5:
            print("\n... and more matches ...")
            break
else:
    print(f"File {fn} does not exist.")
