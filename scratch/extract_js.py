import re

def extract():
    html = open('index.html', encoding='utf-8').read()
    # Find all <script>...</script> blocks
    scripts = re.findall(r'<script\b[^>]*>(.*?)</script>', html, re.DOTALL)
    print(f"Found {len(scripts)} script blocks.")
    with open('scratch/index_extracted.js', 'w', encoding='utf-8') as f:
        for idx, s in enumerate(scripts):
            f.write(f"// --- SCRIPT BLOCK {idx} ---\n")
            f.write(s)
            f.write("\n\n")
    print("Extracted JS to scratch/index_extracted.js")

if __name__ == '__main__':
    extract()
