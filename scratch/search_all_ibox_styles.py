import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's find every occurrence of .ibox or .crow in style blocks
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if style_match:
    styles = style_match.group(1)
    lines = styles.split('\n')
    for i, line in enumerate(lines):
        if '.ibox' in line or '.crow' in line:
            print(f"Line {i+22}: {line.strip()}")
            # print surrounding styles
            start = max(0, i - 2)
            end = min(len(lines), i + 8)
            for j in range(start, end):
                print(f"  {j+22}: {lines[j]}")
            print("---")
else:
    print("No style tag found")
