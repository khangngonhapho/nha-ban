with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's write lines of index.html between character offsets 62000 and 70000
# to a separate file so we can view it.
chunk = content[62000:70000]

with open('scratch/layout_chunk.txt', 'w', encoding='utf-8') as f:
    f.write(chunk)
print("Done writing to scratch/layout_chunk.txt")
