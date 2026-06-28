import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'static/js/lego_detail_admin.js'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    print("--- Section 1 (Line 2410-2460) ---")
    for idx in range(2409, min(2460, len(lines))):
        print(f"{idx+1}: {lines[idx]}", end="")
        
    print("\n\n--- Section 2 (Line 2780-2830) ---")
    for idx in range(2779, min(2830, len(lines))):
        print(f"{idx+1}: {lines[idx]}", end="")

if __name__ == '__main__':
    main()
