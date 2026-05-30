with open('SOURCE_OF_TRUTH.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'backlog' in line.lower() or 'tính năng' in line.lower():
        print(f"Line {i+1}: {line.strip()}")
