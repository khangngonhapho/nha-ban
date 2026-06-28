import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'static/js/lego_detail_admin.js'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Search for PUT requests to the local api
        import re
        matches = re.finditer(r"['\"`]/api/listings/.*?['\"`]", content)
        for m in matches:
            start_idx = max(0, m.start() - 200)
            end_idx = min(len(content), m.end() + 1000)
            print(f"Match found at position {m.start()}:")
            print(content[start_idx:end_idx])
            print("="*50)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
