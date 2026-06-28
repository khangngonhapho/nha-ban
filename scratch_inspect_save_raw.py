import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    with open('pool_lego.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    idx = content.find('def get_safe_col_name')
    if idx == -1:
        print("get_safe_col_name not found")
        return
        
    start_line = content[:idx].count('\n') + 1
    print(f"get_safe_col_name starts at line: {start_line}")
    
    lines = content.split('\n')
    for i in range(start_line - 1, start_line + 30):
        if i < len(lines):
            print(f"{i+1}: {lines[i]}")

if __name__ == '__main__':
    main()
