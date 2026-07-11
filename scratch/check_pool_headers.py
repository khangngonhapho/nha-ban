import sys

# Set standard output encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

with open("pool_lego.py", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')
for i, line in enumerate(lines):
    if "POOL_HEADERS = [" in line or "POOL_HEADERS =" in line:
        print(f"\nLine {i+1}: {line}")
        # Print next 35 lines
        for j in range(1, 100):
            if i + j < len(lines):
                print(lines[i+j])
                if "]" in lines[i+j] and not "'" in lines[i+j] and not '"' in lines[i+j]:
                    break
