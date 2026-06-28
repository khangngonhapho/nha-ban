import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'docs/system_architecture_deployment.md'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        import re
        matches = list(re.finditer(r'(LỊCH SỬ THAY ĐỔI|Change Log)', content, re.IGNORECASE))
        print(f"Found {len(matches)} matches:")
        for m in matches:
            start = max(0, m.start() - 100)
            end = min(len(content), m.end() + 500)
            print(content[start:end].strip())
            print("-"*50)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
