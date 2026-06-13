import os

html_path = "curator.html"
py_path = "curator_html_data.py"

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    with open(py_path, "w", encoding="utf-8") as f:
        f.write("# -*- coding: utf-8 -*-\n")
        f.write("CURATOR_HTML_CONTENT = ")
        f.write(repr(html_content))
        f.write("\n")
    print("Successfully synchronized curator_html_data.py with curator.html")
else:
    print("curator.html not found")
