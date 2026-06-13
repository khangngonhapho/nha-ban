import re

f = open('curator_server.py', 'r', encoding='utf-8')
lines = f.read().splitlines()
f.close()

out = open('scratch/status_search_results.txt', 'w', encoding='utf-8')
for i, line in enumerate(lines):
    if 'status' in line.lower() and ('select' in line.lower() or 'update' in line.lower() or 'where' in line.lower() or 'filter' in line.lower()):
        out.write(f"{i+1}: {line}\n")
out.close()
print("Done searching status queries.")
