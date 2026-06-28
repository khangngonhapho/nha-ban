import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'static/js/lego_detail_admin.js'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    print("--- Section 3 (Line 2831-2950) ---")
    for idx in range(2830, min(2950, len(lines))):
        print(f"{idx+1}: {lines[idx]}", end="")

if __name__ == '__main__':
    main()
