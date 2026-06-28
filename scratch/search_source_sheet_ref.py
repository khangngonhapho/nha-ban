import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk("."):
    if any(p in root for p in [".git", "__pycache__", "build", "dist", "dist (1)", "scratch"]):
        continue
    for f in files:
        if f.endswith(('.py', '.gs')):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8') as file:
                    for i, line in enumerate(file):
                        if "Source" in line or "1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0" in line:
                            # Print only matching lines, replace errors
                            print(f"{fp} Line {i+1}: {line.strip()}")
            except Exception as e:
                pass
