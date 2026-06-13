f = open('curator_server.py', 'r', encoding='utf-8')
content = f.read()
f.close()

lines = content.splitlines()
out = open('scratch/image_migration_search.txt', 'w', encoding='utf-8')
for i, line in enumerate(lines):
    if i+1 >= 780 and i+1 <= 1120:
        out.write(f"{i+1}: {line}\n")
out.close()
print("Search done.")
