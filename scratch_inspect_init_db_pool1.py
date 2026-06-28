import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'pool_lego.py'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    lines = content.split('\n')
    for i in range(649, min(750, len(lines))):
        print(f"{i+1}: {lines[i]}")

if __name__ == '__main__':
    main()
