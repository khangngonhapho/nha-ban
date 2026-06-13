f = open('crawl_pipeline.py', 'r', encoding='utf-8')
content = f.read()
f.close()

lines = content.splitlines()
out = open('scratch/crawl_pipeline_sheet_search.txt', 'w', encoding='utf-8')
for i, line in enumerate(lines):
    if 'sheet' in line.lower() or 'google' in line.lower() or 'upload' in line.lower() or 'sync' in line.lower():
        out.write(f"{i+1}: {line}\n")
out.close()
print("Search done.")
