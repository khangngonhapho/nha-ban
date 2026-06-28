import os
import re

filepath = "api/index.js"
if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Let's find occurrences of routes
    # E.g. app.get('/api/..., router.get('/api/..., etc.
    matches = re.finditer(r'(app|router|server)\.(get|post|put|delete|use)\(\s*[\'"]([^\'"]+)[\'"]', content)
    print("Found routes:")
    for m in matches:
        print(f"  {m.group(1)}.{m.group(2)}('{m.group(3)}')")
else:
    print("api/index.js not found")
