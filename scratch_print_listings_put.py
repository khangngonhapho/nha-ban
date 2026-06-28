import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'manager.py'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Search for app.route('/api/listings/<tk_id>'
    idx = -1
    for i, line in enumerate(lines):
        if "@app.route('/api/listings/<tk_id>'" in line:
            idx = i
            break
            
    if idx == -1:
        print("Route /api/listings/<tk_id> not found")
        return
        
    print(f"Found route at line {idx+1}")
    for i in range(idx, idx + 150):
        if i < len(lines):
            print(f"{i+1}: {lines[i]}", end="")

if __name__ == '__main__':
    main()
