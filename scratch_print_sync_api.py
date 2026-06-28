import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    path = 'manager.py'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    idx = -1
    for i, line in enumerate(lines):
        if "@app.route('/api/sync-databases'" in line:
            idx = i
            break
            
    if idx == -1:
        print("Route /api/sync-databases not found")
        return
        
    print(f"Found route at line {idx+1}")
    for i in range(idx, min(idx + 100, len(lines))):
        print(f"{i+1}: {lines[i]}", end="")

if __name__ == '__main__':
    main()
