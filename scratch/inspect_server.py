import re

with open('curator_server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for sheet references or read/write operations
lines = content.split('\n')
for i, line in enumerate(lines):
    if any(keyword in line for keyword in ['spreadsheets', 'sheet', 'POOL', 'SOURCE', 'Source', 'Pool', 'tk-', 'duplicate']):
        print(f"Line {i+1}: {line.strip()}")
