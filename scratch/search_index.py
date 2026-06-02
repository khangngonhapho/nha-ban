# search_index.py
with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

out_lines = []
def show_matches(kw, max_show=50):
    out_lines.append(f"\n=== Matches for '{kw}' ===")
    count = 0
    for i, line in enumerate(lines):
        if kw.lower() in line.lower():
            out_lines.append(f"Line {i+1:4d}: {line.strip()}")
            count += 1
            if count >= max_show:
                out_lines.append("... truncated ...")
                break

show_matches(".admin-only", 20)
show_matches("admin-only", 20)

with open("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo\\scratch\\matches_adminonly.txt", "w", encoding="utf-8") as out_f:
    out_f.write("\n".join(out_lines))
print("Done")
