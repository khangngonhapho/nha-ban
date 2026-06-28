import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    with open('fetcher.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Search for get_val_by_label
    idx = content.find('def get_val_by_label')
    if idx == -1:
        print("get_val_by_label not found")
        return
        
    start_line = content[:idx].count('\n') + 1
    print(f"get_val_by_label starts at line: {start_line}")
    
    lines = content.split('\n')
    for i in range(start_line - 1, start_line + 40):
        if i < len(lines):
            print(f"{i+1}: {lines[i]}")

if __name__ == '__main__':
    main()
