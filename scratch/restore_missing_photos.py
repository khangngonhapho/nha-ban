import os
import sys
import json
import time
import sqlite3

sys.path.append("d:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
from manager import load_config, get_google_credentials, DB_FILE
from pool_lego import POOL_HEADERS, get_safe_col_name

def classify_image_origin(url, tk_id, raw_drive_images):
    """
    Phân tích sâu URL hình ảnh để phân loại nguồn gốc (crawl vs self):
    1. Nếu URL trùng khớp với bất kỳ ảnh nào trong raw_drive_images -> crawl
    2. Nếu tên file chứa tiền tố 'SYS-' -> self
    3. Nếu tên file khớp mẫu 'img_tk_id_idx.jpg' hoặc 'sodo_tk_id.jpg' -> crawl
    4. Mặc định: Nếu là link R2 -> self, các link khác -> crawl
    """
    url_clean = url.strip()
    if not url_clean:
        return "crawl"
        
    # So khớp trực tiếp với danh sách raw_drive_images
    if raw_drive_images:
        for r_url in raw_drive_images:
            if url_clean.split('?')[0] == r_url.strip().split('?')[0]:
                return "crawl"
                
    filename = url_clean.split('/')[-1]
    
    # Check tiền tố SYS- (do người dùng upload thủ công)
    if filename.upper().startswith("SYS-"):
        return "self"
        
    # Check mẫu đặt tên của crawler
    tk_id_upper = tk_id.upper()
    if f"img_{tk_id_upper}_" in filename.upper() or f"img_{tk_id}_" in filename:
        return "crawl"
    if f"sodo" in filename.lower() and (tk_id_upper in filename.upper() or tk_id in filename):
        return "crawl"
        
    # Nếu là ảnh R2 mà không khớp mẫu crawl -> Nhiều khả năng là tự upload
    if "r2.dev" in url_clean or "r2.cloudflarestorage.com" in url_clean or "pub-" in url_clean:
        return "self"
        
    return "crawl"

def main(dry_run=True, limit=5, all_flag=False):
    print("==========================================================")
    print(f"🔄 TIẾN TRÌNH KHÔI PHỤC & DỌN DẸP ẢNH R2 TỪ SQLITE (DRY_RUN={dry_run}, LIMIT={limit if not all_flag else 'ALL'})")
    print("==========================================================")
    
    # 1. Đọc dữ liệu từ SQLite cục bộ làm Source of Truth
    print("[1/3] Đang kết nối SQLite và lấy thông tin ảnh di cư...")
    if not os.path.exists(DB_FILE):
        print(f"❌ Không tìm thấy tệp CSDL: {DB_FILE}")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Lấy danh sách các cột thực tế của bảng listings
    cursor.execute("PRAGMA table_info(listings)")
    db_cols = {r[1] for r in cursor.fetchall()}
    
    sql_cols = ["tk_id", "status"]
    for c in ["raw_drive_images_json", "Images_Admin_JSON", "curated_config_json"]:
        if c in db_cols:
            sql_cols.append(c)
            
    db_rows = cursor.execute(f"SELECT {', '.join(sql_cols)} FROM listings").fetchall()
    conn.close()
    
    sqlite_images_map = {}
    for r in db_rows:
        d = dict(r)
        tk_id = d.get("tk_id")
        if not tk_id:
            continue
            
        # Trích xuất ảnh R2 di cư
        raw_drive_images = []
        if "raw_drive_images_json" in d and d["raw_drive_images_json"]:
            try:
                raw_drive_images = json.loads(d["raw_drive_images_json"])
            except Exception:
                pass
                
        # Trích xuất ảnh hiện tại (bao gồm cả ảnh tự up)
        all_images = []
        
        # Thử đọc curated_config_json trước
        curated_str = d.get("curated_config_json")
        if curated_str:
            try:
                parsed = json.loads(curated_str)
                # curated_config có thể là list hoặc dict
                imgs_list = parsed.get("images", []) if isinstance(parsed, dict) else parsed
                for img in imgs_list:
                    if isinstance(img, dict) and img.get("url"):
                        all_images.append(img)
            except Exception:
                pass
                
        # Thử đọc Images_Admin_JSON
        admin_str = d.get("Images_Admin_JSON") or d.get("images_admin_json")
        if not all_images and admin_str:
            try:
                parsed = json.loads(admin_str)
                for img in parsed:
                    if isinstance(img, dict):
                        url = img.get("r2_url") or img.get("image_url")
                        role_vi_map = {
                            "diagram": "Sơ đồ", "facade": "Mặt tiền", "cover": "Bìa",
                            "alley": "Hẻm", "interior": "Nội thất", "hidden": "Ẩn", "deleted": "deleted"
                        }
                        if url:
                            all_images.append({
                                "url": url,
                                "role": role_vi_map.get(img.get("role", "interior"), "Nội thất"),
                                "visible": img.get("is_hidden", 0) == 0
                            })
            except Exception:
                pass
                
        # Nếu cả 2 đều trống, sử dụng raw_drive_images
        if not all_images and raw_drive_images:
            for url in raw_drive_images:
                all_images.append({
                    "url": url,
                    "role": "Nội thất",
                    "visible": True
                })
                
        if all_images:
            sqlite_images_map[tk_id] = {
                "all_images": all_images,
                "raw_drive_images": raw_drive_images,
                "status": d.get("status")
            }
            
    print(f"  - Đã tải {len(sqlite_images_map)} căn nhà có hình ảnh từ SQLite.")
    
    # 2. Kết nối Google Sheets
    print("\n[2/3] Đang tải dữ liệu Google Sheets...")
    creds = get_google_credentials()
    cfg = load_config()
    sheet_id = cfg.get("sheet_id") or "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
    
    import gspread
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    
    pool_sheet = spreadsheet.worksheet("Pool")
    pool_rows = pool_sheet.get_all_values()
    print(f"  - Tổng số dòng trong tab Pool: {len(pool_rows)}")
    
    headers = pool_rows[0]
    
    # Chỉ số các cột cần thiết trên Pool
    img_headers = [f"Ảnh {i}" for i in range(1, 26)] + [f"Hình Hẻm {i}" for i in range(1, 11)]
    img_col_indices = {h: headers.index(h) for h in img_headers if h in headers}
    
    hinh_mat_tien_idx = headers.index("Hình Mặt Tiền") if "Hình Mặt Tiền" in headers else -1
    link_goc_idx = headers.index("Link Gốc") if "Link Gốc" in headers else -1
    ma_hang_idx = headers.index("Mã Hàng") if "Mã Hàng" in headers else -1
    images_admin_json_idx = headers.index("Images_Admin_JSON") if "Images_Admin_JSON" in headers else -1
    
    # 3. Phân tích sự lệch/thiếu hình và xây dựng nhóm update
    print("\n[3/3] Đang so khớp dữ liệu và tạo nhóm cập nhật...")
    updates_pool = []
    updates_backup_rows = []
    
    # Tải trước tab Pool_Images để cập nhật
    pool_images_sheet = spreadsheet.worksheet("Pool_Images")
    pool_images_rows = pool_images_sheet.get_all_values()
    pool_images_keys = {}
    for idx, r in enumerate(pool_images_rows[1:], start=2):
        if r and len(r) > 2:
            key = (r[0].strip(), r[2].strip()) # (tk_id, type)
            pool_images_keys[key] = idx
            
    for idx, row in enumerate(pool_rows[1:], start=2):
        if len(row) < 10 or not row[0]:
            continue
            
        link_goc = row[link_goc_idx] if link_goc_idx > -1 else ""
        ma_hang = row[ma_hang_idx] if ma_hang_idx > -1 else ""
        tk_id = ""
        if link_goc:
            parts = link_goc.rstrip("/").split("/")
            if parts:
                tk_id = parts[-1].strip()
        if not tk_id and ma_hang:
            tk_id = ma_hang
            
        if not tk_id or tk_id not in sqlite_images_map:
            continue
            
        db_data = sqlite_images_map[tk_id]
        db_all_imgs = db_data["all_images"]
        db_raw_drive = db_data["raw_drive_images"]
        
        # Kiểm tra xem hình trên Sheets hiện tại có trống hoặc chứa link thô đối tác không
        has_flat_images = False
        has_raw_cloudfront = False
        
        for h, c_idx in img_col_indices.items():
            if c_idx < len(row) and row[c_idx].strip().startswith("http"):
                has_flat_images = True
                if "cloudfront.net" in row[c_idx] or "proptech" in row[c_idx]:
                    has_raw_cloudfront = True
                    
        # Kiểm tra xem Images_Admin_JSON trên Sheets có trống hoặc chưa được khởi tạo không
        has_empty_admin_json = False
        if images_admin_json_idx > -1:
            admin_val = row[images_admin_json_idx].strip() if images_admin_json_idx < len(row) else ""
            if not admin_val or admin_val == "[]":
                has_empty_admin_json = True
                    
        # Điều kiện khôi phục: Căn bị trống ảnh hoàn toàn, còn chứa link thô Cloudfront, hoặc trường Images_Admin_JSON trên Sheets trống
        if (not has_flat_images) or has_raw_cloudfront or has_empty_admin_json:
            # Nhóm ảnh sơ đồ hiện có từ sheets
            diag_cols = [f"Sơ đồ thửa đất {i}" for i in range(1, 6)]
            diag_urls = []
            for d_col in diag_cols:
                if d_col in headers:
                    d_idx = headers.index(d_col)
                    if d_idx < len(row) and row[d_idx].strip():
                        diag_urls.append(row[d_idx].strip())
                        
            # Lọc ảnh nội thất & hẻm R2 từ SQLite
            interiors = []
            alleys = []
            
            for img in db_all_imgs:
                url = img["url"]
                role = img["role"]
                is_diag = any(url.split("?")[0] == d_url.split("?")[0] for d_url in diag_urls)
                if is_diag:
                    continue
                if role == "Hẻm":
                    alleys.append(url)
                elif role != "Sơ đồ":
                    interiors.append(url)
                    
            # 3.1 Cập nhật tab Pool
            row_updated = list(row)
            while len(row_updated) < len(headers):
                row_updated.append("")
                
            # Cập nhật Hình mặt tiền
            if hinh_mat_tien_idx > -1 and (not row_updated[hinh_mat_tien_idx].strip() or "cloudfront" in row_updated[hinh_mat_tien_idx]):
                if interiors:
                    row_updated[hinh_mat_tien_idx] = interiors[0]
                    
            # Cập nhật Ảnh 1-25
            for i in range(25):
                h_name = f"Ảnh {i+1}"
                if h_name in img_col_indices:
                    c_idx = img_col_indices[h_name]
                    row_updated[c_idx] = interiors[i] if i < len(interiors) else ""
                    
            # Cập nhật Hình Hẻm 1-10
            for i in range(10):
                h_name = f"Hình Hẻm {i+1}"
                if h_name in img_col_indices:
                    c_idx = img_col_indices[h_name]
                    row_updated[c_idx] = alleys[i] if i < len(alleys) else ""
                    
            # Cập nhật trường Images_Admin_JSON trên Pool
            if images_admin_json_idx > -1:
                # Đóng gói danh sách ảnh di cư hoàn chỉnh
                role_map_vi_to_en = {
                    "Sơ đồ": "diagram", "Mặt tiền": "facade", "Bìa": "cover",
                    "Hẻm": "alley", "Nội thất": "interior", "Ẩn": "hidden", "deleted": "deleted"
                }
                migrated_images_meta = []
                for idx_meta, img in enumerate(db_all_imgs):
                    url = img["url"]
                    role_en = role_map_vi_to_en.get(img["role"], "interior")
                    origin = classify_image_origin(url, tk_id, db_raw_drive)
                    is_hidden_val = 1 if (not img["visible"] or role_en in ["hidden", "deleted"]) else 0
                    
                    migrated_images_meta.append({
                        "image_url": url,
                        "r2_url": url,
                        "role": role_en,
                        "sequence_index": idx_meta,
                        "origin": origin,
                        "is_hidden": is_hidden_val
                    })
                row_updated[images_admin_json_idx] = json.dumps(migrated_images_meta, ensure_ascii=False)
                
            col_letter_max = gspread.utils.rowcol_to_a1(1, len(row_updated)).replace("1", "")
            updates_pool.append({
                'range': f"A{idx}:{col_letter_max}{idx}",
                'values': [row_updated],
                'ma_hang': ma_hang,
                'tk_id': tk_id,
                'db_all_imgs': db_all_imgs,
                'db_raw_drive': db_raw_drive
            })
            
    # Giới hạn số lượng căn chạy thử
    if not all_flag and limit > 0:
        updates_pool = updates_pool[:limit]
        print(f"⚠️ Chế độ GIỚI HẠN: Chỉ xử lý {len(updates_pool)} căn đầu tiên để kiểm tra.")
        
    # Tạo danh sách cập nhật cho Pool_Images dựa trên những căn được khôi phục
    for up in updates_pool:
        # Tách ảnh crawl R2 và ảnh self R2
        crawl_imgs = []
        self_imgs = []
        
        for img in up['db_all_imgs']:
            url = img["url"]
            origin = classify_image_origin(url, up['tk_id'], up['db_raw_drive'])
            if origin == "self":
                self_imgs.append(url)
            else:
                crawl_imgs.append(url)
                
        address = up['values'][0][headers.index("Địa chỉ")] if "Địa chỉ" in headers else ""
        
        # Dòng crawl
        crawl_row = [up['tk_id'], address, "crawl", len(crawl_imgs)] + crawl_imgs
        # Dòng self
        self_row = [up['tk_id'], address, "self", len(self_imgs)] + self_imgs
        
        # Xác định dòng ghi trên Pool_Images
        crawl_key = (up['tk_id'], "crawl")
        self_key = (up['tk_id'], "self")
        
        if crawl_key in pool_images_keys:
            r_idx = pool_images_keys[crawl_key]
            c_letter = gspread.utils.rowcol_to_a1(1, len(crawl_row)).replace("1", "")
            updates_backup_rows.append({
                'range': f"A{r_idx}:{c_letter}{r_idx}",
                'values': [crawl_row]
            })
        if self_key in pool_images_keys:
            r_idx = pool_images_keys[self_key]
            c_letter = gspread.utils.rowcol_to_a1(1, len(self_row)).replace("1", "")
            updates_backup_rows.append({
                'range': f"A{r_idx}:{c_letter}{r_idx}",
                'values': [self_row]
            })
            
        print(f"🚩 Phát hiện khôi phục {up['ma_hang']}: {len(crawl_imgs)} ảnh crawl R2, {len(self_imgs)} ảnh self R2 (Sạch link thô).")
        
    # 4. Thực thi cập nhật lên Sheets
    if not dry_run:
        # Cập nhật Pool
        if updates_pool:
            print(f"\n🚀 Đang cập nhật {len(updates_pool)} căn lên tab Pool...")
            pool_sheet.batch_update([{'range': u['range'], 'values': u['values']} for u in updates_pool], value_input_option='USER_ENTERED')
            print("  [OK] Đã cập nhật tab Pool.")
            
        # Cập nhật Pool_Images
        if updates_backup_rows:
            print(f"\n🚀 Đang dọn dẹp và cập nhật {len(updates_backup_rows)} dòng lên tab Pool_Images...")
            pool_images_sheet.batch_update(updates_backup_rows, value_input_option='USER_ENTERED')
            print("  [OK] Đã cập nhật tab Pool_Images.")
            
    print("\n==========================================================")
    print(f"🏁 HOÀN TẤT: Tổng số căn được cập nhật ảnh R2: {len(updates_pool)}")
    print("==========================================================")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Thực hiện ghi nhận đè dữ liệu lên Google Sheets.")
    parser.add_argument("--all", action="store_true", help="Khôi phục toàn bộ các căn (không giới hạn). Mặc định chỉ khôi phục 5 căn đầu.")
    args = parser.parse_args()
    
    main(dry_run=not args.run, limit=5, all_flag=args.all)
