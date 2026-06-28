import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'static/js/lego_detail_admin.js'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("--- Occurrences of 'huong' or 'editHuong' in lego_detail_admin.js ---")
        for i, line in enumerate(lines):
            line_str = line.strip()
            if 'huong' in line_str.lower() or 'edithuong' in line_str.lower():
                print(f"Line {i+1}: {line_str}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
