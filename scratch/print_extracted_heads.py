import sys

def print_heads(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if '// ===' in line:
            print(f"Line {i+1}: {line.strip()}")
            # print next 3 lines
            for j in range(1, 4):
                if i + j < len(lines):
                    print(f"  + {j}: {lines[i+j].strip()}")

if __name__ == '__main__':
    print_heads('static/js/lego_detail_admin.js')
