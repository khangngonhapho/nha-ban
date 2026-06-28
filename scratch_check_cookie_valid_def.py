import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'fetcher.py'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        idx = content.find('def check_cookie_valid')
        if idx == -1:
            print("check_cookie_valid not found")
            return
            
        start_line = content[:idx].count('\n') + 1
        print(f"check_cookie_valid starts at line: {start_line}")
        
        lines = content.split('\n')
        for i in range(start_line - 1, start_line + 40):
            if i < len(lines):
                print(f"{i+1}: {lines[i]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
