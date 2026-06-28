import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'static/js/lego_detail_client.js'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print("--- Occurrences in lego_detail_client.js ---")
        for i, line in enumerate(lines):
            line_str = line.strip()
            if any(term in line_str.lower() for term in ['thông tin', 'dien_tich', 'so_tang', 'phuong', 'huong', 'sổ']):
                print(f"Line {i+1}: {line_str}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
