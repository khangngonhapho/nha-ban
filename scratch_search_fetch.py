import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'static/js/lego_detail_admin.js'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        import re
        matches = re.finditer(r"fetch\(", content)
        print("--- fetch calls in lego_detail_admin.js ---")
        for m in matches:
            start_idx = max(0, m.start() - 100)
            end_idx = min(len(content), m.end() + 300)
            print(f"Position {m.start()}:")
            print(content[start_idx:end_idx].strip())
            print("-"*40)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
