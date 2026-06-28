import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'static/js/lego_detail_admin.js'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i in range(2529, min(2570, len(lines))):
        print(f"{i+1}: {lines[i]}", end="")

if __name__ == '__main__':
    main()
