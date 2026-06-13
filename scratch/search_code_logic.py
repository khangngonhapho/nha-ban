import os

def search_files():
    targets = [
        "index.html",
        "api/index.js",
        "curator_server.py",
        "pool_backend_v3.gs",
        "SOURCE_OF_TRUTH.md",
        "docs/data_dictionary.md",
        "Schema Sheet Source.md",
        "Schema Sheet Public.md",
        "Schema Sheet Raw.md"
    ]
    
    terms = [
        "Tiêu đề BDS",
        "tieu_de",
        "tieu_de_public",
        "Tiêu đề Public",
        "tieuDe",
        "tieuDePublic",
        "tieu_de_source"
    ]
    
    output_lines = []
    
    for filename in targets:
        path = os.path.join("d:\\LHTBrain\\01_PROJECTS\\BDS-KhangNgo", filename)
        if not os.path.exists(path):
            output_lines.append(f"File not found: {filename}\n")
            continue
            
        output_lines.append(f"\n=== MATCHES IN {filename} ===\n")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line_no, line in enumerate(f, 1):
                    line_lower = line.lower()
                    matched_terms = [t for t in terms if t.lower() in line_lower]
                    if matched_terms:
                        snippet = line.strip()
                        if len(snippet) > 200:
                            snippet = snippet[:200] + "... [TRUNCATED]"
                        output_lines.append(f"Line {line_no} (matched {matched_terms}): {snippet}\n")
        except Exception as e:
            output_lines.append(f"Error reading {filename}: {e}\n")
            
    with open("scratch/search_results_clean.txt", "w", encoding="utf-8") as out:
        out.writelines(output_lines)
    print("Done search.")

if __name__ == "__main__":
    search_files()
