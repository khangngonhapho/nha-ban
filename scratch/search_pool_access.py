f = open('curator_server.py', 'r', encoding='utf-8')
content = f.read()
f.close()

lines = content.splitlines()
out = open('scratch/pool_access_search.txt', 'w', encoding='utf-8')
for i, line in enumerate(lines):
    if 'Pool' in line and ('worksheet' in line or 'open' in line or 'update' in line or 'sheet' in line):
        out.write(f"{i+1}: {line}\n")
out.close()
print("Search done.")
