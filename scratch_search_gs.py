import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'pool_backend_v3.gs'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print("--- Occurrences in pool_backend_v3.gs ---")
        found = False
        for i, line in enumerate(lines):
            line_str = line.strip()
            if 'huong' in line_str.lower():
                print(f"Line {i+1}: {line_str}")
                found = True
        if not found:
            print("No occurrences of 'huong' found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
