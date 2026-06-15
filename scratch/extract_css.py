import os
import shutil

html_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html"
backup_path = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/index.html.bak"
css_dir = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/static/css"
css_path = os.path.join(css_dir, "global.css")

# 1. Create static/css folder if not exists
if not os.path.exists(css_dir):
    os.makedirs(css_dir)
    print(f"Created directory: {css_dir}")

# 2. Backup index.html
shutil.copy2(html_path, backup_path)
print(f"Backed up index.html to {backup_path}")

# 3. Read index.html
with open(html_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Verify that lines[20] is <style> and lines[3669] is </style>
# Note: 0-indexed indices.
style_start_line = lines[20].strip()
style_end_line = lines[3669].strip()

print(f"Line 21 (index 20) content: '{style_start_line}'")
print(f"Line 3670 (index 3669) content: '{style_end_line}'")

if "style" not in style_start_line or "style" not in style_end_line:
    raise ValueError(f"Error: Expected <style> and </style> at index 20 and 3669 respectively. Found '{style_start_line}' and '{style_end_line}'.")

# 4. Extract CSS content (index 21 to 3668 inclusive)
css_lines = lines[21:3669]
css_content = "".join(css_lines)

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_content)
print(f"Wrote {len(css_lines)} lines of CSS to {css_path}")

# 5. Build new index.html content
# Keep indices 0 to 19 (lines 1 to 20)
# Add link rel
# Keep indices 3670 onwards (lines 3671 onwards)
new_lines = lines[0:20] + ['  <link rel="stylesheet" href="static/css/global.css">\n'] + lines[3670:]

with open(html_path, "w", encoding="utf-8") as f:
    f.write("".join(new_lines))
print("Successfully updated index.html with global.css stylesheet link.")
