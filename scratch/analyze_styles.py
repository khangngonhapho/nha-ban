import re
import sys

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/extracted_styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

output = []

# Helper to find where selectors are defined
def find_selectors(pattern):
    output.append(f"=== Searching for selector: {pattern} ===\n")
    matches = list(re.finditer(pattern, css))
    for m in matches:
        start = m.start()
        # Find start of CSS block (previous '{' or '}')
        block_start = css.rfind('}', 0, start)
        if block_start == -1:
            block_start = css.rfind('{', 0, start)
        if block_start == -1:
            block_start = 0
        else:
            block_start += 1
        
        # Find end of CSS block (next '}')
        block_end = css.find('}', start)
        if block_end == -1:
            block_end = len(css)
        else:
            block_end += 1
            
        snippet = css[block_start:block_end].strip()
        
        # Find if this block is inside a media query
        # Let's search backwards for '@media'
        media_context = "Global (No Media Query)"
        last_media = css.rfind('@media', 0, start)
        if last_media != -1:
            # check if there is a closing brace for the media query after start
            sub_css = css[last_media:start]
            open_braces = sub_css.count('{')
            close_braces = sub_css.count('}')
            if open_braces > close_braces:
                # We are inside this media query!
                media_header_end = css.find('{', last_media)
                media_context = css[last_media:media_header_end].strip()
        
        output.append(f"Media context: {media_context}\n")
        output.append(snippet + "\n")
        output.append("-" * 50 + "\n")

find_selectors(r'\bfilter-panel\b')
find_selectors(r'#filterPanel\b')
find_selectors(r'\bsheet\b')
find_selectors(r'\boverlay\b')

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/analyze_styles_output.txt', 'w', encoding='utf-8') as f_out:
    f_out.write("".join(output))

print("Successfully written results to scratch/analyze_styles_output.txt")
