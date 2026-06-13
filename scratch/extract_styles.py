import re
import sys

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find style block
style_match = re.search(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
if style_match:
    styles = style_match.group(1)
    with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/extracted_styles.css', 'w', encoding='utf-8') as f_out:
        f_out.write(styles)
    print(f"Extracted {len(styles)} characters of CSS to scratch/extracted_styles.css")
else:
    print("No style block found!")
