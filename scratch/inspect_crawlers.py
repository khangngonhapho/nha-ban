import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

filepath = "manager.py"
if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = list(f)
    print("=== manager.py around line 3312 ===")
    for idx in range(3300, 3325):
        if idx < len(lines):
            print(f"{idx+1}: {lines[idx].rstrip()}")
            
    print("\n=== manager.py around line 3550 ===")
    for idx in range(3535, 3565):
        if idx < len(lines):
            print(f"{idx+1}: {lines[idx].rstrip()}")
else:
    print("manager.py not found")
