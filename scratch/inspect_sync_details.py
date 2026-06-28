import sys

# Set stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Search for thienkhoi, data.thienkhoi, proptech.thienkhoi, Link_Goc in pool_lego.py
with open("pool_lego.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== References in pool_lego.py ===")
for i, line in enumerate(lines):
    if any(term in line for term in ["thienkhoi", "Link_Goc", "Link Gốc", "data.thienkhoi"]):
        print(f"Line {i+1}: {line.strip()}")
