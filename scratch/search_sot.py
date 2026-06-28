with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/SOURCE_OF_TRUTH.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
found = False
for idx, line in enumerate(lines):
    if "US-104" in line:
        found = True
        start = max(0, idx - 5)
        end = min(len(lines), idx + 25)
        out.append(f"--- Found US-104 at Line {idx+1} ---\n")
        for j in range(start, end):
            out.append(f"{j+1}: {lines[j]}")
        out.append("-----------------\n")

if not found:
    print("US-104 not found in SOT")
else:
    with open("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/scratch/search_sot_output.txt", "w", encoding="utf-8") as f_out:
        f_out.writelines(out)
    print("SOT search completed.")
