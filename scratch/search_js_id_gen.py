import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk("static/js"):
    for f in files:
        if f.endswith('.js'):
            fp = os.path.join(root, f)
            with open(fp, 'r', encoding='utf-8') as file:
                content = file.read()
                if "gen" in content or "id" in content or "Khang" in content:
                    # Let's search line by line
                    file.seek(0)
                    for i, line in enumerate(file):
                        if any(term in line for term in ["gen_id", "genId", "generateId", "KhangNgo", "Khang Ngô", "digit_map"]):
                            print(f"{fp} Line {i+1}: {line.strip()}")
