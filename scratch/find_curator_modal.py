import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's search for divs with id or class containing curator or editor, or any overlay/modal elements
print("=== Modal IDs and classes in HTML ===")
divs = re.findall(r'<div\s+[^>]*id="[^"]*(?:modal|curator|editor|overlay)[^"]*"[^>]*>', html, re.IGNORECASE)
for d in divs:
    print(d)

# Let's search for css related to admin editing panel/modal
print("\n=== Style definitions for admin sections ===")
style_block_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
if style_block_match:
    styles = style_block_match.group(1)
    # find lines matching admin, curator, editor
    lines = styles.split('\n')
    for i, line in enumerate(lines):
        if any(w in line.lower() for w in ['admin', 'curator', 'editor', 'edit-']) and '{' in line:
            print(f"Line {i+22}: {line.strip()}")
            # print up to 5 lines of body
            for j in range(i+1, min(i+10, len(lines))):
                print(f"  {lines[j].rstrip()}")
                if '}' in lines[j]:
                    break
            print("---")
