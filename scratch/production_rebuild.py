# -*- coding: utf-8 -*-
"""
Script cứu hộ tái thiết dữ liệu Production BDS KhangNgo (US-152) - Gộp tinh giản v2
Hỗ trợ hai chế độ:
  1. --prepare: Sao lưu CSDL, cấu hình R2 v3, làm sạch DB Production, trích xuất danh sách 100% căn cần cào.
  2. --run: Chạy cào dữ liệu thô, di cư ảnh lên R2 v3 và đồng bộ lên Google Sheets theo mẻ lớn (Batch sync).
"""

import os
import json
import sqlite3
import sys
import time
import base64
import random
import argparse
import requests
from datetime import datetime

# Thêm thư mục root dự án vào sys.path để import các module local
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import manager
import fetcher
import pool_lego

JSON_CONTROL_FILE = os.path.join("scratch", "listings_to_rebuild.json")
ERROR_REPORT_FILE = os.path.join("scratch", "rebuild_errors_report.json")

def load_config():
    with open("settings.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def get_token_exp(access_token):
    """Giải mã JWT thô để đọc trường exp (không cần verify signature)"""
    try:
        parts = access_token.split('.')
        if len(parts) != 3:
            return 0
        payload_b64 = parts[1]
        # Bổ sung padding cho base64url hợp lệ
        payload_b64 += '=' * (4 - len(payload_b64) % 4)
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes)
        return payload.get("exp", 0)
    except Exception as e:
        print(f"  - [⚠️ Exp Check] Không thể decode JWT token: {e}")
        return 0

def check_and_active_refresh_cookie(cookie_file):
    """Kiểm tra thời hạn token chủ động. Nếu còn dưới 5 phút, tự động gọi refresh trước khi cào."""
    if not os.path.exists(cookie_file):
        return None
    try:
        with open(cookie_file, "r", encoding="utf-8") as f:
            cookie_str = f.read().strip()
        
        access_token, refresh_token, _ = fetcher.extract_tokens(cookie_str)
        if not access_token:
            return cookie_str
            
        exp_time = get_token_exp(access_token)
        if exp_time == 0:
            return cookie_str
            
        remaining_seconds = exp_time - time.time()
        print(f"  - [🔑 Auth] Access Token còn hiệu lực: {remaining_seconds:.1f} giây (~{remaining_seconds/60:.1f} phút).")
        
        # Nếu còn dưới 5 phút (300 giây) hoặc đã quá hạn -> Chủ động refresh
        if remaining_seconds < 300:
            print("  - [🔑 Auth] Token sắp hết hạn hoặc đã hết hạn. Đang chủ động refresh token...")
            refreshed = fetcher.try_refresh_tokens(cookie_file)
            if refreshed:
                print("  - [🎉 Auth] Chủ động refresh token thành công!")
                return refreshed
            else:
                print("  - [⚠️ Auth] Không thể chủ động refresh token. Sẽ dùng tiếp token cũ làm fallback.")
    except Exception as e:
        print(f"  - [⚠️ Auth] Lỗi kiểm tra/refresh token chủ động: {e}")
    return None

def log_error_report(tk_id, status_code, reason):
    """Ghi nhận log report chi tiết các căn gặp lỗi để PO rà soát"""
    errors = []
    if os.path.exists(ERROR_REPORT_FILE):
        try:
            with open(ERROR_REPORT_FILE, "r", encoding="utf-8") as f:
                errors = json.load(f)
        except Exception:
            pass
            
    # Tránh trùng lặp log
    errors = [e for e in errors if e.get("tk_id") != tk_id]
    errors.append({
        "tk_id": tk_id,
        "status_code": status_code,
        "reason": reason,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })
    
    with open(ERROR_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=4, ensure_ascii=False)
    print(f"  - [🚨 Error Log] Đã ghi nhận căn lỗi {tk_id} vào {ERROR_REPORT_FILE}")

def prepare_rebuild():
    print("[+] KHỞI ĐỘNG CHẾ ĐỘ CHUẨN BỊ (PREPARE)...")
    
    # 1. Cấu hình R2 v3
    cfg = load_config()
    current_prefix = cfg.get("r2_migration_prefix", "")
    target_prefix = "BDS-KhangNgo-v3"
    if current_prefix != target_prefix:
        cfg["r2_migration_prefix"] = target_prefix
        save_config(cfg)
        print(f"  - [Cấu hình R2] Đã cập nhật r2_migration_prefix thành '{target_prefix}' trong settings.json")
    else:
        print(f"  - [Cấu hình R2] prefix đã là '{target_prefix}'")

    # 2. Xác định đường dẫn file CSDL
    db_dir = cfg.get("database_dir", "")
    if not db_dir:
        print("[-] LỖI: Chưa cấu hình database_dir trong settings.json")
        sys.exit(1)
        
    master_db_path = os.path.join(db_dir, "raw_archive.db")
    staging_db_path = os.path.join(db_dir, "raw_archive_staging.db")
    
    print(f"  - Database Production: {master_db_path}")
    print(f"  - Database Staging: {staging_db_path}")
    
    if not os.path.exists(master_db_path):
        print(f"[-] LỖI: Không tìm thấy tệp CSDL Production tại {master_db_path}")
        sys.exit(1)
        
    if not os.path.exists(staging_db_path):
        print(f"[-] LỖI: Không tìm thấy tệp CSDL Staging tại {staging_db_path}. Vui lòng sao chép file này sang cùng thư mục DB.")
        sys.exit(1)

    # 3. Sao lưu database Production hiện tại
    backup_dir = "BDS_Backups"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"raw_archive_pre_rebuild_backup_{timestamp}.db")
    
    import shutil
    try:
        shutil.copy2(master_db_path, backup_path)
        print(f"  - [Backup] Đã sao lưu CSDL Production thành công sang {backup_path}")
    except Exception as e:
        print(f"[-] LỖI: Không thể sao lưu CSDL: {str(e)}")
        sys.exit(1)

    # 4. Đọc danh sách tk_id từ CSDL Staging
    # [US-152] PO yêu cầu lấy HẾT TẤT CẢ các căn để cào lại mới, không phân biệt trạng thái hoạt động
    print("  - [Staging] Đang quét danh sách các căn cần rebuild từ CSDL Staging...")
    conn_st = sqlite3.connect(staging_db_path)
    cursor_st = conn_st.cursor()
    rows = cursor_st.execute("SELECT tk_id FROM listings").fetchall()
    conn_st.close()
    
    target_ids = [r[0] for r in rows if r[0]]
    print(f"  - [Staging] Phát hiện tổng cộng {len(target_ids)} căn cần rebuild.")

    # 5. Lưu danh sách JSON kiểm soát
    os.makedirs("scratch", exist_ok=True)
    control_list = []
    
    # Nếu file JSON kiểm soát đã có, giữ lại trạng thái cũ để tránh cào đè
    existing_control = {}
    if os.path.exists(JSON_CONTROL_FILE):
        try:
            with open(JSON_CONTROL_FILE, "r", encoding="utf-8") as f:
                old_list = json.load(f)
                existing_control = {item["tk_id"]: item["status"] for item in old_list}
            print(f"  - [Kiểm soát] Đã tìm thấy tệp {JSON_CONTROL_FILE} cũ. Giữ lại trạng thái để tiếp tục.")
        except Exception:
            pass

    for tk_id in target_ids:
        status = existing_control.get(tk_id, "pending")
        control_list.append({"tk_id": tk_id, "status": status})
        
    with open(JSON_CONTROL_FILE, "w", encoding="utf-8") as f:
        json.dump(control_list, f, indent=4, ensure_ascii=False)
    print(f"  - [Kiểm soát] Đã tạo/cập nhật tệp kiểm soát {JSON_CONTROL_FILE}")

    # 6. Làm sạch CSDL Production
    print("  - [Database] Đang làm sạch dữ liệu trong CSDL Production...")
    conn_prd = sqlite3.connect(master_db_path)
    cursor_prd = conn_prd.cursor()
    try:
        cursor_prd.execute("DELETE FROM listings")
        cursor_prd.execute("DELETE FROM listings_images")
        cursor_prd.execute("DELETE FROM sqlite_sequence WHERE name = 'listings'")
        cursor_prd.execute("DELETE FROM sqlite_sequence WHERE name = 'listings_images'")
        conn_prd.commit()
        print("  - [Database] Đã làm sạch các bảng listings và listings_images thành công.")
    except Exception as e_db:
        print(f"[-] LỖI: Không thể làm sạch CSDL: {str(e_db)}")
        sys.exit(1)
    finally:
        conn_prd.close()

    print("[✅] BƯỚC CHUẨN BỊ HOÀN THÀNH THÀNH CÔNG! SẴN SÀNG CHO BƯỚC CÀO REBUILD.")

def batch_publish_to_sheets(tk_ids):
    """
    Đồng bộ hàng loạt danh sách tk_ids vừa cào lên Google Sheets bằng gspread batch append.
    Giúp tránh Rate Limit 429 và tăng tốc độ xử lý lên gấp 100 lần.
    """
    if not tk_ids:
        return
    print(f"\n⚡ [Sheets Batch] Bắt đầu đồng bộ hàng loạt {len(tk_ids)} căn lên Google Sheets...")
    
    cfg = load_config()
    db_file = os.path.join(cfg.get("database_dir"), "raw_archive.db")
    
    # 1. Đọc dữ liệu từ SQLite
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    rows_data_to_append = []
    
    for tk_id in tk_ids:
        row = cursor.execute("SELECT * FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
        if not row:
            continue
            
        d = dict(row)
        
        # Xử lý phân rã hình ảnh giống hệt logic pool_lego.publish_listing
        curated_json = d.get("curated_config_json")
        diagrams = []
        facades = []
        covers = []
        alleys = []
        interiors = []
        
        if curated_json:
            try:
                curated_data = json.loads(curated_json)
                images_list = curated_data.get("images", []) if isinstance(curated_data, dict) else (curated_data if isinstance(curated_data, list) else [])
                for img in images_list:
                    if not isinstance(img, dict) or img.get("role") in ["Ẩn", "hidden", "deleted"]:
                        continue
                    url = img.get("url")
                    role = img.get("role")
                    if not url:
                        continue
                    if role == "Sơ đồ":
                        diagrams.append(url)
                    elif role == "Mặt tiền":
                        facades.append(url)
                    elif role == "Bìa":
                        covers.append(url)
                    elif role == "Hẻm":
                        alleys.append(url)
                    else:
                        interiors.append(url)
            except Exception:
                pass
                
        cover_url = covers[0] if covers else (facades[0] if facades else (interiors[0] if interiors else ""))
        d[pool_lego.get_safe_col_name("Hình Nhận Diện")] = cover_url
        d[pool_lego.get_safe_col_name("Hình Mặt Tiền")] = facades[0] if facades else ""
        
        for idx in range(5):
            d[pool_lego.get_safe_col_name(f"Sơ đồ thửa đất {idx+1}")] = diagrams[idx] if idx < len(diagrams) else ""
        for idx in range(10):
            d[pool_lego.get_safe_col_name(f"Hình Hẻm {idx+1}")] = alleys[idx] if idx < len(alleys) else ""
        for idx in range(25):
            d[pool_lego.get_safe_col_name(f"Ảnh {idx+1}")] = interiors[idx] if idx < len(interiors) else ""
            
        # Build mảng giá trị 79 cột tương ứng POOL_HEADERS
        row_values = []
        for header in pool_lego.POOL_HEADERS:
            safe_col = pool_lego.get_safe_col_name(header)
            val = d.get(safe_col, "")
            
            if header == "Mã Hàng":
                parts = tk_id.split('-')
                val = f"TK-{parts[-1].upper()}" if parts else tk_id
            elif header == "Hình Nhận Diện":
                val = ""
            elif header == "Mã Khang Ngô (ID)" and not val:
                val = pool_lego.gen_id_khang_ngo_python(d.get("Ngo_So_nha", ""), d.get("Duong", ""), d.get("Quan", ""))
            elif header == "System ID" and not val:
                val = d.get("System_ID", "")
            elif header == "Last Sync":
                val = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                
            val_str = str(val) if val is not None else ""
            val_str = pool_lego.clean_sheet_formula_prefix(val_str)
            row_values.append(val_str)
            
        rows_data_to_append.append(row_values)
        
    conn.close()
    
    if not rows_data_to_append:
        return
        
    # 2. Kết nối Google Sheets và Append hàng loạt
    try:
        creds = manager.get_google_credentials()
        sheet_id = cfg.get("staging_pool_sheet_id") if os.environ.get("STAGING") == "true" else cfg.get("sheet_id")
        
        import gspread
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.worksheet("Pool")
        
        print(f"  - [Sheets] Đang chèn append hàng loạt {len(rows_data_to_append)} dòng lên tab 'Pool'...")
        sheet.append_rows(rows_data_to_append, value_input_option='USER_ENTERED')
        print(f"  - [Sheets] Đã đồng bộ hàng loạt thành công {len(rows_data_to_append)} căn lên Sheets.")
        
        # 2b. Đồng bộ hình ảnh lên tab Pool_Images làm backup
        print("  - [Sheets] Đang đồng bộ danh sách hình ảnh lên tab 'Pool_Images'...")
        conn_check = sqlite3.connect(db_file)
        conn_check.row_factory = sqlite3.Row
        cursor_check = conn_check.cursor()
        for tk_id in tk_ids:
            try:
                row_check = cursor_check.execute("SELECT raw_images_tk_json, Ngo_So_nha, Duong, Phuong, Quan FROM listings WHERE tk_id = ?", (tk_id,)).fetchone()
                if row_check:
                    d_check = dict(row_check)
                    raw_imgs = []
                    media_json = d_check.get("raw_images_tk_json")
                    if media_json:
                        raw_imgs = json.loads(media_json)
                    address_str = f"{d_check.get('Ngo_So_nha', '')} {d_check.get('Duong', '')}, {d_check.get('Phuong', '')}, {d_check.get('Quan', '')}"
                    
                    pool_lego.init_pool_images_rows(spreadsheet, tk_id, address_str, raw_imgs)
                    pool_lego.update_pool_images_crawl_row(spreadsheet, tk_id, address_str, raw_imgs)
            except Exception as e_img_backup:
                print(f"    [⚠️ WARNING] Không thể backup ảnh lên Pool_Images cho {tk_id}: {str(e_img_backup)}")
        conn_check.close()
        
        # 3. Đồng bộ trạng thái SQLite thành 'published'
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        for tk_id in tk_ids:
            cursor.execute("UPDATE listings SET status = 'published' WHERE tk_id = ?", (tk_id,))
        conn.commit()
        conn.close()
        print("  - [SQLite] Đã đồng bộ cập nhật trạng thái 'published' cho các căn vừa batch sync.")
        
    except Exception as e:
        print(f"[-] LỖI: Đồng bộ hàng loạt lên Sheets thất bại: {str(e)}")

def run_rebuild(limit):
    print(f"[+] KHỞI ĐỘNG TIẾN TRÌNH CÀO REBUILD (LIMIT = {limit})...")
    
    # 1. Đọc tệp kiểm soát JSON
    if not os.path.exists(JSON_CONTROL_FILE):
        print(f"[-] LỖI: Không tìm thấy tệp kiểm soát {JSON_CONTROL_FILE}. Vui lòng chạy chế độ --prepare trước.")
        sys.exit(1)
        
    with open(JSON_CONTROL_FILE, "r", encoding="utf-8") as f:
        control_list = json.load(f)
        
    pending_items = [item for item in control_list if item["status"] == "pending"]
    print(f"  - [Kiểm soát] Phát hiện {len(pending_items)}/{len(control_list)} căn ở trạng thái 'pending'.")
    
    if not pending_items:
        print("[✅] Tuyệt vời! Không còn căn nào ở trạng thái 'pending'. Rebuild hoàn tất!")
        return

    # 2. Kiểm tra & Active Refresh Cookie
    refreshed_cookie = check_and_active_refresh_cookie(manager.COOKIE_FILE)
    cookie = refreshed_cookie or ""
    if not cookie and os.path.exists(manager.COOKIE_FILE):
        try:
            with open(manager.COOKIE_FILE, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
        except Exception:
            pass
            
    if not cookie:
        print("[-] LỖI: Không tìm thấy Cookie Thiên Khôi. Vui lòng cập nhật Cookie qua Web UI.")
        sys.exit(1)

    # 3. Trích xuất token
    access_token, _, _ = fetcher.extract_tokens(cookie)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://proptech.thienkhoi.com",
        "Referer": "https://proptech.thienkhoi.com/"
    }

    processed_count = 0
    successfully_crawled_ids = []
    
    # Chạy vòng lặp cào từng căn
    for item in pending_items:
        if processed_count >= limit:
            print(f"[i] Đã đạt giới hạn {limit} căn cho mẻ chạy này. Dừng lại.")
            break
            
        tk_id = item["tk_id"]
        print(f"\n📦 [{processed_count+1}/{limit}] Đang xử lý căn: {tk_id}...")
        
        # [🔑 Auth] Kiểm tra thời hạn token trước mỗi lượt cào (Active Refresh Guardrail)
        refreshed_cookie = check_and_active_refresh_cookie(manager.COOKIE_FILE)
        if refreshed_cookie:
            cookie = refreshed_cookie
            _, access_token, _ = fetcher.extract_tokens(cookie)
            headers["Authorization"] = f"Bearer {access_token}"
            
        detail_api_url = f"https://backend.thienkhoi.com/product/v1/property/{tk_id}"
        
        # Gọi API Thiên Khôi
        r = requests.get(detail_api_url, headers=headers, timeout=20)
        
        # Nếu token hết hạn -> thử refresh bị động làm fallback
        if r.status_code in [401, 403]:
            print("  - [🔑 Auth] Access Token hết hạn. Đang thử làm mới token...")
            refreshed_cookie = fetcher.try_refresh_tokens(manager.COOKIE_FILE)
            if refreshed_cookie:
                cookie = refreshed_cookie
                _, access_token, _ = fetcher.extract_tokens(cookie)
                headers["Authorization"] = f"Bearer {access_token}"
                r = requests.get(detail_api_url, headers=headers, timeout=20)
            else:
                print("[-] LỖI: Cookie đã hết hạn hoàn toàn và không thể tự refresh. Vui lòng cập nhật Cookie trên Web UI.")
                break
                
        if r.status_code in [400, 404]:
            print(f"  - [🚨 Tránh] Căn nhà {tk_id} đã bị xóa hoặc khóa trên Thiên Khôi (Mã lỗi {r.status_code}). Bỏ qua.")
            item["status"] = f"skipped_error_{r.status_code}"
            # Ghi nhận log lỗi chi tiết phục vụ rà soát
            log_error_report(tk_id, r.status_code, "deleted_or_locked")
            
            with open(JSON_CONTROL_FILE, "w", encoding="utf-8") as f:
                json.dump(control_list, f, indent=4, ensure_ascii=False)
            continue
        elif r.status_code != 200:
            print(f"[-] LỖI: API Thiên Khôi phản hồi mã lỗi {r.status_code}. Dừng mẻ chạy.")
            log_error_report(tk_id, r.status_code, "http_error")
            break
            
        detail_json = r.json()
        detail_data = detail_json.get("data") or {}
        if not detail_data:
            print("[-] LỖI: Phản hồi API trống. Bỏ qua.")
            log_error_report(tk_id, 200, "empty_response_data")
            continue

        # Parse thông tin thô để lưu
        ma_hang = detail_data.get("code") or tk_id
        tinh = (detail_data.get("district") or {}).get("provinceName", "TP Hồ Chí Minh")
        quan_name = (detail_data.get("district") or {}).get("name", "")
        phuong_name = (detail_data.get("ward") or {}).get("name", "")
        duong_name = (detail_data.get("street") or {}).get("name") if detail_data.get("street") else detail_data.get("streetName", "")
        ngo_so_nha = detail_data.get("address", "")
        
        phan_loai_names = [c.get("name") for c in (detail_data.get("criteria") or []) if c and c.get("name")]
        phan_loai = ", ".join(phan_loai_names)
        
        # Dựng title thô
        dt_so = str(detail_data.get("area") or "").strip()
        dt_thuc = str(detail_data.get("actualArea") or "").strip()
        area_str = f"{dt_so}/{dt_thuc}" if (dt_so and dt_thuc and dt_so != dt_thuc) else (dt_so or dt_thuc)
        
        floors_val = str(detail_data.get("floors") or "").strip()
        wide_val = str(detail_data.get("wide") or "").strip()
        depth_val = str(detail_data.get("depth") or "").strip()
        price_val = str(detail_data.get("offeringPrice") or "").strip()
        
        parts = [ngo_so_nha, duong_name, area_str, floors_val, wide_val, depth_val]
        if price_val:
            parts.append(f"{price_val} tỷ")
        noi_dung_chinh = " ".join([str(p).strip() for p in parts if p])
        
        media = detail_data.get("media", [])
        property_images = [m.get("url") for m in media if m.get("url") and m.get("type") not in ["parcel_map", "certificate_image"]]
        sodo_images = [m.get("url") for m in media if m.get("url") and m.get("type") in ["parcel_map", "certificate_image"]]
        raw_images_tk_ordered = [m.get("url") for m in media if m.get("url")]
        
        channels_list = detail_data.get("channels") or []
        channels_str = ", ".join([str(c) for c in channels_list if c])
        tags_list = detail_data.get("tags") or []
        tags_str = ", ".join([t.get("name") if isinstance(t, dict) else str(t) for t in tags_list if t])
        
        # Dựng crawled_data
        crawled_data = {
            "raw_images_tk_ordered": raw_images_tk_ordered,
            "Mã Hàng": ma_hang,
            "Tỉnh": tinh,
            "Quận": quan_name,
            "Phường": phuong_name,
            "Đường": duong_name,
            "Ngõ/Số nhà": ngo_so_nha,
            "Phân loại": phan_loai,
            "Nội dung chính": noi_dung_chinh,
            "Mô tả chi tiết": detail_data.get("description", ""),
            "Giá chào": price_val,
            "Giá Public": price_val,
            "DT Thực tế": dt_thuc,
            "DT Trên sổ": dt_so,
            "Số Tầng": floors_val,
            "Mặt Tiền": wide_val,
            "Chieu_dai": depth_val,
            "Số phòng ngủ": str(detail_data.get("bedrooms") or ""),
            "Số nhà vệ sinh": str(detail_data.get("restrooms") or ""),
            "Đường trước nhà (m)": str(detail_data.get("minimumRoadWidth") or ""),
            "Trạng thái": detail_data.get("status", ""),
            "Tên Chủ Nhà": ", ".join([o.get("name") for o in (detail_data.get("homeOwner") or []) if o and o.get("name")]),
            "Điện thoại 1": detail_data.get("contactPhoneNumber", ""),
            "Điện thoại Đầu Chủ": (detail_data.get("ownerSideUser") or {}).get("phone", ""),
            "Tên Đầu Chủ (Hợp đồng)": (detail_data.get("ownerSideUser") or {}).get("name", ""),
            "Ten_Dau_Chu": (detail_data.get("ownerSideUser") or {}).get("name", ""),
            "Điểm Facebook": (detail_data.get("ownerSideUser") or {}).get("fbLink", ""),
            "Link Gốc": f"https://proptech.thienkhoi.com/warehouse/sources/{tk_id}",
            "System ID": f"SYS-{datetime.now().strftime('%Y%m%d').upper()}-{random.randint(100, 999)}",
            "Mã Khang Ngô (ID)": pool_lego.gen_id_khang_ngo_python(ngo_so_nha, duong_name, quan_name),
            "Last Crawl": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "raw_json_full": json.dumps(detail_data, ensure_ascii=False)
        }
        
        # [US-152] Lọc sạch tiền tố công thức (+, -, =, *) của mọi trường text trước khi lưu SQLite
        for k, v in crawled_data.items():
            if isinstance(v, str) and k != "raw_json_full" and k != "JSON_UI":
                crawled_data[k] = pool_lego.clean_sheet_formula_prefix(v)
        
        for idx, url in enumerate(sodo_images[:5]):
            crawled_data[f"Sơ đồ thửa đất {idx+1}"] = url
            
        criteria_list = detail_data.get("criteria") or []
        criteria_cols = fetcher.parse_criteria_groups(criteria_list)
        crawled_data.update(criteria_cols)
        crawled_data["JSON_UI"] = json.dumps(pool_lego.extract_json_ui_data(detail_data), ensure_ascii=False)
        
        # 4. Lưu thô vào SQLite Production
        fetcher.save_raw_to_sqlite(tk_id, crawled_data, property_images)
        print("  - [SQLite] Đã lưu thô thành công.")
        
        # 5. Di cư ảnh R2 v3 (đồng bộ, bỏ qua auto-sheets lẻ tẻ để ghi batch tối ưu)
        print("  - [R2 v3] Đang tải ảnh, nén ảnh và di cư sang R2 v3...")
        manager.run_image_migration_thread(limit=1, cookie=cookie, target_tk_id=tk_id, skip_sheets_publish=True)
        
        successfully_crawled_ids.append(tk_id)
        item["status"] = "crawled_waiting_sync"
        
        # Ghi nhận checkpoint SQLite thành công tạm thời
        with open(JSON_CONTROL_FILE, "w", encoding="utf-8") as f:
            json.dump(control_list, f, indent=4, ensure_ascii=False)
            
        processed_count += 1
        
        # Nghỉ ngẫu nhiên từ 3 đến 6 giây để chống rate limit Thiên Khôi
        delay = random.uniform(3.0, 6.0)
        print(f"  - [Delay] Nghỉ {delay:.2f} giây...")
        time.sleep(delay)

    # 6. Đồng bộ hàng loạt lên Sheets bằng Batch Append sau khi hoàn thành mẻ (Tối ưu hóa cào mẻ lớn)
    if successfully_crawled_ids:
        batch_publish_to_sheets(successfully_crawled_ids)
        # Cập nhật trạng thái completed chính thức cho các căn đã sync thành công
        for item in control_list:
            if item["tk_id"] in successfully_crawled_ids:
                item["status"] = "completed"
        with open(JSON_CONTROL_FILE, "w", encoding="utf-8") as f:
            json.dump(control_list, f, indent=4, ensure_ascii=False)

    print(f"\n[✅] ĐÃ HOÀN THÀNH MẺ CHẠY! Đã cào và xử lý thành công {processed_count} căn.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script cứu hộ tái thiết dữ liệu Production BDS KhangNgo (US-152)")
    parser.add_argument("--prepare", action="store_true", help="Chạy chế độ chuẩn bị CSDL và tệp kiểm soát JSON")
    parser.add_argument("--run", action="store_true", help="Chạy tiến trình cào và rebuild dữ liệu")
    parser.add_argument("--limit", type=int, default=1, help="Giới hạn số lượng căn cần xử lý trong mẻ chạy (mặc định: 1)")
    
    args = parser.parse_args()
    
    if args.prepare:
        prepare_rebuild()
    elif args.run:
        run_rebuild(args.limit)
    else:
        parser.print_help()
