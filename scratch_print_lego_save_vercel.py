import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'static/js/lego_detail_admin.js'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    print("--- Section 4 (Line 2950-3080) ---")
    for idx in range(2949, min(3080, len(lines))):
        print(f"{idx+1}: {lines[idx]}", end="")

if __name__ == '__main__':
    main()
