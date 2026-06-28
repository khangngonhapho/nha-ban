import sys

sys.stdout.reconfigure(encoding='utf-8')

def search_fetcher():
    path = 'fetcher.py'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("--- Occurrences in fetcher.py ---")
        for i, line in enumerate(lines):
            line_str = line.strip()
            # print lines containing "huong" or similar terms
            if any(term in line_str.lower() for term in ['huong', 'direction', 'criteria', 'house_detail', 'parse_']):
                print(f"Line {i+1}: {line_str}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    search_fetcher()
