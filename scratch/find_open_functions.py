import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for "function openS" or "openS =" or "openPoolS ="
lines = content.split('\n')
for name in ['openS', 'openPoolS']:
    print(f"=== Searching for function: {name} ===")
    found = False
    for i, line in enumerate(lines):
        if f'function {name}' in line or f'{name} = function' in line or f'const {name}' in line or f'window.{name}' in line:
            print(f"Found {name} at line {i+1}: {line.strip()}")
            # print next 100 lines
            for j in range(i, min(i+120, len(lines))):
                print(f"  {j+1}: {lines[j]}")
            found = True
            break
    if not found:
        print(f"Could not find {name}")
    print("\n")
