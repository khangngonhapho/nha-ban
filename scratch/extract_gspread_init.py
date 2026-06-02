import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

with open('curator_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# let's look at lines 2040 to 2090
for i in range(2039, min(2095, len(lines))):
    print(f"{i+1}: {lines[i].strip()}")
