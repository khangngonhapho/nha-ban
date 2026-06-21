# -*- coding: utf-8 -*-
import os
import re

brain_dir = "C:/Users/Khang Ngo/.gemini/antigravity/brain"
default_id = "1088195961071-25r6rpvsfmoudokb75u0m2ugu8na0v0"

def main():
    print(f"Scanning for Google OAuth Client IDs in {brain_dir}...")
    pattern = re.compile(r'(\d+-[a-zA-Z0-9_]+\.apps\.googleusercontent\.com)')
    found_ids = set()
    
    for root, dirs, files in os.walk(brain_dir):
        for file in files:
            if file.endswith('.jsonl') or file.endswith('.md') or file.endswith('.js') or file.endswith('.txt'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, start=1):
                            matches = pattern.findall(line)
                            for match in matches:
                                if default_id not in match:
                                    found_ids.add(match)
                                    print(f"Found ID in {filepath} (Line {line_num}): {match}")
                except Exception as e:
                    pass
                    
    print("\n=== SCAN SUMMARY ===")
    if found_ids:
        print("Found non-default Client IDs:")
        for idx in found_ids:
            print(f"- {idx}")
    else:
        print("No non-default Client IDs found in history.")

if __name__ == "__main__":
    main()
