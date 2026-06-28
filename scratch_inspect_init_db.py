import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'pool_lego.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    idx = content.find('def init_db')
    if idx == -1:
        print("init_db not found")
        return
        
    start_line = content[:idx].count('\n') + 1
    print(f"init_db starts at line: {start_line}")
    
    lines = content.split('\n')
    for i in range(start_line - 1, start_line + 120):
        if i < len(lines):
            print(f"{i+1}: {lines[i]}")

if __name__ == '__main__':
    main()
