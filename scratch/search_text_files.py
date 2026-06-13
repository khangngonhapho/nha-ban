import os
import sys

sys.stdout = open("scratch/text_search_output.txt", "w", encoding="utf-8")

search_files = [
    "SOURCE_OF_TRUTH.md",
    "matching_db_listings.txt",
    "match_info.txt",
    "sheet_data.json",
    "inspect_listing.json",
    "inspect_db_full.json"
]

for filename in search_files:
    if os.path.exists(filename):
        print(f"=== Searching in {filename} ===")
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                # Find all occurrences of 270.93.16 or surrounding lines
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if "270.93.16" in line:
                        print(f"Line {i+1}: {line}")
        except Exception as e:
            print(f"Error reading {filename}: {e}")

sys.stdout.close()
