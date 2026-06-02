import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open("index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("EDITING AND FORM LOGIC IN index.html:")
print("=" * 60)

for idx, line in enumerate(lines):
    if "edit" in line.lower() and ("input" in line or "textarea" in line or "modal" in line or "save" in line):
        if any(k in line for k in ["TieuDe", "MoTa", "Title", "Desc", "cover", "image", "hinh"]):
            print(f"Line {idx+1}: {line.strip()[:120]}")
