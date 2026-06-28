import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'manager.py'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("--- Occurrences in manager.py ---")
        for i, line in enumerate(lines):
            line_str = line.strip()
            if any(term in line_str.lower() for term in ['huong', 'direction', 'criteria', 'save_']):
                print(f"Line {i+1}: {line_str}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
