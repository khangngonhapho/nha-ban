import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'manager.py'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i in range(2900, min(3000, len(lines))):
        print(f"{i+1}: {lines[i]}", end="")

if __name__ == '__main__':
    main()
