with open('crawl_pipeline.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
print("Lines mentioning db checks in crawl_pipeline.py:")
for idx, line in enumerate(lines):
    if 'listings WHERE' in line or 'SELECT' in line or 'existing' in line or 'skip' in line or 'update' in line.lower() or 'skipped' in line:
        if len(line.strip()) < 120:
            safe_line = ''.join(c if ord(c) < 128 else '?' for c in line.strip())
            print(f"Line {idx+1}: {safe_line}")
