import os

filepath = "api/index.js"
if os.path.exists(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, 1):
            line_str = line.strip()
            if any(k in line_str for k in ['module.exports', 'export', 'request', 'response', 'handler', 'http', 'url', 'get', 'post']):
                print(f"{idx}: {line_str[:120]}")
else:
    print("api/index.js not found")
