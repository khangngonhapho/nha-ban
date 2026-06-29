import os
import json
import re
import sys
from urllib.parse import urlparse

# Set project root path
project_root = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo"
sys.path.append(project_root)

# Import get_google_credentials from manager.py
from manager import get_google_credentials, load_config

def extract_tk_id_from_r2_url(url):
    # Strip query parameters if any
    url_path = url.split('?')[0]
    filename = url_path.split('/')[-1]
    
    # Format 2: img_{tk_id}_{stt}.jpg (Check first!)
    if filename.startswith("img_"):
        temp = filename[4:]
        if "_" in temp:
            parts = temp.rsplit('_', 1)
            tk_id = parts[0]
            stt = parts[1].split('.')[0]
            return tk_id, "interior", stt
            
    # Format 3: sodo{num}_{tk_id}.jpg (Check second!)
    if filename.startswith("sodo"):
        match = re.match(r"sodo(\d+)_(.+)\.[a-zA-Z0-9]+", filename)
        if match:
            sodo_num = match.group(1)
            tk_id = match.group(2)
            return tk_id, "sodo", sodo_num
            
    # Format 4: SYS-{tk_id}_{role}_{timestamp}.jpg (Check third!)
    if filename.startswith("SYS-"):
        temp = filename[4:]
        if "_" in temp:
            parts = temp.split('_', 1)
            tk_id = parts[0].lower()
            return tk_id, "manual", parts[1]
            
    # Format 1: BDS-KhangNgo/{tk_id}_{filename} (Fallback/last!)
    if "/BDS-KhangNgo/" in url_path:
        if "_" in filename:
            parts = filename.split('_', 1)
            return parts[0], "cloudinary", parts[1]
            
    return None, None, None

def main():
    print("[+] KHỞI ĐỘNG TIẾN TRÌNH SAO LƯU VÀ CHIẾT XUẤT ẢNH R2 TỪ GOOGLE SHEET...")
    cfg = load_config()
    sheet_id = cfg.get("sheet_id")
    if not sheet_id:
        print("[-] Lỗi: Không tìm thấy sheet_id trong settings.json!")
        sys.exit(1)
        
    print(f"[i] Sử dụng Sheet ID: {sheet_id}")
    
    creds = get_google_credentials()
    if not creds:
        print("[-] Lỗi: Không lấy được credentials Google OAuth!")
        sys.exit(1)
        
    import gspread
    client = gspread.authorize(creds)
    
    print("[+] Đang kết nối tới Google Sheets...")
    spreadsheet = client.open_by_key(sheet_id)
    sheet = spreadsheet.worksheet("Pool")
    
    print("[+] Đang tải dữ liệu từ tab 'Pool' (dòng 2 trở đi)...")
    all_values = sheet.get_all_values()
    if len(all_values) <= 1:
        print("[*] Tab Pool trống hoặc chỉ có header. Không có dữ liệu để quét.")
        sys.exit(0)
        
    headers = all_values[0]
    rows = all_values[1:]
    
    print(f"[i] Đã tải {len(rows)} dòng dữ liệu từ Google Sheets.")
    
    # Tìm các cột hình ảnh
    image_headers = [
        "Sơ đồ thửa đất 1", "Sơ đồ thửa đất 2", "Sơ đồ thửa đất 3", "Sơ đồ thửa đất 4", "Sơ đồ thửa đất 5",
        "Hình Mặt Tiên", "Hình Mặt Tiền", # check cả 2 typo
        "Hình Hẻm 1", "Hình Hẻm 2", "Hình Hẻm 3", "Hình Hẻm 4", "Hình Hẻm 5",
        "Hình Hẻm 6", "Hình Hẻm 7", "Hình Hẻm 8", "Hình Hẻm 9", "Hình Hẻm 10",
        "Ảnh 1", "Ảnh 2", "Ảnh 3", "Ảnh 4", "Ảnh 5", "Ảnh 6", "Ảnh 7", "Ảnh 8",
        "Ảnh 9", "Ảnh 10", "Ảnh 11", "Ảnh 12", "Ảnh 13", "Ảnh 14", "Ảnh 15",
        "Ảnh 16", "Ảnh 17", "Ảnh 18", "Ảnh 19", "Ảnh 20",
        "Ảnh 21", "Ảnh 22", "Ảnh 23", "Ảnh 24", "Ảnh 25"
    ]
    
    col_indices = {}
    for h in image_headers:
        if h in headers:
            col_indices[h] = headers.index(h)
            
    print(f"[i] Các cột ảnh được quét: {list(col_indices.keys())}")
    
    r2_mapping = {}
    r2_domain = "pub-e92603c36c8d4789917d05d1eba12a7e.r2.dev"
    
    total_images_mapped = 0
    
    for row_idx, r in enumerate(rows):
        for col_name, col_idx in col_indices.items():
            if col_idx < len(r):
                val = r[col_idx].strip()
                if val and r2_domain in val:
                    # Bóc tách tk_id
                    tk_id, img_type, key = extract_tk_id_from_r2_url(val)
                    if tk_id:
                        if tk_id not in r2_mapping:
                            r2_mapping[tk_id] = {
                                "images": {},      # stt -> r2_url (dành cho img_tk_id_stt)
                                "sodo": {},        # num -> r2_url (dành cho sodoX_tk_id)
                                "filenames": {}    # original_filename -> r2_url (dành cho cloudinary_tk_id_origfilename)
                            }
                        
                        mapped = False
                        if img_type == "cloudinary":
                            r2_mapping[tk_id]["filenames"][key] = val
                            mapped = True
                        elif img_type == "interior":
                            r2_mapping[tk_id]["images"][key] = val
                            mapped = True
                        elif img_type == "sodo":
                            r2_mapping[tk_id]["sodo"][key] = val
                            mapped = True
                        elif img_type == "manual":
                            r2_mapping[tk_id]["filenames"][key] = val
                            mapped = True
                            
                        if mapped:
                            total_images_mapped += 1
                            
    # Ghi file map ra scratch
    output_file = os.path.join(project_root, "scratch/r2_images_by_tk_id.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(r2_mapping, f, ensure_ascii=False, indent=4)
        
    print(f"\n[🏁 HOÀN TẤT SAO LƯU HÌNH ẢNH]")
    print(f"  - Số lượng tk_id căn được nhận diện: {len(r2_mapping)}")
    print(f"  - Tổng số lượng ảnh R2 được lưu trữ: {total_images_mapped}")
    print(f"  - File map được ghi thành công tại: {output_file}")

if __name__ == "__main__":
    main()
