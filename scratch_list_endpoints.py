import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'manager.py'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("--- Flask Routes in manager.py ---")
        for i, line in enumerate(lines):
            line_str = line.strip()
            if '@app.route' in line_str or 'def ' in line_str and i > 0 and '@app.' in lines[i-2]:
                print(f"Line {i-1}: {lines[i-2].strip()}")
                print(f"Line {i}: {lines[i-1].strip()}")
                print(f"Line {i+1}: {line_str}")
                print()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
