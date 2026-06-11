import os
import sys
import json
import time
import sqlite3
import requests
import random
from datetime import datetime

# Đảm bảo import được các hàm và cấu hình từ curator_server.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from manager import (
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
    print("🚀 BẮT ĐẦU QUY TRÌNH SỬA LỖI NÉN ẢNH SƠ ĐỒ THỬA ĐẤT CHO CÁC CĂN ĐÃ DI CƯ")
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

    rows = []
    try:
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
    except sqlite3.OperationalError as e:
        if "no such table" in str(e).lower():
            print("[ℹ Sandbox Mode] Bảng listings chưa tồn tại trong Database SQLite rỗng. Bỏ qua sửa ảnh sơ đồ.")
            conn.close()
            return
        else:
            conn.close()
            raise e
    
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
                    from manager import execute_publish_listing
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


def run_cleanup_diagrams(limit=None, do_publish=False):
    print("======================================================================")
    print("🧹 BẮT ĐẦU QUY TRÌNH DỌN DẸP & ĐÔN ẢNH NHÀ THẬT CHO RỔ HÀNG CŨ")
    print("👉 Áp dụng thuật toán Zero-Comparison (Cắt index đầu mảng của anh Khang Ngô)")
    if do_publish:
        print("⚡ [KÍCH HOẠT SHEETS] Cập nhật an toàn bằng Batch Update không liên tục!")
    print("======================================================================")
    
    if not os.path.exists(DB_FILE):
        print(f"[❌] Database SQLite {DB_FILE} không tồn tại!")
        return

    # 1. Truy vấn các căn đã di cư
    conn = sqlite3.connect(DB_FILE, timeout=30.0)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    col_sodo1_key = get_safe_col_name("Sơ đồ thửa đất 1")
    col_sodo2_key = get_safe_col_name("Sơ đồ thửa đất 2")
    col_sodo3_key = get_safe_col_name("Sơ đồ thửa đất 3")
    col_sodo4_key = get_safe_col_name("Sơ đồ thửa đất 4")
    col_sodo5_key = get_safe_col_name("Sơ đồ thửa đất 5")
    
    rows = []
    try:
        # Lấy toàn bộ các hàng đã di cư xong
        rows = cursor.execute(
            "SELECT * FROM listings WHERE status = 'raw_complete' OR status = 'published'"
        ).fetchall()
    except sqlite3.OperationalError as e:
        if "no such table" in str(e).lower():
            print("[ℹ Sandbox Mode] Bảng listings chưa tồn tại trong Database SQLite rỗng. Bỏ qua quét dọn database.")
            conn.close()
            return
        else:
            conn.close()
            raise e
            
    conn.close()

    if not rows:
        print("[✅] Không tìm thấy căn nào đã di cư trong SQLite để dọn dẹp.")
        return

    print(f"[i] Tìm thấy {len(rows)} căn đã di cư cần quét kiểm tra.")
    if limit:
        print(f"[i] Giới hạn kiểm tra: {limit} căn.")

    repaired_items = []
    processed = 0
    db_updated = 0

    for row in rows:
        if limit and processed >= limit:
            break
            
        processed += 1
        row = dict(row)
        tk_id = row["tk_id"]
        row_db_id = row["id"]
        
        # 1. Đếm số lượng hình sơ đồ cào được ban đầu (khác rỗng và là link hợp lệ)
        sodo_count = 0
        for col in [col_sodo1_key, col_sodo2_key, col_sodo3_key, col_sodo4_key, col_sodo5_key]:
            val = row.get(col, "")
            if val and str(val).strip().startswith("http"):
                sodo_count += 1
                
        if sodo_count == 0:
            # Không có hình sổ nào cào được, chắc chắn không bị gộp lẫn sổ ở đầu
            continue

        # 2. Đọc mảng di cư raw_drive_images_json
        try:
            raw_drive_images = json.loads(row["raw_drive_images_json"]) if row.get("raw_drive_images_json") else []
        except Exception:
            continue

        if not raw_drive_images:
            continue

        # 3. Thuật toán Zero-Comparison: Cắt bỏ N phần tử đầu tiên khỏi mảng di cư
        if len(raw_drive_images) >= sodo_count:
            clean_house_links = raw_drive_images[sodo_count:]
        else:
            clean_house_links = list(raw_drive_images)

        # Tạo danh sách 15 ảnh thường mới sạch (fill rỗng cho đủ 15 phần tử)
        new_interior_imgs = [""] * 15
        for idx, img in enumerate(clean_house_links):
            if idx < 15:
                new_interior_imgs[idx] = img

        # Đọc 15 cột ảnh thường hiện tại trong SQLite để so sánh
        current_imgs = []
        for i in range(15):
            col_name = get_safe_col_name(f"Ảnh {i+1}")
            current_imgs.append(row.get(col_name, "") or "")

        # So sánh xem có sự thay đổi thực sự không
        has_difference = False
        for i in range(15):
            if current_imgs[i] != new_interior_imgs[i]:
                has_difference = True
                break

        if has_difference:
            # 4. Cập nhật SQLite cục bộ cho 15 cột ảnh thường sạch
            conn = sqlite3.connect(DB_FILE, timeout=30.0)
            cursor = conn.cursor()
            
            update_sql_parts = []
            update_vals = []
            for i in range(15):
                col_name = get_safe_col_name(f"Ảnh {i+1}")
                update_sql_parts.append(f"`{col_name}` = ?")
                update_vals.append(new_interior_imgs[i])
                
            update_vals.append(row_db_id)
            cursor.execute(
                f"UPDATE listings SET {', '.join(update_sql_parts)} WHERE id = ?",
                update_vals
            )
            conn.commit()
            conn.close()
            db_updated += 1
            
            # Lấy chỉ số dòng Google Sheets của căn này lưu trong database
            # pool_row_index lưu chỉ số dòng thực tế trên Sheets Pool
            sheet_row_idx = row.get("pool_row_index")
            try:
                sheet_row_idx = int(sheet_row_idx) if sheet_row_idx else None
            except ValueError:
                sheet_row_idx = None
                
            if sheet_row_idx:
                repaired_items.append({
                    "tk_id": tk_id,
                    "row_idx": sheet_row_idx,
                    "row_values": new_interior_imgs
                })
                print(f"  [🧹 SQLite Cleaned] Căn {tk_id}: Lẫn {sodo_count} hình sổ. Đã cắt index & dồn ảnh nhà thật lên trước (Dòng Sheets: {sheet_row_idx})")
            else:
                print(f"  [🧹 SQLite Cleaned (Không tìm thấy dòng Sheets)] Căn {tk_id}: Đã cắt lẫn {sodo_count} hình sổ trong SQLite cục bộ.")

    print(f"\n[💾 SQLite Success] Đã dọn dẹp và cập nhật database cục bộ thành công cho {db_updated} căn bị lỗi.")

    # 5. Đồng bộ hàng loạt lên Google Sheets Pool (Batch Update không liên tục)
    if do_publish and repaired_items:
        print(f"\n[⚡ Google Sheets] Bắt đầu đồng bộ hàng loạt (Batch Update) cho {len(repaired_items)} căn lên Pool sheet...")
        try:
            import gspread
            creds = get_google_credentials()
            cfg = load_config()
            sheet_id = cfg.get("sheet_id")
            
            if not creds or not sheet_id:
                print("[❌ LỖI] Không tìm thấy credentials.json hoặc sheet_id trong cấu hình để đồng bộ Sheets!")
                return
                
            client = gspread.authorize(creds)
            spreadsheet = client.open_by_key(sheet_id)
            
            try:
                sheet = spreadsheet.worksheet("Pool")
            except Exception:
                sheet = spreadsheet.get_worksheet(0)
                
            # Chia thành từng nhóm tối đa 100 dòng để tránh quá tải kích thước payload request Google API
            batch_size = 100
            groups = [repaired_items[i:i + batch_size] for i in range(0, len(repaired_items), batch_size)]
            
            synced_count = 0
            for g_idx, group in enumerate(groups, start=1):
                print(f"  -> Đang đẩy Nhóm {g_idx}/{len(groups)} ({len(group)} dòng)...")
                batch_data = []
                for item in group:
                    # Ghi đè duy nhất dải ô AO{R}:BC{R} (15 cột ảnh thường từ Ảnh 1 đến Ảnh 15)
                    batch_data.append({
                        'range': f"AO{item['row_idx']}:BC{item['row_idx']}",
                        'values': [item['row_values']]
                    })
                
                # Gọi API batch_update của gspread
                sheet.batch_update(batch_data, value_input_option='USER_ENTERED')
                synced_count += len(group)
                
                # Throttling nhẹ 1.0 giây giữa các batch để bảo vệ API an toàn tuyệt đối
                time.sleep(1.0)
                
            print(f"[✅ Sheets Success] Đã đồng bộ chép đè an toàn thành công {synced_count} căn lên Google Sheets Pool!")
            
            # Cập nhật trạng thái SQLite sang 'published' cho các căn đã đồng bộ xong
            conn = sqlite3.connect(DB_FILE, timeout=30.0)
            cursor = conn.cursor()
            for item in repaired_items:
                cursor.execute(
                    "UPDATE listings SET status = 'published', `Last_Sync` = ? WHERE tk_id = ?",
                    (datetime.now().strftime("%d/%m/%Y %H:%M:%S"), item["tk_id"])
                )
            conn.commit()
            conn.close()
            print("  💾 Đã cập nhật trạng thái SQLite sang 'published' thành công.")
            
        except Exception as e:
            print(f"[❌ Sheets Error] Gặp sự cố trong tiến trình Batch Update Sheets: {str(e)}")

    print("======================================================================")
    print(f"🏁 HOÀN TẤT DỌN DẸP: Đã quét {processed} căn, dọn dẹp sạch {db_updated} căn bị lỗi.")
    print("======================================================================")


if __name__ == "__main__":
    limit_val = None
    do_publish = False
    do_cleanup = False
    
    # Duyệt đối số dòng lệnh thông minh
    for arg in sys.argv[1:]:
        if arg == "--publish":
            do_publish = True
        elif arg == "--cleanup":
            do_cleanup = True
        else:
            try:
                limit_val = int(arg)
            except ValueError:
                pass
                
    if do_cleanup:
        run_cleanup_diagrams(limit_val, do_publish)
    else:
        run_repair_diagrams(limit_val, do_publish)
