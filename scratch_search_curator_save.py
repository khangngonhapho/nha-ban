import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'curator.html'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Print around line 2770
        print("--- curator.html around line 2770 ---")
        for i in range(2755, min(2810, len(lines))):
            print(f"{i+1}: {lines[i]}", end="")
            
        print("\n\n--- curator.html around line 2857 ---")
        for i in range(2840, min(2880, len(lines))):
            print(f"{i+1}: {lines[i]}", end="")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
