import re

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/extracted_styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

output = []

# Find rules containing body or html
def find_rules(keywords):
    for kw in keywords:
        output.append(f"=== Searching for: {kw} ===\n")
        matches = list(re.finditer(rf'\b{kw}\b', css))
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
            output.append(snippet + "\n")
            output.append("-" * 50 + "\n")

find_rules(['body', 'html'])

with open('d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/inspect_body_style_output.txt', 'w', encoding='utf-8') as f_out:
    f_out.write("".join(output))

print("Wrote output to scratch/inspect_body_style_output.txt")
