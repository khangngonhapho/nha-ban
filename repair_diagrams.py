import os
import sys
import json
import time
import sqlite3
import requests
import random

# Đảm bảo import được các hàm và cấu hình từ curator_server.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from curator_server import (
    load_config, get_google_credentials, get_google_access_token,
    download_image_with_retry, upload_image_to_drive, upload_image_to_cloudinary,
    get_safe_col_name, DB_FILE, add_log_message
)

def find_sodo_index(orig_sodo, raw_images_tk, raw_drive_images, fallback_idx=None):
    if not orig_sodo:
        return -1
    # 1. Nếu sơ đồ đang là link thô Thiên Khôi
    if orig_sodo in raw_images_tk:
        return raw_images_tk.index(orig_sodo)
    # 2. Nếu sơ đồ đã di cư (link Cloudinary/Drive) nằm trong raw_drive_images
    if orig_sodo in raw_drive_images:
        return raw_drive_images.index(orig_sodo)
    # 3. Fallback dùng index dự đoán nếu hợp lệ
    if fallback_idx is not None and fallback_idx < len(raw_images_tk):
        return fallback_idx
    return -1

def run_repair_diagrams(limit=None, do_publish=False):
    print("======================================================================")
    print("🚀 BẮT ĐẦU QUY TRÌNH SỬA LỖI NÉN ẢNH SƠ ĐỒ THỬA ĐẤT CHO 5000 CĂN ĐÃ DI CƯ")
    if do_publish:
        print("⚡ [KÍCH HOẠT US-040] Hệ thống sẽ tự động xuất bản (Publish) lên Google Sheets Pool!")
    print("======================================================================")
    
    if not os.path.exists(DB_FILE):
        print(f"[❌] Database SQLite {DB_FILE} không tồn tại!")
        return

    # 1. Tải cấu hình uploader
    cfg = load_config()
    cld_cloud_name = cfg.get("cloudinary_cloud_name")
    cld_api_key = cfg.get("cloudinary_api_key")
    cld_api_secret = cfg.get("cloudinary_api_secret")
    use_cloudinary = bool(cld_cloud_name and cld_api_key and cld_api_secret)

    creds = None
    token = None
    drive_parent_folder = None
    if not use_cloudinary:
        creds = get_google_credentials()
        token = get_google_access_token(creds)
        drive_parent_folder = cfg.get("drive_folder_id")

    cookie = ""
    if os.path.exists("thienkhoi_cookie.txt"):
        with open("thienkhoi_cookie.txt", "r", encoding="utf-8") as f:
            cookie = f.read().strip()

    headers_tk = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": cookie
    }

    # 2. Truy vấn các căn đã di cư cần sửa đổi
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    col_sodo1_key = get_safe_col_name("Sơ đồ thửa đất 1")
    col_sodo2_key = get_safe_col_name("Sơ đồ thửa đất 2")
    col_sodo3_key = get_safe_col_name("Sơ đồ thửa đất 3")
    col_sodo4_key = get_safe_col_name("Sơ đồ thửa đất 4")
    col_sodo5_key = get_safe_col_name("Sơ đồ thửa đất 5")

    # Truy vấn các hàng đã di cư (raw_complete hoặc published) và có ít nhất 1 ảnh sơ đồ
    rows = cursor.execute(
        f"SELECT * FROM listings WHERE (status = 'raw_complete' OR status = 'published') AND ("
        f"({col_sodo1_key} IS NOT NULL AND {col_sodo1_key} != '') OR "
        f"({col_sodo2_key} IS NOT NULL AND {col_sodo2_key} != '') OR "
        f"({col_sodo3_key} IS NOT NULL AND {col_sodo3_key} != '') OR "
        f"({col_sodo4_key} IS NOT NULL AND {col_sodo4_key} != '') OR "
        f"({col_sodo5_key} IS NOT NULL AND {col_sodo5_key} != '')"
        f")"
    ).fetchall()
    
    conn.close()

    if not rows:
        print("[✅] Không tìm thấy căn nào cần sửa đổi ảnh sơ đồ.")
        return

    print(f"[i] Tìm thấy {len(rows)} căn đã di cư có chứa ảnh sơ đồ.")
    if limit:
        print(f"[i] Giới hạn xử lý: {limit} căn.")

    processed = 0
    repaired = 0

    for row in rows:
        if limit and processed >= limit:
            break
            
        processed += 1
        row = dict(row)
        tk_id = row["tk_id"]
        row_db_id = row["id"]
        
        # Đọc dữ liệu ảnh gốc và ảnh đã di cư
        try:
            raw_images_tk = json.loads(row["raw_images_tk_json"]) if row["raw_images_tk_json"] else []
            raw_drive_images = json.loads(row["raw_drive_images_json"]) if row["raw_drive_images_json"] else []
        except Exception:
            continue

        if not raw_images_tk or not raw_drive_images:
            continue

        # Lấy URL sơ đồ gốc
        orig_sodo1 = row[col_sodo1_key] if col_sodo1_key in row.keys() else None
        orig_sodo2 = row[col_sodo2_key] if col_sodo2_key in row.keys() else None
        orig_sodo3 = row[col_sodo3_key] if col_sodo3_key in row.keys() else None
        orig_sodo4 = row[col_sodo4_key] if col_sodo4_key in row.keys() else None
        orig_sodo5 = row[col_sodo5_key] if col_sodo5_key in row.keys() else None

        # Đối chiếu tìm index chính xác và an toàn của 5 sơ đồ
        sodo1_idx = find_sodo_index(orig_sodo1, raw_images_tk, raw_drive_images, fallback_idx=0 if orig_sodo1 else None)
        sodo2_idx = find_sodo_index(orig_sodo2, raw_images_tk, raw_drive_images, fallback_idx=1 if orig_sodo2 else None)
        sodo3_idx = find_sodo_index(orig_sodo3, raw_images_tk, raw_drive_images, fallback_idx=2 if orig_sodo3 else None)
        sodo4_idx = find_sodo_index(orig_sodo4, raw_images_tk, raw_drive_images, fallback_idx=3 if orig_sodo4 else None)
        sodo5_idx = find_sodo_index(orig_sodo5, raw_images_tk, raw_drive_images, fallback_idx=4 if orig_sodo5 else None)

        need_update = False
        new_sodo_urls = [row[col_sodo1_key], row[col_sodo2_key], row[col_sodo3_key], row[col_sodo4_key], row[col_sodo5_key]]
        updated_drive_images = list(raw_drive_images)

        # 3. Tạo thư mục Drive nếu cần
        house_folder_id = None
        if not use_cloudinary and token:
            house_folder_id = drive_parent_folder

        # Chạy làm mới cho cả 5 Sơ đồ thửa đất
        for i, (idx, orig_sodo) in enumerate(zip(
            [sodo1_idx, sodo2_idx, sodo3_idx, sodo4_idx, sodo5_idx],
            [orig_sodo1, orig_sodo2, orig_sodo3, orig_sodo4, orig_sodo5]
        ), start=1):
            if idx != -1 and idx < len(raw_images_tk):
                orig_url = raw_images_tk[idx]
                print(f"[{processed}/{len(rows)}] Căn {tk_id}: Đang làm mới Sơ đồ {i}...")
                
                img_data = download_image_with_retry(orig_url, headers_tk)
                if img_data:
                    filename = f"img_{tk_id}_{idx+1}.jpg"
                    orig_kb = int(len(img_data) / 1024)
                    
                    # Tải lên Cloud/Drive KHÔNG NÉN
                    if use_cloudinary:
                        cld_folder = f"BDS-KhangNgo/{tk_id}"
                        new_url = upload_image_to_cloudinary(
                            img_data, filename, cld_cloud_name, cld_api_key, cld_api_secret, folder=cld_folder
                        )
                    elif token:
                        new_url = upload_image_to_drive(img_data, filename, house_folder_id, token)
                    else:
                        new_url = ""

                    if new_url:
                        new_sodo_urls[i-1] = new_url
                        # Cập nhật trong mảng ảnh drive
                        if idx < len(updated_drive_images):
                            updated_drive_images[idx] = new_url
                        need_update = True
                        print(f"  [🛡️ Sơ đồ {i}] Thành công! Đã đẩy sơ đồ nguyên bản ({orig_kb}KB) -> {new_url}")

        # 4. Ghi nhận cập nhật vào SQLite nếu có thay đổi
        if need_update:
            conn = sqlite3.connect(DB_FILE, timeout=30.0)
            cursor = conn.cursor()
            
            cursor.execute(
                f"UPDATE listings SET {col_sodo1_key} = ?, {col_sodo2_key} = ?, {col_sodo3_key} = ?, {col_sodo4_key} = ?, {col_sodo5_key} = ?, raw_drive_images_json = ? WHERE id = ?",
                (new_sodo_urls[0], new_sodo_urls[1], new_sodo_urls[2], new_sodo_urls[3], new_sodo_urls[4], json.dumps(updated_drive_images), row_db_id)
            )
            conn.commit()
            conn.close()
            repaired += 1
            print(f"  [💾 SQLite] Đã cập nhật thành công link Sơ đồ nguyên bản vào Database cho căn {tk_id}!")
            
            # Lấy thông tin địa chỉ và tiêu đề căn để hiển thị rõ ràng
            tieu_de_col = get_safe_col_name("Tiêu đề Public")
            tieu_de_raw = row[tieu_de_col] if tieu_de_col in row.keys() else ""
            tieu_de = str(tieu_de_raw or "").strip()
            
            so_nha = str(row.get("Ngo_So_nha", "") or row.get("Ng__S__nh_", "") or "").strip()
            duong = str(row.get("Duong", "") or row.get("___ng", "") or "").strip()
            quan = str(row.get("Quan", "") or row.get("Qu_n", "") or "").strip()
            dia_chi = f"{so_nha} {duong}, Quận {quan}".strip().strip(",")
            
            print("  ┌──────────────────────────────────────────────────────────────────┐")
            print(f"  │ 🏡 THÔNG TIN CĂN NHÀ ĐANG SỬA:                                    │")
            print(f"  │    - Địa chỉ: {dia_chi:<50} │")
            print(f"  │    - Tiêu đề: {tieu_de[:48]:<50}... │")
            print(f"  │    - Mã TK  : {tk_id:<50} │")
            print("  └──────────────────────────────────────────────────────────────────┘")
            
            # 1. In hẳn ra link dạng trần để Ctrl+Click cực tiện
            print(f"  👉 LINK SƠ ĐỒ THỨA ĐẤT SIÊU NÉT (Dùng tổ hợp phím Ctrl + Click vào link dưới để xem):")
            for j, u in enumerate(new_sodo_urls, start=1):
                if u and u.startswith("http"):
                    print(f"     LINK {j}: {u}")
                
            # 2. Tự động bật trình duyệt hiển thị sơ đồ siêu nét cho căn đầu tiên được sửa
            if repaired == 1:
                first_valid_sodo = next((u for u in new_sodo_urls if u and u.startswith("http")), None)
                if first_valid_sodo:
                    print(f"  [🌐 Trình duyệt] Đang tự động mở sơ đồ siêu nét của căn trên trình duyệt...")
                    try:
                        import webbrowser
                        webbrowser.open(first_valid_sodo)
                    except Exception as wb_err:
                        print(f"  [⚠️] Không thể mở tự động trình duyệt: {str(wb_err)}")

            # 3. TỰ ĐỘNG PUBLISH LÊN GOOGLE SHEETS POOL (US-040)
            if do_publish:
                print(f"  [⚡ Sheets Pool] Đang đồng bộ và đẩy dữ liệu căn {tk_id} lên Google Sheets...")
                try:
                    from curator_server import execute_publish_listing
                    res_pub = execute_publish_listing(tk_id)
                    if res_pub.get("status") == "success":
                        print(f"     [✅ Sheets Success] Đã đẩy thành công dữ liệu căn {tk_id} lên Google Sheets Pool!")
                    else:
                        print(f"     [⚠️ Sheets Warning] Lỗi đẩy Sheets: {res_pub.get('message')}")
                except Exception as pub_err:
                    print(f"     [❌ Sheets Error] Gặp sự cố khi tự động đẩy Sheets: {str(pub_err)}")

        # Throttling tàng hình để tránh spam API
        time.sleep(random.uniform(1.0, 2.0))

    print("======================================================================")
    print(f"🏁 HOÀN TẤT LÀM MỚI ẢNH SƠ ĐỒ: Đã rà soát {processed} căn, làm mới thành công {repaired} căn.")
    print("======================================================================")

if __name__ == "__main__":
    limit_val = None
    do_publish = False
    
    # Duyệt đối số dòng lệnh thông minh
    for arg in sys.argv[1:]:
        if arg == "--publish":
            do_publish = True
        else:
            try:
                limit_val = int(arg)
            except ValueError:
                pass
                
    run_repair_diagrams(limit_val, do_publish)
