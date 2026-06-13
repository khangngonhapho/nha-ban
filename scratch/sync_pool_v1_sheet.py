import sys
import os
import sqlite3
import gspread
import time
import datetime
import hmac
import hashlib
import requests
from urllib.parse import urlparse

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
import manager

# Load R2 credentials
import json
config_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/settings.json"
with open(config_file, 'r', encoding='utf-8') as f:
    cfg = json.load(f)

r2_access_key = cfg.get("r2_access_key_id")
r2_secret_key = cfg.get("r2_secret_access_key")
r2_bucket = cfg.get("r2_bucket_name")
account_id = cfg.get("cloudflare_account_id")
r2_public_url = cfg.get("r2_public_url")

def upload_image_to_r2(file_content, filename, content_type="image/jpeg"):
    host = f"{r2_bucket}.{account_id}.r2.cloudflarestorage.com"
    key = f"BDS-KhangNgo/{filename}"
    path = f"/{key}"
    
    t = datetime.datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = t.strftime('%Y%m%d')
    
    hashed_payload = hashlib.sha256(file_content).hexdigest()
    canonical_headers = f"host:{host}\nx-amz-content-sha256:{hashed_payload}\nx-amz-date:{amz_date}\n"
    signed_headers = "host;x-amz-content-sha256;x-amz-date"
    
    canonical_request = f"PUT\n{path}\n\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    algorithm = "AWS4-HMAC-SHA256"
    region = "auto"
    service = "s3"
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    
    string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashed_canonical_request}"
    
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
        
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = hmac.new(("AWS4" + key).encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = sign(k_date, region_name)
        k_service = sign(k_region, service_name)
        k_signing = sign(k_service, "aws4_request")
        return k_signing
        
    signing_key = get_signature_key(r2_secret_key, date_stamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    authorization_header = f"{algorithm} Credential={r2_access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
    
    url = f"https://{host}{path}"
    headers = {
        'Host': host,
        'Authorization': authorization_header,
        'x-amz-date': amz_date,
        'x-amz-content-sha256': hashed_payload,
        'Content-Type': content_type
    }
    
    r = requests.put(url, data=file_content, headers=headers, timeout=30)
    if r.status_code != 200:
        raise Exception(f"R2 PUT failed with status {r.status_code}: {r.text}")
        
    return f"{r2_public_url}/BDS-KhangNgo/{filename}"

def extract_cloudinary_filename_and_tk_id(url):
    parsed = urlparse(url)
    path = parsed.path
    parts = path.split('/')
    
    filename = parts[-1]
    tk_id = ""
    if "BDS-KhangNgo" in parts:
        idx = parts.index("BDS-KhangNgo")
        if idx + 2 < len(parts):
            tk_id = parts[idx+1]
    return filename, tk_id

def main():
    creds = manager.get_google_credentials()
    if not creds:
        print("[❌ LỖI] Không thể load Google Credentials.")
        return
        
    client = gspread.authorize(creds)
    sheet_id = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
    db_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
    
    print("[⚡] Kết nối SQLite và tải dữ liệu R2...")
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    db_rows = cursor.execute("SELECT * FROM listings").fetchall()
    conn.close()
    
    # Map database records
    db_by_tk_id = {}
    db_by_sys_id = {}
    db_by_ma_hang = {}
    db_by_ma_kn = {}
    
    for r in db_rows:
        d = dict(r)
        tk_id = d.get("tk_id")
        sys_id = d.get("System_ID")
        ma_hang = d.get("Ma_Hang")
        ma_kn = d.get("Ma_Khang_Ngo_ID")
        
        if tk_id:
            db_by_tk_id[tk_id.strip()] = d
        if sys_id:
            db_by_sys_id[sys_id.strip()] = d
        if ma_hang:
            db_by_ma_hang[ma_hang.strip()] = d
        if ma_kn:
            db_by_ma_kn[ma_kn.strip()] = d
            
    print(f"[✅] Đã tải {len(db_rows)} bản ghi từ SQLite.")
    
    # 2. Open Google Sheets
    print(f"[⚡] Đang mở Google Sheet Pool (v1) [ID: {sheet_id}]...")
    try:
        ss = client.open_by_key(sheet_id)
        sheet = ss.worksheet("Pool")
        print("[⚡] Đang tải toàn bộ dữ liệu từ Google Sheets (get_all_values)...")
        all_rows = sheet.get_all_values()
        print(f"[✅] Đã tải thành công {len(all_rows)} dòng.")
    except Exception as e:
        print(f"[❌ LỖI] Không thể đọc dữ liệu từ Google Sheets: {e}")
        return
        
    # Column mapping from Sheet (0-indexed) to DB column name
    col_map = {
        1: "Hinh_Nhan_Dien",         # Col 2
        27: "So_do_thua_dat_1",      # Col 28
        28: "So_do_thua_dat_2",      # Col 29
        29: "Hinh_Mat_Tien",         # Col 30
        30: "Hinh_Hem_1",            # Col 31
        31: "Hinh_Hem_2",
        32: "Hinh_Hem_3",
        33: "Hinh_Hem_4",
        34: "Hinh_Hem_5",
        35: "Hinh_Hem_6",
        36: "Hinh_Hem_7",
        37: "Hinh_Hem_8",
        38: "Hinh_Hem_9",
        39: "Hinh_Hem_10",           # Col 40
        40: "Anh_1",                 # Col 41
        41: "Anh_2",
        42: "Anh_3",
        43: "Anh_4",
        44: "Anh_5",
        45: "Anh_6",
        46: "Anh_7",
        47: "Anh_8",
        48: "Anh_9",
        49: "Anh_10",
        50: "Anh_11",
        51: "Anh_12",
        52: "Anh_13",
        53: "Anh_14",
        54: "Anh_15",                # Col 55
        80: "So_do_thua_dat_3",      # Col 81
        81: "So_do_thua_dat_4",      # Col 82
        82: "So_do_thua_dat_5",      # Col 83
        83: "Anh_16",                # Col 84
        84: "Anh_17",
        85: "Anh_18",
        86: "Anh_19",
        87: "Anh_20",
        88: "Anh_21",
        89: "Anh_22",
        90: "Anh_23",
        91: "Anh_24",
        92: "Anh_25"                 # Col 93
    }
    
    cells_to_update = []
    direct_migrate_count = 0
    direct_migrate_success = 0
    direct_migrate_fail = 0
    db_match_count = 0
    no_match_count = 0
    
    print("[⚡] Bắt đầu quét so khớp từng dòng...")
    
    # Data rows start at index 1 (row 2)
    for r_idx, row in enumerate(all_rows[1:], start=2):
        if len(row) < 74:
            continue
            
        ma_hang = row[0].strip()
        ma_kn = row[55].strip()
        sys_id = row[72].strip()
        link_goc = row[73].strip()
        
        # Extract tk_id from Link Gốc
        tk_id = ""
        if link_goc:
            parts = link_goc.split('/')
            if len(parts) > 0:
                tk_id = parts[-1].strip()
                
        # Find DB record
        db_record = None
        if tk_id and tk_id in db_by_tk_id:
            db_record = db_by_tk_id[tk_id]
        elif sys_id and sys_id in db_by_sys_id:
            db_record = db_by_sys_id[sys_id]
        elif ma_kn and ma_kn in db_by_ma_kn:
            db_record = db_by_ma_kn[ma_kn]
        elif ma_hang and ma_hang in db_by_ma_hang:
            db_record = db_by_ma_hang[ma_hang]
            
        if db_record:
            db_match_count += 1
            # Gather all R2 values and Cloudinary values from DB for this record (properly parsing JSON lists)
            db_r2_values = []
            db_cld_values = []
            for val in db_record.values():
                if not val:
                    continue
                val_str = str(val).strip()
                if val_str.startswith("[") and val_str.endswith("]"):
                    try:
                        urls = json.loads(val_str)
                        for u in urls:
                            u_str = str(u).strip()
                            if "r2.dev" in u_str:
                                db_r2_values.append(u_str)
                            elif "cloudinary.com" in u_str:
                                db_cld_values.append(u_str)
                    except Exception:
                        pass
                else:
                    if "r2.dev" in val_str:
                        db_r2_values.append(val_str)
                    elif "cloudinary.com" in val_str:
                        db_cld_values.append(val_str)
            
            # Check mapped image columns
            for sheet_col_idx, db_col_name in col_map.items():
                if sheet_col_idx >= len(row):
                    continue
                sheet_val = row[sheet_col_idx].strip()
                db_val = db_record.get(db_col_name)
                
                # Normalize sheet_val if it is a JSON list string
                is_sheet_json = sheet_val.startswith("[") and sheet_val.endswith("]")
                sheet_urls = []
                if is_sheet_json:
                    try:
                        sheet_urls = json.loads(sheet_val)
                    except Exception:
                        pass
                
                # Extract first URL from sheet if it was a JSON list
                first_sheet_url = sheet_urls[0].strip() if sheet_urls else sheet_val
                
                # Case 1: Database already has a single R2 URL for this column
                if db_val and "r2.dev" in db_val and not (db_val.startswith("[") and db_val.endswith("]")):
                    # Overwrite sheet cell if it is different (e.g. JSON list, Cloudinary, or empty)
                    if sheet_val != db_val:
                        cells_to_update.append(gspread.Cell(r_idx, sheet_col_idx + 1, db_val))
                    continue
                
                # Case 2: Database does NOT have an R2 URL for this column (it's empty or Cloudinary)
                if first_sheet_url and "cloudinary.com" in first_sheet_url:
                    filename, folder_tk_id = extract_cloudinary_filename_and_tk_id(first_sheet_url)
                    file_base = filename.rsplit('.', 1)[0] if '.' in filename else filename
                    
                    # 1. Search in all DB R2 values
                    found_r2 = None
                    for r2_val in db_r2_values:
                        if file_base in r2_val:
                            found_r2 = r2_val
                            break
                            
                    if found_r2:
                        cells_to_update.append(gspread.Cell(r_idx, sheet_col_idx + 1, found_r2))
                        
                        # Sync back to SQLite for this specific column
                        if not db_val or "r2.dev" not in db_val:
                            try:
                                conn_local = sqlite3.connect(db_file, timeout=30.0)
                                c_local = conn_local.cursor()
                                c_local.execute("PRAGMA journal_mode=WAL")
                                c_local.execute("PRAGMA synchronous=OFF")
                                rec_tk_id = db_record.get("tk_id")
                                if rec_tk_id:
                                    c_local.execute(f"UPDATE listings SET `{db_col_name}` = ? WHERE tk_id = ?", (found_r2, rec_tk_id))
                                    conn_local.commit()
                                conn_local.close()
                            except Exception as e_db:
                                print(f"     [⚠️ Warning] Không thể cập nhật SQLite: {e_db}")
                                sys.stdout.flush()
                        continue
                        
                    # 2. Search in all DB Cloudinary values (known 404s)
                    found_cld = False
                    for cld_val in db_cld_values:
                        if file_base in cld_val:
                            found_cld = True
                            break
                            
                    if found_cld:
                        if is_sheet_json:
                            cells_to_update.append(gspread.Cell(r_idx, sheet_col_idx + 1, first_sheet_url))
                        continue
                        
                    # 3. Direct migration
                    direct_migrate_count += 1
                    r2_filename = f"{folder_tk_id}_{filename}" if folder_tk_id else filename
                    try:
                        res_img = requests.get(first_sheet_url, timeout=10)
                        if res_img.status_code == 200:
                            r2_url = upload_image_to_r2(res_img.content, r2_filename)
                            cells_to_update.append(gspread.Cell(r_idx, sheet_col_idx + 1, r2_url))
                            direct_migrate_success += 1
                            
                            # Update SQLite database
                            try:
                                conn_local = sqlite3.connect(db_file, timeout=30.0)
                                c_local = conn_local.cursor()
                                c_local.execute("PRAGMA journal_mode=WAL")
                                c_local.execute("PRAGMA synchronous=OFF")
                                
                                rec_tk_id = db_record.get("tk_id")
                                if rec_tk_id:
                                    c_local.execute(f"UPDATE listings SET `{db_col_name}` = ? WHERE tk_id = ?", (r2_url, rec_tk_id))
                                    conn_local.commit()
                                conn_local.close()
                            except Exception as e_db:
                                print(f"     [⚠️ Warning] Không thể cập nhật SQLite: {e_db}")
                                sys.stdout.flush()
                        else:
                            direct_migrate_fail += 1
                            if is_sheet_json:
                                cells_to_update.append(gspread.Cell(r_idx, sheet_col_idx + 1, first_sheet_url))
                    except Exception:
                        direct_migrate_fail += 1
                        if is_sheet_json:
                            cells_to_update.append(gspread.Cell(r_idx, sheet_col_idx + 1, first_sheet_url))
                
                # Case 3: The sheet cell has a JSON list of R2 URLs, but the database is empty or Cloudinary
                elif first_sheet_url and "r2.dev" in first_sheet_url:
                    if is_sheet_json:
                        cells_to_update.append(gspread.Cell(r_idx, sheet_col_idx + 1, first_sheet_url))
                    
                    # Update SQLite database
                    if not db_val or "r2.dev" not in db_val:
                        try:
                            conn_local = sqlite3.connect(db_file, timeout=30.0)
                            c_local = conn_local.cursor()
                            c_local.execute("PRAGMA journal_mode=WAL")
                            c_local.execute("PRAGMA synchronous=OFF")
                            rec_tk_id = db_record.get("tk_id")
                            if rec_tk_id:
                                c_local.execute(f"UPDATE listings SET `{db_col_name}` = ? WHERE tk_id = ?", (first_sheet_url, rec_tk_id))
                                conn_local.commit()
                            conn_local.close()
                        except Exception as e_db:
                            print(f"     [⚠️ Warning] Không thể cập nhật SQLite: {e_db}")
                            sys.stdout.flush()
        else:
            no_match_count += 1
            # Direct migration for unmatched row
            for sheet_col_idx in col_map.keys():
                if sheet_col_idx >= len(row):
                    continue
                sheet_val = row[sheet_col_idx].strip()
                
                is_sheet_json = sheet_val.startswith("[") and sheet_val.endswith("]")
                sheet_urls = []
                if is_sheet_json:
                    try:
                        sheet_urls = json.loads(sheet_val)
                    except Exception:
                        pass
                first_sheet_url = sheet_urls[0].strip() if sheet_urls else sheet_val
                
                if first_sheet_url and "cloudinary.com" in first_sheet_url:
                    direct_migrate_count += 1
                    filename, folder_tk_id = extract_cloudinary_filename_and_tk_id(first_sheet_url)
                    r2_filename = f"{folder_tk_id}_{filename}" if folder_tk_id else filename
                    try:
                        res_img = requests.get(first_sheet_url, timeout=10)
                        if res_img.status_code == 200:
                            r2_url = upload_image_to_r2(res_img.content, r2_filename)
                            cells_to_update.append(gspread.Cell(r_idx, sheet_col_idx + 1, r2_url))
                            direct_migrate_success += 1
                        else:
                            direct_migrate_fail += 1
                            if is_sheet_json:
                                cells_to_update.append(gspread.Cell(r_idx, sheet_col_idx + 1, first_sheet_url))
                    except Exception:
                        direct_migrate_fail += 1
                        if is_sheet_json:
                            cells_to_update.append(gspread.Cell(r_idx, sheet_col_idx + 1, first_sheet_url))
                elif first_sheet_url and "r2.dev" in first_sheet_url:
                    if is_sheet_json:
                        cells_to_update.append(gspread.Cell(r_idx, sheet_col_idx + 1, first_sheet_url))
                        
        if r_idx % 1000 == 0:
            print(f"  - Đã quét xong {r_idx} dòng...")
            sys.stdout.flush()
            
    print(f"\n[📊] Kết quả quét so sánh tổng quát:")
    print(f"  - Số dòng khớp SQLite: {db_match_count}")
    print(f"  - Số dòng không khớp SQLite: {no_match_count}")
    print(f"  - Số ảnh phải di cư trực tiếp: {direct_migrate_count}")
    print(f"  - Di cư trực tiếp thành công: {direct_migrate_success}")
    print(f"  - Di cư trực tiếp thất bại (404/Lỗi): {direct_migrate_fail}")
    print(f"  - Tổng số ô ảnh sẽ được cập nhật R2 lên Google Sheet: {len(cells_to_update)}")
    sys.stdout.flush()
    
    if not cells_to_update:
        print("[✅] Không có ô nào cần cập nhật.")
        sys.stdout.flush()
        return
        
    print(f"[⚡] Bắt đầu lưu hàng loạt {len(cells_to_update)} ô ảnh lên Google Sheets...")
    sys.stdout.flush()
    
    # Save in chunks of 1000 cells (very fast)
    chunk_size = 1000
    for i in range(0, len(cells_to_update), chunk_size):
        chunk = cells_to_update[i:i + chunk_size]
        print(f"  -> Đang đẩy batch {i // chunk_size + 1} ({len(chunk)} ô)...")
        sys.stdout.flush()
        try:
            sheet.update_cells(chunk, value_input_option='USER_ENTERED')
            print("     [✅] Đã hoàn thành batch.")
            sys.stdout.flush()
            time.sleep(2)
        except Exception as e:
            print(f"     [❌ LỖI] Ghi batch thất bại: {e}")
            sys.stdout.flush()
            
    print("\n[🏁 HOÀN TẤT] Đồng bộ ảnh R2 lên sheet Pool (v1) hoàn tất!")
    sys.stdout.flush()

if __name__ == '__main__':
    main()
