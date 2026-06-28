import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'pool_lego.py'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        import re
        matches = list(re.finditer(r'source_sheet_id', content))
        print(f"Found {len(matches)} matches for 'source_sheet_id' in pool_lego.py:")
        for m in matches:
            start = max(0, m.start() - 150)
            end = min(len(content), m.end() + 250)
            print(content[start:end].strip())
            print("-"*50)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
