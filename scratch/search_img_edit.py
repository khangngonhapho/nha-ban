import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's search for the image editor container and how it renders
print("=== IDs related to image/editor/modal/carousel ===")
for m in re.finditer(r'(?i)id=[\'\"][^\'\"]*(?:image|photo|edit|curat|modal|carousel|gallery|grid)[^\'\"]*[\'\"]', content):
    print(m.group(0), 'at line', content[:m.start()].count('\n') + 1)

print("\n=== Search for text related to Mặt tiền, Hình nền, Sổ ===")
keywords = ["mặt tiền", "mặt_tiền", "hình nền", "hình_nền", "sổ đỏ", "sơ đồ", "chọn hiển thị", "show_img", "checked"]
for kw in keywords:
    matches = list(re.finditer(re.escape(kw), content, re.IGNORECASE))
    print(f"Keyword '{kw}': {len(matches)} matches")
    for m in matches[:10]: # Print first 10 matches
        line_no = content[:m.start()].count('\n') + 1
        line_start = content.rfind('\n', 0, m.start()) + 1
        line_end = content.find('\n', m.end())
        line_content = content[line_start:line_end].strip()
        print(f"  Line {line_no}: {line_content[:120]}")
