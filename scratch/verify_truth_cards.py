# -*- coding: utf-8 -*-
"""
Script kiểm tra tính cập nhật của các Truth Cards.
Quét tất cả các tệp trong thư mục .agents/truth_cards/
và đối chiếu ngày verify với ngày sửa đổi cuối cùng của các related_files.
"""

import os
import sys
import datetime
import re

# Đảm bảo in ra UTF-8 trên Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TRUTH_CARDS_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "..", "..", ".agents", "truth_cards"))

def parse_frontmatter(content):
    """Bóc tách frontmatter đơn giản không cần thư viện bên ngoài"""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None
    
    yaml_text = match.group(1)
    metadata = {}
    current_key = None
    
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
            
        if line.startswith("-") and current_key:
            # Dòng list item
            val = line[1:].strip().strip('"').strip("'")
            if current_key not in metadata or metadata[current_key] is None:
                metadata[current_key] = []
            if isinstance(metadata[current_key], list):
                metadata[current_key].append(val)
        elif ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip().strip('"').strip("'")
            current_key = key
            if val == "" or val == "null":
                metadata[key] = None
            elif val.startswith("[") and val.endswith("]"):
                # Dạng list inline [a, b]
                items = [i.strip().strip('"').strip("'") for i in val[1:-1].split(",") if i.strip()]
                metadata[key] = items
            else:
                metadata[key] = val
                
    return metadata

def main():
    print("[INFO] Bat dau kiem tra tinh cap nhat cua Truth Cards...")
    if not os.path.exists(TRUTH_CARDS_DIR):
        print(f"[ERROR] Thu muc chua Truth Cards khong ton tai: {TRUTH_CARDS_DIR}")
        sys.exit(1)
        
    card_files = [f for f in os.listdir(TRUTH_CARDS_DIR) if f.endswith(".md")]
    warnings = 0
    errors = 0
    
    for filename in card_files:
        filepath = os.path.join(TRUTH_CARDS_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"[ERROR] Khong the doc file: {filename} - {str(e)}")
            errors += 1
            continue
            
        metadata = parse_frontmatter(content)
        if not metadata:
            print(f"[ERROR] File khong chua frontmatter hop le: {filename}")
            errors += 1
            continue
            
        card_id = metadata.get("id", "Unknown")
        verify_date_str = metadata.get("last_verified_against_code")
        related_files = metadata.get("related_files", [])
        
        if not verify_date_str:
            print(f"[ERROR] Card {card_id} ({filename}) thieu truong 'last_verified_against_code'")
            errors += 1
            continue
            
        try:
            verify_date = datetime.datetime.strptime(verify_date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"[ERROR] Card {card_id} ({filename}) co ngay verify sai dinh dang YYYY-MM-DD: {verify_date_str}")
            errors += 1
            continue
            
        print(f"Card {card_id} (Verify Date: {verify_date_str})...")
        
        for rel_file in related_files:
            rel_path = os.path.join(PROJECT_ROOT, rel_file)
            if not os.path.exists(rel_path):
                print(f"  [ERROR] File lien quan khong ton tai: {rel_file}")
                errors += 1
                continue
                
            mtime_ts = os.path.getmtime(rel_path)
            mtime_date = datetime.datetime.fromtimestamp(mtime_ts).date()
            
            if mtime_date > verify_date:
                print(f"  [WARNING] Truth Card {card_id} ({filename}) co the da loi thoi!")
                print(f"    - File lien quan '{rel_file}' duoc sua doi vao {mtime_date}")
                print(f"    - Ngay xac minh gan nhat cua Card la {verify_date}")
                warnings += 1
                
    print("\nBAO CAO KET QUA KIEM TRA:")
    print(f"  - Tong so Truth Cards da quet: {len(card_files)}")
    print(f"  - So loi (Errors): {errors}")
    print(f"  - So canh bao (Warnings): {warnings}")
    
    if errors > 0:
        print("[FAIL] Phat hien loi cau truc/file! Kiem tra that bai.")
        sys.exit(1)
    elif warnings > 0:
        print("[WARNING] Co canh bao Truth Cards loi thoi so voi code thuc te.")
        sys.exit(0)
    else:
        print("[SUCCESS] Tat ca Truth Cards deu up-to-date!")
        sys.exit(0)

if __name__ == "__main__":
    main()
