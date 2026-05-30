files_to_check = [
    r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\curator_server.py",
    r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\pool_backend_v3.gs"
]
query = "Chuyên gia môi giới"

output_content = []

for file_path in files_to_check:
    output_content.append("=" * 60)
    output_content.append(f"File: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for idx, line in enumerate(lines):
            if query in line:
                output_content.append(f"Line {idx+1}: {line.strip()}")
                output_content.append("--- Context ---")
                start = max(0, idx - 5)
                end = min(len(lines), idx + 100)  # load up to 100 lines to see the entire prompt
                for i in range(start, end):
                    output_content.append(f"{i+1}: {lines[i].rstrip()}")
                output_content.append("-" * 40)
    except Exception as e:
        output_content.append(f"Error reading {file_path}: {e}")

with open(r"d:\LHTBrain\01_PROJECTS\BDS-KhangNgo\scratch\search_results.txt", "w", encoding="utf-8") as out_f:
    out_f.write("\n".join(output_content))
print("Done writing to search_results.txt")
