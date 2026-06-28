import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'SOURCE_OF_TRUTH.md'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        found = False
        for idx, line in enumerate(lines):
            if "## 7. 📝 LỊCH SỬ THAY ĐỔI (Change Log)" in line:
                found = True
                print(f"Changelog starts at line {idx+1}:")
                for j in range(idx, min(idx + 100, len(lines))):
                    print(f"{j+1}: {lines[j]}", end="")
                break
        if not found:
            print("Not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
