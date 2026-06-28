import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'index.html'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i in range(482, min(560, len(lines))):
            print(f"{i+1}: {lines[i]}", end="")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
