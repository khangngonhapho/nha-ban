with open("curator.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "function setSidebarStatus" in line:
        print(f"setSidebarStatus starts at line {idx+1}: {line.strip()}")
    if "listings.forEach(house =>" in line:
        print(f"listings loop starts at line {idx+1}: {line.strip()}")
    if "function selectListing" in line:
        print(f"selectListing starts at line {idx+1}: {line.strip()}")
