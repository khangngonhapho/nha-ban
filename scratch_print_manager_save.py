import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'manager.py'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    start = 2835
    end = 2915
    for i in range(start - 1, end):
        if i < len(lines):
            print(f"{i+1}: {lines[i]}", end="")

if __name__ == '__main__':
    main()
