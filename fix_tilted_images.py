#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
==================================================
KHANG NGÔ NHÀ PHỐ - MIGRATED IMAGE ROTATION FIXER
US-056: Quét và sửa lỗi quay ảnh 90 độ cho các căn cũ
==================================================
"""

import os
import sys
import time
import json
import sqlite3
import requests
import io
import argparse
import concurrent.futures
from datetime import datetime
from PIL import Image

# Đảm bảo mã hóa UTF-8
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Import backend modules
import manager
import hashlib

def extract_cloudinary_public_id(url):
    """
    Trích xuất public_id từ URL Cloudinary.
    Ví dụ: https://res.cloudinary.com/deru9p712/image/upload/v1779958985/BDS-KhangNgo/ey4mbj-lvcjwvqn-41094ab3/kgdlqkg5rrztdnaipo5i.jpg
    -> BDS-KhangNgo/ey4mbj-lvcjwvqn-41094ab3/kgdlqkg5rrztdnaipo5i
    """
    if not url or "cloudinary.com" not in url:
        return None
    try:
        parts = url.split("/image/upload/")
        if len(parts) < 2:
            return None
        path = parts[1]
        
        path_segments = path.split("/")
        # Loại bỏ version segment (vd: v1779958985)
        if path_segments[0].startswith("v") and path_segments[0][1:].isdigit():
            path_segments = path_segments[1:]
            
        public_id_with_ext = "/".join(path_segments)
        public_id = os.path.splitext(public_id_with_ext)[0]
        return public_id
    except Exception:
        return None

def delete_cloudinary_image(public_id, cfg):
    """
    Xóa một ảnh cũ trên Cloudinary thông qua REST API Signed Destroy.
    """
    if not public_id:
        return False
        
    cloud_name = cfg.get("cloudinary_cloud_name")
    api_key = cfg.get("cloudinary_api_key")
    api_secret = cfg.get("cloudinary_api_secret")
    
    if not (cloud_name and api_key and api_secret):
        return False
        
    timestamp = int(time.time())
    params_to_sign = {
        "public_id": public_id,
        "timestamp": timestamp
    }
    
    sorted_params = sorted([f"{k}={v}" for k, v in params_to_sign.items()])
    sign_string = "&".join(sorted_params) + api_secret
    signature = hashlib.sha1(sign_string.encode('utf-8')).hexdigest()
    
    url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/destroy"
    data = {
        "api_key": api_key,
        "timestamp": timestamp,
        "signature": signature,
        "public_id": public_id
    }
    
    try:
        r = requests.post(url, data=data, timeout=15)
        if r.status_code == 200:
            res_data = r.json()
            if res_data.get("result") == "ok":
                print(f"  [🗑️ Cloudinary] Đã xóa thành công ảnh cũ: {public_id}")
                return True
            else:
                print(f"  [⚠️ Cloudinary] Phản hồi xóa ảnh không thành công: {res_data}")
        else:
            print(f"  [⚠️ Cloudinary] Lỗi API xóa ảnh ({r.status_code}): {r.text}")
    except Exception as e:
        print(f"  [❌ Cloudinary LỖI] Lỗi khi xóa ảnh {public_id}: {str(e)}")
    return False

def delete_old_cloudinary_images_for_listing(old_images_json, cfg):
    """
    Xóa tất cả các ảnh cũ trên Cloudinary của căn hộ này.
    """
    if not old_images_json:
        return
    try:
        urls = json.loads(old_images_json)
    except Exception:
        return
        
    if not urls:
        return
        
    print(f"  [🗑️ Cloudinary] Phát hiện danh sách {len(urls)} ảnh cũ. Tiến hành dọn dẹp giải phóng dung lượng...")
    for url in urls:
        if url and "cloudinary.com" in url:
            public_id = extract_cloudinary_public_id(url)
            if public_id:
                delete_cloudinary_image(public_id, cfg)

def get_image_exif_orientation(img_url, headers_tk):
    """
    Tải byte ảnh gốc từ Thiên Khôi và kiểm tra xem có thẻ EXIF Orientation nào cần xoay không.
    Trả về giá trị Orientation (int) hoặc None nếu không có hoặc bình thường.
    """
    try:
        r = requests.get(img_url, headers=headers_tk, timeout=10)
        if r.status_code == 200:
            img = Image.open(io.BytesIO(r.content))
            exif = img.getexif()
            if exif:
                orientation = exif.get(274)
                return orientation
    except Exception:
        pass
    return None

def scrape_original_tk_urls(tk_id, headers_tk):
    """
    Cào lại trang chi tiết gốc Thiên Khôi để lấy danh sách ảnh gốc còn nguyên EXIF.
    Trả về (product_urls, diagram_urls) nếu thành công, ngược lại (None, None).
    """
    detail_url = f"https://data.thienkhoi.com/Hang/Detail/{tk_id}"
    try:
        r = requests.get(detail_url, headers=headers_tk, timeout=15)
        if r.status_code == 200 and "security.html" not in r.url and "Account/Login" not in r.url:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, "html.parser")
            
            img_els_nd = soup.select('#lightgalleryND li')
            images_nd = [li.get('data-src', '') for li in img_els_nd if li.get('data-src')]
            
            img_els_td = soup.select('#lightgalleryTD li')
            images_td = [li.get('data-src', '') for li in img_els_td if li.get('data-src')]
            
            return images_nd, images_td
    except Exception:
        pass
    return None, None

def check_listing_tilted(row, headers_tk):
    """
    Kiểm tra xem căn nhà có ảnh nào bị lỗi nghiêng 90 độ hay không.
    Tự động cào lại Thiên Khôi nếu phát hiện mảng ảnh thô chứa link Cloudinary bị mất EXIF.
    """
    tk_id = row["tk_id"]
    raw_images_tk_json = row.get("raw_images_tk_json") or "[]"
    
    # 1. Phát hiện và tự động cào đè nếu chỉ có link Cloudinary cũ
    needs_scrape = False
    if "cloudinary.com" in raw_images_tk_json or raw_images_tk_json == "[]":
        needs_scrape = True
        
    raw_images_tk = []
    if needs_scrape:
        print(f"  [🔎 Cào lại] Phát hiện căn {tk_id} bị mất mảng ảnh gốc. Đang cào lại từ Thiên Khôi...")
        original_nd, original_td = scrape_original_tk_urls(tk_id, headers_tk)
        if original_nd:
            raw_images_tk = original_nd
            # Lưu đè mảng ảnh gốc chuẩn vào SQLite
            try:
                conn = sqlite3.connect("raw_archive.db")
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE listings SET raw_images_tk_json = ? WHERE tk_id = ?",
                    (json.dumps(original_nd + original_td), tk_id)
                )
                conn.commit()
                conn.close()
                print(f"  [✅ Cào lại] Đã khôi phục {len(original_nd)} ảnh gốc Thiên Khôi cho {tk_id} vào SQLite!")
            except Exception as e:
                print(f"  [⚠️ WARNING] Không thể lưu mảng ảnh gốc khôi phục: {str(e)}")
        else:
            print(f"  [❌ Cào lại] Scrape trang gốc Thiên Khôi thất bại cho {tk_id} (Có thể cookie hết hạn hoặc link hỏng).")
    
    # Nếu không cần cào hoặc cào thất bại, dùng mảng ảnh có sẵn
    if not raw_images_tk and raw_images_tk_json:
        try:
            raw_images_tk = json.loads(raw_images_tk_json)
        except Exception:
            pass

    if not raw_images_tk:
        return False, []

    # Lọc bỏ các ảnh sơ đồ hoặc Cloudinary còn sót lại
    images_to_check = [url for url in raw_images_tk if url and url.startswith("http") and "cloudinary.com" not in url][:5]
    tilted_urls = []
    
    for url in images_to_check:
        orientation = get_image_exif_orientation(url, headers_tk)
        if orientation and orientation in [2, 3, 4, 5, 6, 7, 8]:
            tilted_urls.append((url, orientation))
            
    return len(tilted_urls) > 0, tilted_urls

def re_migrate_listing_images(tk_id, row, cookie, cfg):
    """
    Tải lại ảnh gốc, xoay đứng thẳng vật lý, nén ảnh, upload lên Cloudinary và cập nhật SQLite + Sheets.
    """
    print(f"🔄 [Bắt đầu sửa] Đang tiến hành di cư đè hình ảnh thẳng đứng cho căn: {tk_id}...")
    
    # Reload dòng mới nhất trong SQLite đề phòng raw_images_tk_json vừa được cập nhật khi quét
    try:
        conn_load = sqlite3.connect("raw_archive.db")
        conn_load.row_factory = sqlite3.Row
        cursor_load = conn_load.cursor()
        latest_row = cursor_load.execute("SELECT * FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
        conn_load.close()
        if latest_row:
            row = dict(latest_row)
    except Exception:
        pass

    cld_cloud_name = cfg.get("cloudinary_cloud_name")
    cld_api_key = cfg.get("cloudinary_api_key")
    cld_api_secret = cfg.get("cloudinary_api_secret")
    use_cloudinary = bool(cld_cloud_name and cld_api_key and cld_api_secret)

    if not use_cloudinary:
        raise RuntimeError("Chưa cấu hình thông số Cloudinary trong settings.json")

    headers_tk = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie or ""
    }

    # Thực hiện xóa dọn dẹp các ảnh cũ đã tải lên Cloudinary trước khi tải ảnh mới lên
    old_drive_images_json = row.get("raw_drive_images_json")
    if old_drive_images_json:
        try:
            delete_old_cloudinary_images_for_listing(old_drive_images_json, cfg)
        except Exception as del_err:
            print(f"  [⚠️ WARNING] Lỗi dọn dẹp ảnh cũ Cloudinary: {str(del_err)}")

    raw_images_tk = json.loads(row["raw_images_tk_json"]) if row.get("raw_images_tk_json") else []
    drive_links = ["" for _ in raw_images_tk]

    col_sodo1_key = manager.get_safe_col_name("Sơ đồ thửa đất 1")
    col_sodo2_key = manager.get_safe_col_name("Sơ đồ thửa đất 2")
    col_sodo3_key = manager.get_safe_col_name("Sơ đồ thửa đất 3")
    col_sodo4_key = manager.get_safe_col_name("Sơ đồ thửa đất 4")
    col_sodo5_key = manager.get_safe_col_name("Sơ đồ thửa đất 5")
    
    original_sodo1 = row[col_sodo1_key] if col_sodo1_key in row.keys() else None
    original_sodo2 = row[col_sodo2_key] if col_sodo2_key in row.keys() else None
    original_sodo3 = row[col_sodo3_key] if col_sodo3_key in row.keys() else None
    original_sodo4 = row[col_sodo4_key] if col_sodo4_key in row.keys() else None
    original_sodo5 = row[col_sodo5_key] if col_sodo5_key in row.keys() else None

    def process_single_image(args_tuple):
        idx, img_url = args_tuple
        try:
            img_data = manager.download_image_with_retry(img_url, headers_tk)
            if not img_data:
                return idx, ""
                
            is_diagram = (img_url == original_sodo1) or (img_url == original_sodo2) or (img_url == original_sodo3) or (img_url == original_sodo4) or (img_url == original_sodo5)
            
            if is_diagram:
                # Bỏ qua nén cho ảnh sơ đồ thửa đất
                pass
            else:
                # Nén và TỰ ĐỘNG XOAY ĐỨNG VẬT LÝ pillow
                img_data = manager.compress_image(img_data)
            
            filename = f"img_{tk_id}_{idx+1}.jpg"
            cld_folder = f"BDS-KhangNgo/{tk_id}"
            
            img_link = manager.upload_image_to_cloudinary(
                img_data, 
                filename, 
                cld_cloud_name, 
                cld_api_key, 
                cld_api_secret, 
                folder=cld_folder
            )
            return idx, img_link
        except Exception as e:
            print(f"  [❌ LỖI] Xử lý ảnh #{idx+1} thất bại cho {tk_id}: {str(e)}")
            return idx, ""

    max_workers = min(3, len(raw_images_tk)) if raw_images_tk else 1
    tasks = list(enumerate(raw_images_tk))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(process_single_image, tasks)
        for idx, img_link in results:
            if img_link:
                drive_links[idx] = img_link
                
    drive_links = [link for link in drive_links if link]

    # Phân loại và gán cột hình ảnh
    clean_sodo1 = ""
    clean_sodo2 = ""
    clean_sodo3 = ""
    clean_sodo4 = ""
    clean_sodo5 = ""
    house_links = []
    
    for idx, img_url in enumerate(raw_images_tk):
        if idx >= len(drive_links):
            continue
        migrated_url = drive_links[idx]
        if not migrated_url:
            continue
            
        if img_url == original_sodo1:
            clean_sodo1 = migrated_url
        elif img_url == original_sodo2:
            clean_sodo2 = migrated_url
        elif img_url == original_sodo3:
            clean_sodo3 = migrated_url
        elif img_url == original_sodo4:
            clean_sodo4 = migrated_url
        elif img_url == original_sodo5:
            clean_sodo5 = migrated_url
        else:
            house_links.append(migrated_url)

    # Cập nhật SQLite
    conn = sqlite3.connect("raw_archive.db")
    cursor = conn.cursor()
    
    update_fields = {}
    update_fields[col_sodo1_key] = clean_sodo1 or original_sodo1 or ""
    update_fields[col_sodo2_key] = clean_sodo2 or original_sodo2 or ""
    update_fields[col_sodo3_key] = clean_sodo3 or original_sodo3 or ""
    update_fields[col_sodo4_key] = clean_sodo4 or original_sodo4 or ""
    update_fields[col_sodo5_key] = clean_sodo5 or original_sodo5 or ""
    
    # 15 Cột ảnh sản phẩm
    for i in range(15):
        col_name = manager.get_safe_col_name(f"Ảnh {i+1}")
        val = house_links[i] if i < len(house_links) else ""
        update_fields[col_name] = val
        
    cols_sql = [f"`{k}` = ?" for k in update_fields.keys()]
    vals = list(update_fields.values())
    vals.append(json.dumps(drive_links))
    vals.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    vals.append(tk_id)
    
    cursor.execute(
        f"UPDATE listings SET {', '.join(cols_sql)}, raw_drive_images_json = ?, status = 'published', Last_Sync = ? WHERE tk_id = ?",
        vals
    )
    conn.commit()
    conn.close()

    print(f"  [✅ SQLite] Đã cập nhật SQLite cục bộ. Trạng thái -> published")

    # Đẩy lên Google Sheets Pool
    print("  [⚡ Google Sheets] Đang tự động đẩy cập nhật chép đè lên Sheets Pool...")
    res_publish = manager.execute_publish_listing(tk_id)
    if res_publish.get("status") == "success":
        print(f"  [✅ Sheets Success] Đã sửa đổi xoay thẳng đứng và cập nhật thành công căn {tk_id} lên Google Sheets Pool!")
        return True
    else:
        print(f"  [⚠️ Sheets Failed] Cập nhật Sheets thất bại: {res_publish.get('message')}. Vui lòng đẩy thủ công.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Fix rotated images for previously migrated listings.")
    parser.add_argument("--dry-run", action="store_true", help="Quét thử nghiệm đếm số căn lỗi mà không sửa thực tế.")
    parser.add_argument("--limit", type=int, default=None, help="Giới hạn số lượng căn lỗi cần sửa để chạy thử nghiệm.")
    parser.add_argument("--all", action="store_true", help="Chạy sửa toàn bộ các căn lỗi được phát hiện.")
    parser.add_argument("--tk-id", type=str, default=None, help="Chỉ định ID căn Thiên Khôi cụ thể để sửa.")
    args = parser.parse_args()

    db_file = "raw_archive.db"
    if not os.path.exists(db_file):
        print("[❌ LỖI] Không tìm thấy file SQLite raw_archive.db")
        return

    # Tải cấu hình & Cookie
    cfg = manager.load_config()
    cookie = ""
    if os.path.exists("thienkhoi_cookie.txt"):
        try:
            with open("thienkhoi_cookie.txt", "r", encoding="utf-8") as f:
                cookie = f.read().strip()
        except Exception:
            pass

    headers_tk = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie
    }

    # Truy vấn từ SQLite
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if args.tk_id:
        print(f"[🔎] Đang lấy thông tin căn chỉ định tk_id = '{args.tk_id}'...")
        rows = cursor.execute("SELECT * FROM listings WHERE tk_id = ?", (args.tk_id,)).fetchall()
    else:
        # Tự động lấy ngày hiện tại ở cả 2 định dạng để loại trừ các căn đã đồng bộ hôm nay
        today_str1 = datetime.now().strftime("%d/%m/%Y")
        today_str2 = datetime.now().strftime("%Y-%m-%d")
        print(f"[🔎] Đang lấy danh sách căn cần quét (loại trừ ngày hôm nay: {today_str1} và {today_str2})...")
        rows = cursor.execute(
            "SELECT * FROM listings WHERE status = 'published' AND `Last_Sync` NOT LIKE ? AND `Last_Sync` NOT LIKE ?",
            (f"%{today_str1}%", f"%{today_str2}%")
        ).fetchall()
    conn.close()

    if not rows:
        print("[✅] Không tìm thấy căn cũ nào cần kiểm tra trong SQLite database!")
        return

    print(f"[🔎] Bắt đầu quét các căn đã di cư trước đây để tìm lỗi xoay ảnh 90 độ...")

    tilted_listings = []
    
    # ĐỊNH HẠN QUÉT ĐỂ DỪNG SỚM (EARLY STOPPING BATCH SCANNER - TỐI ƯU CỰC ĐẠI)
    limit_scan = args.limit if args.limit else (5 if not args.all else 999999)
    if args.dry_run:
        limit_scan = 999999 # dry run thì quét hết để đếm

    # Chạy đa luồng quét nhanh EXIF (Tối đa 15 luồng đồng thời vì chỉ check Header EXIF, không tốn tài nguyên)
    def scan_single_row(row_dict):
        tk_id = row_dict["tk_id"]
        try:
            is_tilted, details = check_listing_tilted(row_dict, headers_tk)
            if is_tilted:
                return row_dict
        except Exception as e:
            pass
        return None

    row_dicts = [dict(r) for r in rows]
    
    # Phân phối theo từng lô 15 căn để dừng sớm ngay khi tìm đủ limit_scan
    batch_size = 15
    print(f"[⚡] Đang quét nhanh EXIF song song đa luồng theo lô {batch_size} căn...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        for idx_batch in range(0, len(row_dicts), batch_size):
            if len(tilted_listings) >= limit_scan:
                break
                
            batch = row_dicts[idx_batch : idx_batch + batch_size]
            results = executor.map(scan_single_row, batch)
            
            for r_dict in results:
                if r_dict:
                    tilted_listings.append(r_dict)
                    if len(tilted_listings) >= limit_scan:
                        break

    print(f"\n[📊 THỐNG KÊ QUÉT]")
    print(f"- Phát hiện thực tế: {len(tilted_listings)} căn bị lỗi xoay ảnh 90 độ.")

    if not tilted_listings:
        print("[✅] Không tìm thấy căn cũ nào có hình ảnh bị lỗi xoay 90 độ trong lô quét.")
        return

    if args.dry_run:
        print("\n[🏁 DRY-RUN HOÀN TẤT] Hãy chạy thực tế bằng cách bỏ tham số --dry-run.")
        return

    to_process = tilted_listings
    if args.limit:
        to_process = tilted_listings[:args.limit]
    elif not args.all:
        to_process = tilted_listings[:5] # Fallback an toàn mặc định 5 căn

    print(f"\n[🚀] BẮT ĐẦU SỬA: Sẽ xử lý {len(to_process)} căn bị lỗi xoay ảnh...")
    
    success_count = 0
    for idx, row in enumerate(to_process):
        tk_id = row["tk_id"]
        print(f"\n📦 [{idx+1}/{len(to_process)}] Sửa xoay hình căn {tk_id}...")
        try:
            res = re_migrate_listing_images(tk_id, row, cookie, cfg)
            if res:
                success_count += 1
            time.sleep(1.5) # Throttling nhẹ chống quá tải Sheets API
        except Exception as e:
            print(f"  [❌ LỖI] Lỗi hệ thống khi sửa căn {tk_id}: {str(e)}")

    print(f"\n[🏁 HOÀN TẤT] Tiến trình sửa lỗi xoay ảnh hoàn tất!")
    print(f"- Đã xử lý thành công: {success_count}/{len(to_process)} căn.")

if __name__ == '__main__':
    main()
