import re

with open('crawl_pipeline.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Search for functions or logic checking if a listing is new or updated
print("Searching for update detection logic in crawl_pipeline.py:")
matches = re.finditer(r'def \w+\(.*?\):', content)
for m in matches:
    func_def = m.group(0)
    if 'save' in func_def or 'scrape' in func_def or 'check' in func_def or 'update' in func_def:
        print(f"  Function: {func_def}")
