import re

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/extracted_styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Search for selectors styling 'header'
matches = list(re.finditer(r'\bheader\b', css))
output = []
for m in matches:
    start = m.start()
    block_start = css.rfind('}', 0, start)
    if block_start == -1:
        block_start = css.rfind('{', 0, start)
    if block_start == -1:
        block_start = 0
    else:
        block_start += 1
    
    block_end = css.find('}', start)
    if block_end == -1:
        block_end = len(css)
    else:
        block_end += 1
        
    snippet = css[block_start:block_end].strip()
    # Check if there is a media query context
    media_context = "Global"
    last_media = css.rfind('@media', 0, start)
    if last_media != -1:
        sub_css = css[last_media:start]
        open_braces = sub_css.count('{')
        close_braces = sub_css.count('}')
        if open_braces > close_braces:
            media_header_end = css.find('{', last_media)
            media_context = css[last_media:media_header_end].strip()
            
    output.append(f"Media context: {media_context}\n{snippet}\n" + "-"*50 + "\n")

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/inspect_header_styles_output.txt', 'w', encoding='utf-8') as f_out:
    f_out.write("".join(output))

print("Wrote output to scratch/inspect_header_styles_output.txt")
