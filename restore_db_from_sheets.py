import os
import sys
import json
import sqlite3
import time
from datetime import datetime

# Đảm bảo import được các hàm và cấu hình từ manager.py và pool_lego.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from manager import (
    load_config, get_google_credentials, DB_FILE, get_safe_col_name
)
from pool_lego import init_db, POOL_HEADERS

# Cho phép chỉ định database đích qua tham số dòng lệnh (vd: python restore_db_from_sheets.py --db=custom_test.db)
for arg in sys.argv:
    if arg.startswith("--db="):
        DB_FILE = arg.split("=", 1)[1]
        print(f"[ℹ] Chỉ định ghi đè CSDL đích: {DB_FILE}")

LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.lock")

class DBLock:
    def __init__(self, lock_path=LOCK_FILE):
        self.lock_path = lock_path
        self.fd = None

    def acquire(self, timeout=120):
        start = time.time()
        while True:
            try:
                self.fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return True
            except FileExistsError:
                try:
                    mtime = os.path.getmtime(self.lock_path)
                    if time.time() - mtime > 300:
                        try:
                            os.remove(self.lock_path)
                            print("[🛡️ Guard] Phát hiện và giải phóng file lock bị kẹt của phiên cũ.")
                        except Exception:
                            pass
                        continue
                except Exception:
                    pass
                if time.time() - start > timeout:
                    raise TimeoutError(f"Không thể lấy khóa ghi database sau {timeout} giây.")
                time.sleep(0.5)

    def release(self):
        if self.fd is not None:
            try:
                os.close(self.fd)
            except Exception:
                pass
            try:
                os.remove(self.lock_path)
            except Exception:
                pass
            self.fd = None

def with_db_lock(func):
    def wrapper(*args, **kwargs):
        lock = DBLock()
        try:
            lock.acquire(timeout=120)
        except Exception as e_lock:
            print(f"[❌ LOCK ERROR] Không thể chạy {func.__name__} do trùng khóa DB: {str(e_lock)}")
            return
        try:
            return func(*args, **kwargs)
        finally:
            lock.release()
    return wrapper

def backup_master_database(master_db_path):
    """Sao lưu CSDL Gốc trước khi hợp nhất và xoay vòng lưu tối đa 10 ngày"""
    try:
        if not os.path.exists(master_db_path):
            return
        import shutil
        backup_dir = "d:/LHTBrain/BDS_Backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        db_basename = os.path.splitext(os.path.basename(master_db_path))[0]
        # Quét các bản backup tương ứng với CSDL này
        backups = sorted(
            [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.startswith(f"{db_basename}_backup_")],
            key=os.path.getmtime
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{db_basename}_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_name)
        
        shutil.copy2(master_db_path, backup_path)
        print(f"  - [Backup] Đã sao lưu CSDL Gốc thành công: {backup_name}")
        
        backups.append(backup_path)
        
        # Giữ tối đa 10 bản sao lưu
        while len(backups) > 10:
            try:
                os.remove(backups.pop(0))
            except Exception:
                pass
    except Exception as e:
        print(f"  - [⚠️ WARNING] Không thể sao lưu CSDL Gốc: {str(e)}")

def is_empty_config(val_str):
    if not val_str or val_str in ["[]", "{}"]:
        return True
    try:
        parsed = json.loads(val_str)
        if isinstance(parsed, dict) and "images" in parsed:
            return len(parsed["images"]) == 0
        if isinstance(parsed, list):
            return len(parsed) == 0
    except Exception:
        pass
    return False

def merge_temp_to_master(temp_db_path, master_db_path):
    print("\n[+] Đang hợp nhất dữ liệu từ CSDL Tạm vào CSDL Gốc...")
    if not os.path.exists(temp_db_path):
        print("[-] Không tìm thấy CSDL Tạm để hợp nhất.")
        return
        
    # Nếu CSDL Gốc chưa tồn tại (chưa bao giờ chạy), ta chỉ cần copy tệp temp sang master
    if not os.path.exists(master_db_path):
        import shutil
        shutil.copy2(temp_db_path, master_db_path)
        print("  - [Master] CSDL Gốc chưa tồn tại. Đã tạo mới CSDL Gốc bằng CSDL Tạm.")
        return

    # Kết nối CSDL Gốc
    conn = sqlite3.connect(master_db_path, timeout=60.0)
    cursor = conn.cursor()
    
    try:
        # ATTACH CSDL Tạm
        cursor.execute("ATTACH DATABASE ? AS temp_db", (temp_db_path,))
        
        # 1. Định nghĩa Whitelist các cột được phép hợp nhất từ CSDL Tạm vào CSDL Gốc
        whitelist_cols = [
            "Quan", "Phuong", "Ma_Khang_Ngo_ID", "Tieu_de_Public", "Mo_ta_Public", "Gia_Public",
            "Duong_truoc_nha_m", "Phan_loai_Hem", "Danh_gia_Admin", "Tinh_trang_nha",
            "So_phong_ngu", "So_nha_ve_sinh", "Phuong_cu_AI", "Ngu_tret_Admin", "CHDV_Admin",
            "Anh_Public_VD_1_3_5", "Anh_Hem_Public_VD_1_2",
            "status", "custom_huong", "custom_dt_thuc_te", "custom_dt_so",
            "curated_config_json", "Images_Admin_JSON", "images_public_json", "manual_images_json"
        ]
        
        cursor.execute("PRAGMA table_info(listings)")
        db_cols = {r[1] for r in cursor.fetchall()}
        
        # Đảm bảo cols chứa các cột whitelist tồn tại trong DB, và luôn có tk_id ở đầu để làm khóa
        cols = ["tk_id"] + [c for c in whitelist_cols if c in db_cols]
        
        # 2. Truy vấn dữ liệu từ temp_db.listings
        sql_select = f"SELECT {', '.join([f'`{c}`' for c in cols])} FROM temp_db.listings"
        temp_rows = cursor.execute(sql_select).fetchall()
        print(f"  - Đang hợp nhất {len(temp_rows)} căn từ CSDL Tạm vào CSDL Gốc...")
        
        # Tạo map cột để dễ truy xuất
        col_to_idx = {c: i for i, c in enumerate(cols)}
        
        inserted_count = 0
        updated_count = 0
        BATCH_SIZE = 100  # Commit mỗi 100 căn để giảm rủi ro mất dữ liệu khi crash
        
        for i, row in enumerate(temp_rows):
            tk_id = row[col_to_idx["tk_id"]]
            if not tk_id:
                continue
                
            # Lấy thông tin bản ghi hiện có trong Master
            existing = cursor.execute(
                "SELECT tk_id FROM listings WHERE tk_id = ?",
                (tk_id,)
            ).fetchone()
            
            if existing:
                # Bản ghi đã tồn tại -> CẬP NHẬT (UPDATE)
                update_parts = []
                update_vals = []
                
                for col in cols:
                    if col in ["id", "tk_id"]:
                        continue
                        
                    val = row[col_to_idx[col]]
                    
                    # [US-152] Chặn ghi đè giá trị rỗng từ CSDL Tạm lên CSDL Gốc cho tất cả các cột Whitelist
                    if val is None or str(val).strip() == "" or str(val).strip() == "[]" or is_empty_config(str(val)):
                        continue
                            
                    update_parts.append(f"`{col}` = ?")
                    update_vals.append(val)
                    
                # Chỉ thực thi UPDATE lên SQLite nếu có ít nhất 1 cột thực sự cần thay đổi
                if update_parts:
                    update_vals.append(tk_id)
                    update_sql = f"UPDATE listings SET {', '.join(update_parts)} WHERE tk_id = ?"
                    cursor.execute(update_sql, update_vals)
                    updated_count += 1
                
                # Cập nhật listings_images cho căn này
                temp_admin_val = row[col_to_idx.get("Images_Admin_JSON") or col_to_idx.get("images_admin_json") or 0]
                is_temp_admin_empty = not temp_admin_val or temp_admin_val == "[]"
                
                if not is_temp_admin_empty:
                    cursor.execute("DELETE FROM listings_images WHERE tk_id = ?", (tk_id,))
                    cursor.execute("""
                        INSERT INTO listings_images (tk_id, system_id, image_url, r2_url, role, sequence_index, origin, is_hidden)
                        SELECT tk_id, system_id, image_url, r2_url, role, sequence_index, origin, is_hidden
                        FROM temp_db.listings_images WHERE tk_id = ?
                    """, (tk_id,))
            else:
                # Bản ghi chưa tồn tại -> THÊM MỚI (INSERT)
                placeholders = ", ".join(["?"] * len(cols))
                insert_vals = [row[col_to_idx[col]] for col in cols]
                insert_sql = f"INSERT INTO listings ({', '.join([f'`{c}`' for c in cols])}) VALUES ({placeholders})"
                cursor.execute(insert_sql, insert_vals)
                inserted_count += 1
                
                # Sao chép listings_images từ CSDL Tạm cho căn mới
                cursor.execute("""
                    INSERT INTO listings_images (tk_id, system_id, image_url, r2_url, role, sequence_index, origin, is_hidden)
                    SELECT tk_id, system_id, image_url, r2_url, role, sequence_index, origin, is_hidden
                    FROM temp_db.listings_images WHERE tk_id = ?
                """, (tk_id,))
            
            # [ANTI-MALFORMED] Batch commit mỗi BATCH_SIZE căn để giảm kích thước WAL
            if (i + 1) % BATCH_SIZE == 0:
                conn.commit()
                print(f"  - [Batch Commit] Đã commit an toàn {i + 1}/{len(temp_rows)} căn...")
        
        # Commit phần còn lại của listings
        conn.commit()
                
        # 3. Soft Delete: Đánh dấu status = 'sheet_deleted' cho các căn có trong Master nhưng KHÔNG có trong Temp
        del_rows = cursor.execute("SELECT tk_id FROM listings WHERE tk_id NOT IN (SELECT tk_id FROM temp_db.listings)").fetchall()
        soft_deleted_count = 0
        for r in del_rows:
            del_tk_id = r[0]
            current_status_row = cursor.execute("SELECT status FROM listings WHERE tk_id = ?", (del_tk_id,)).fetchone()
            
            # [US-152] WHITELIST AN TOÀN: Chỉ những căn "published" (đã xuất bản Sheets) bị biến mất mới đổi sang sheet_deleted.
            # Tha bổng hoàn toàn các căn nháp mới cào (raw_text, raw_complete, processing...).
            if current_status_row and current_status_row[0] == "published":
                cursor.execute("UPDATE listings SET status = 'sheet_deleted' WHERE tk_id = ?", (del_tk_id,))
                soft_deleted_count += 1
                
        if soft_deleted_count > 0:
            print(f"  - [Soft Delete] Đã chuyển trạng thái sang 'sheet_deleted' cho {soft_deleted_count} căn bị xóa trên Sheets.")
        
        # 4. Hợp nhất các bảng quản lý liên kết, blacklist và customer profiles từ CSDL Tạm sang CSDL Gốc
        # Vì các bảng này không cần giữ vết lịch sử phức tạp như listings, ta chép trực tiếp từ temp_db sang
        cursor.execute("DELETE FROM shared_links")
        cursor.execute("INSERT INTO shared_links SELECT * FROM temp_db.shared_links")
        
        cursor.execute("DELETE FROM phone_blacklist")
        cursor.execute("INSERT INTO phone_blacklist SELECT * FROM temp_db.phone_blacklist")
        
        # Khởi tạo bảng customer_profiles trên master db nếu chưa có (phòng thủ)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_profiles (
            raw_phone TEXT,
            phone_hash TEXT PRIMARY KEY,
            name TEXT,
            note TEXT,
            lifecycle_status TEXT DEFAULT 'LẠNH',
            updated_at TEXT
        )
        """)
        cursor.execute("DELETE FROM customer_profiles")
        cursor.execute("INSERT INTO customer_profiles SELECT * FROM temp_db.customer_profiles")

        # Khởi tạo bảng exclusion_filters trên master db nếu chưa có (phòng thủ)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exclusion_filters (
            id TEXT PRIMARY KEY,
            field TEXT NOT NULL,
            operator TEXT NOT NULL,
            value TEXT,
            status TEXT NOT NULL DEFAULT 'Active',
            note TEXT
        )
        """)
        cursor.execute("DELETE FROM exclusion_filters")
        cursor.execute("INSERT INTO exclusion_filters SELECT * FROM temp_db.exclusion_filters")

        conn.commit()
        
        # DETACH CSDL Tạm
        cursor.execute("DETACH DATABASE temp_db")
        
        # [ANTI-MALFORMED] Ép WAL checkpoint: ghi toàn bộ WAL vào file DB chính và xóa sạch WAL file
        cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        
        print(f"  - [Hoàn tất hợp nhất] Đã hợp nhất listings, shared_links, phone_blacklist, customer_profiles và exclusion_filters vào CSDL Gốc.")
    except Exception as e_merge:
        # Rollback để tránh dữ liệu dở dang gây malformed
        try:
            conn.rollback()
        except Exception:
            pass
        print(f"  - [❌ LỖI NGHIÊM TRỌNG] Lỗi hợp nhất CSDL: {str(e_merge)}. Đã rollback an toàn.")
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass

def restore_links_and_blacklist(client, db_path):
    print(f"\n🔄 Đang đồng bộ bảng Links, Blacklist và Customer Profiles từ Tracking Log vào tệp CSDL Tạm: {db_path}...")
    TRACKING_SHEET_ID = "1zCAP0pUSZdVNxbEkVl94y_hJc1ShM4PqtB-fxpm_I5Y"
    try:
        spreadsheet = client.open_by_key(TRACKING_SHEET_ID)
        
        # 1. Đồng bộ Link_Registry
        try:
            link_sheet = spreadsheet.worksheet("Link_Registry")
            link_rows = link_sheet.get_all_values()
            if len(link_rows) > 1:
                conn = sqlite3.connect(db_path, timeout=30.0)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM shared_links")
                for r in link_rows[1:]:
                    if len(r) >= 8 and r[0]:
                        cursor.execute("""
                            INSERT OR REPLACE INTO shared_links (link_id, customer_name, customer_note, shared_house_ids, created_at, expires_at, bound_phone_hash, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
                conn.commit()
                conn.close()
                print(f"  - [Link Registry] Đã nạp {len(link_rows)-1} liên kết vào CSDL Tạm.")
        except Exception as e_link:
            print(f"  - [⚠️ WARNING Link Registry] Không thể đồng bộ: {str(e_link)}")

        # 2. Đồng bộ Phone_Blacklist
        try:
            blacklist_sheet = spreadsheet.worksheet("Phone_Blacklist")
            bl_rows = blacklist_sheet.get_all_values()
            if len(bl_rows) > 1:
                conn = sqlite3.connect(db_path, timeout=30.0)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM phone_blacklist")
                for r in bl_rows[1:]:
                    if len(r) >= 5 and r[1]:
                        cursor.execute("""
                            INSERT OR REPLACE INTO phone_blacklist (raw_phone, phone_hash, blocked_at, reason, status)
                            VALUES (?, ?, ?, ?, ?)
                        """, (r[0], r[1], r[2], r[3], r[4]))
                conn.commit()
                conn.close()
                print(f"  - [Phone Blacklist] Đã nạp {len(bl_rows)-1} số điện thoại chặn vào CSDL Tạm.")
        except Exception as e_bl:
            print(f"  - [⚠️ WARNING Phone Blacklist] Không thể đồng bộ: {str(e_bl)}")

        # 3. Đồng bộ Customer_Profiles (US-140)
        try:
            try:
                profile_sheet = spreadsheet.worksheet("Customer_Profiles")
            except Exception:
                profile_sheet = spreadsheet.add_worksheet(title="Customer_Profiles", rows=1000, cols=6)
                headers = ["Raw_Phone", "Phone_Hash", "Name", "Note", "Lifecycle_Status", "Updated_At"]
                profile_sheet.update(range_name='A1:F1', values=[headers])
            cp_rows = profile_sheet.get_all_values()
            if len(cp_rows) > 1:
                conn = sqlite3.connect(db_path, timeout=30.0)
                cursor = conn.cursor()
                # Khởi tạo bảng customer_profiles trên db tạm trước khi insert (phòng thủ)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS customer_profiles (
                    raw_phone TEXT,
                    phone_hash TEXT PRIMARY KEY,
                    name TEXT,
                    note TEXT,
                    lifecycle_status TEXT DEFAULT 'LẠNH',
                    updated_at TEXT
                )
                """)
                cursor.execute("DELETE FROM customer_profiles")
                for r in cp_rows[1:]:
                    if len(r) >= 6 and r[1]:
                        cursor.execute("""
                            INSERT OR REPLACE INTO customer_profiles (raw_phone, phone_hash, name, note, lifecycle_status, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (r[0], r[1], r[2], r[3], r[4], r[5]))
                conn.commit()
                conn.close()
                print(f"  - [Customer Profiles] Đã nạp {len(cp_rows)-1} hồ sơ khách hàng vào CSDL Tạm.")
            else:
                print("  - [Customer Profiles] Tab trống hoặc chỉ có tiêu đề. Không có dữ liệu khách hàng để nạp.")
        except Exception as e_cp:
            print(f"  - [⚠️ WARNING Customer Profiles] Không thể đồng bộ: {str(e_cp)}")

        # 4. Đồng bộ Exclusion_Filters (US-143)
        try:
            try:
                exclusions_sheet = spreadsheet.worksheet("Exclusion_Filters")
            except Exception:
                exclusions_sheet = spreadsheet.add_worksheet(title="Exclusion_Filters", rows=1000, cols=6)
                headers = ["ID", "Field", "Operator", "Value", "Status", "Note"]
                exclusions_sheet.update(range_name='A1:F1', values=[headers])
            ex_rows = exclusions_sheet.get_all_values()
            if len(ex_rows) > 1:
                conn = sqlite3.connect(db_path, timeout=30.0)
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS exclusion_filters (
                    id TEXT PRIMARY KEY,
                    field TEXT NOT NULL,
                    operator TEXT NOT NULL,
                    value TEXT,
                    status TEXT NOT NULL DEFAULT 'Active',
                    note TEXT
                )
                """)
                cursor.execute("DELETE FROM exclusion_filters")
                for r in ex_rows[1:]:
                    if len(r) >= 5 and r[0]:
                        cursor.execute("""
                            INSERT OR REPLACE INTO exclusion_filters (id, field, operator, value, status, note)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (r[0], r[1], r[2], r[3], r[4], r[5] if len(r) >= 6 else ''))
                conn.commit()
                conn.close()
                print(f"  - [Exclusion Filters] Đã nạp {len(ex_rows)-1} tiêu chí loại trừ vào CSDL Tạm.")
            else:
                print("  - [Exclusion Filters] Tab trống hoặc chỉ có tiêu đề. Không có tiêu chí loại trừ để nạp.")
        except Exception as e_ex:
            print(f"  - [⚠️ WARNING Exclusion Filters] Không thể đồng bộ: {str(e_ex)}")
            
    except Exception as e:
        print(f"  - [⚠️ WARNING Links Sync] Lỗi kết nối hoặc mở spreadsheet: {str(e)}")

def normalize_images_list(images_list):
    """Chuẩn hóa list ảnh để luôn có các key cần thiết (url, role, visible)
    và ánh xạ chính xác vai trò tiếng Anh sang tiếng Việt, cờ ẩn/hiện.
    """
    normalized_images = []
    if not images_list or not isinstance(images_list, list):
        return normalized_images
        
    for img in images_list:
        if not isinstance(img, dict):
            continue
        url = img.get("url") or img.get("r2_url") or img.get("image_url") or ""
        if not url:
            continue
        role = img.get("role") or "Nội thất"
        role_map_en_to_vi = {
            "diagram": "Sơ đồ", "facade": "Mặt tiền", "cover": "Bìa",
            "alley": "Hẻm", "interior": "Nội thất", "hidden": "Ẩn", "deleted": "deleted", "sodo": "Sơ đồ"
        }
        if role in role_map_en_to_vi:
            role = role_map_en_to_vi[role]
        
        is_hidden = img.get("is_hidden")
        visible = img.get("visible")
        if visible is None:
            if is_hidden is not None:
                visible = (is_hidden == 0)
            else:
                visible = True
        
        normalized_images.append({
            "url": url,
            "role": role,
            "visible": visible,
            "origin": img.get("origin")
        })
    return normalized_images

@with_db_lock
def restore_database(repair_sheets=False):
    print("======================================================================")
    print("🔄 BẮT ĐẦU KHÔI PHỤC DATABASE SQLITE CỤC BỘ TỪ GOOGLE SHEETS POOL")
    print("👉 Hợp nhất dọn dẹp đôn ảnh nhà thật chuẩn US-055!")
    print("======================================================================")
    
    # 1. Đọc hình ảnh hiện tại từ SQLite cục bộ trước khi xóa để làm bộ nhớ đệm chống mất ảnh (US-055 Guard)
    existing_images = {}
    if os.path.exists(DB_FILE):
        try:
            conn_old = sqlite3.connect(DB_FILE)
            cursor_old = conn_old.cursor()
            
            # Kiểm tra xem bảng listings có tồn tại không
            cursor_old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings'")
            table_exists = cursor_old.fetchone()
            
            if table_exists:
                # Kiểm tra các cột trong bảng listings
                cursor_old.execute("PRAGMA table_info(listings)")
                cols_old = {r[1] for r in cursor_old.fetchall()}
                
                req_cols = ["tk_id", "curated_config_json", "raw_images_tk_json", "raw_drive_images_json", "Images_Admin_JSON", "images_public_json", "status"]
                valid_cols = [c for c in req_cols if c in cols_old]
                
                if "tk_id" in valid_cols:
                    sql_select = f"SELECT {', '.join(valid_cols)} FROM listings"
                    rows_old = cursor_old.execute(sql_select).fetchall()
                    
                    for r in rows_old:
                        row_dict_old = dict(zip(valid_cols, r))
                        tk_id = row_dict_old.get("tk_id")
                        if not tk_id:
                            continue
                            
                        curated = row_dict_old.get("curated_config_json")
                        raw_tk = row_dict_old.get("raw_images_tk_json")
                        
                        has_real_images = False
                        if curated:
                            try:
                                parsed_curated = json.loads(curated)
                                imgs = parsed_curated.get("images", [])
                                if any(img.get("role") not in ["Sơ đồ", "diagram"] for img in imgs if isinstance(img, dict)):
                                    has_real_images = True
                            except Exception:
                                pass
                                
                        if not has_real_images and raw_tk:
                            try:
                                raw_urls = json.loads(raw_tk)
                                if len(raw_urls) > 1:
                                    has_real_images = True
                            except Exception:
                                pass
                                
                        if has_real_images:
                            existing_images[tk_id] = row_dict_old
                            
            conn_old.close()
            print(f"  - [🛡️ Bảo vệ] Đã lưu trữ bộ nhớ đệm {len(existing_images)} căn nhà có hình ảnh từ CSDL SQLite hiện tại.")
        except Exception as e:
            print(f"  - [⚠️ Bảo vệ] Không thể đọc CSDL SQLite cũ để sao lưu hình ảnh: {str(e)}")

    db_file_temp = DB_FILE + ".temp"
    print(f"[1/4] Khởi tạo cấu trúc database SQLite tạm: {db_file_temp}...")
    if os.path.exists(db_file_temp):
        try:
            os.remove(db_file_temp)
            print("  - Đã dọn dẹp file SQLite Temp cũ.")
        except Exception as e:
            print(f"  - Lỗi dọn dẹp file SQLite Temp: {str(e)}")
            
    init_db(db_file=db_file_temp)
    
    # 2. Kết nối Google Sheets và tải toàn bộ dữ liệu Pool & Source
    print("\n[2/4] Đang kết nối API và tải dữ liệu từ Google Sheets Pool và Source...")
    creds = get_google_credentials()
    cfg = load_config()
    if os.environ.get("STAGING") == "true":
        sheet_id = cfg.get("staging_pool_sheet_id") or cfg.get("sheet_id") or "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
        source_sheet_id = cfg.get("staging_source_sheet_id") or "1ljauQNEPA-8wM0vlJDRQkWjT2KQUwdR8tcq0r69dikk"
    else:
        sheet_id = cfg.get("sheet_id") or "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"
        source_sheet_id = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"
    
    if not creds:
        print("[❌ LỖI] Thiếu file credentials.json!")
        return
        
    try:
        import gspread
    except ImportError:
        print("[❌ LỖI] Chưa cài đặt thư viện gspread! Hãy cài đặt bằng lệnh: pip install gspread")
        return
        
    try:
        client = gspread.authorize(creds)
        
        # Đọc dữ liệu từ Pool sheet
        print("  - Đang đọc dữ liệu Google Sheets Pool...")
        spreadsheet = client.open_by_key(sheet_id)
        try:
            sheet = spreadsheet.worksheet("Pool")
        except Exception:
            sheet = spreadsheet.get_worksheet(0)
        all_values = sheet.get_all_values()
        
        # Đọc dữ liệu từ Source sheet
        print("  - Đang đọc dữ liệu Google Sheets Source...")
        try:
            source_spreadsheet = client.open_by_key(source_sheet_id)
            source_sheet = source_spreadsheet.worksheet("Source")
            source_values = source_sheet.get_all_values()
        except Exception as e:
            print(f"[⚠️ WARNING] Không thể đọc dữ liệu từ sheet Source, dữ liệu biên tập sẽ không được hợp nhất: {str(e)}")
            source_values = []

        # Đọc dữ liệu từ Pool_Images sheet (Hệ thống lưu ảnh cào thô)
        print("  - Đang đọc dữ liệu Google Sheets Pool_Images...")
        pool_images_map = {}
        try:
            pool_images_sheet = spreadsheet.worksheet("Pool_Images")
            pool_images_values = pool_images_sheet.get_all_values()
            if pool_images_values:
                for row in pool_images_values:
                    if not row or len(row) < 4:
                        continue
                    p_tk_id = row[0].strip()
                    p_type = row[2].strip()
                    if p_type == "crawl":
                        p_images = [url.strip() for url in row[4:] if url.strip().startswith("http")]
                        if p_images:
                            pool_images_map[p_tk_id] = p_images
                print(f"  - [✅ Pool_Images] Đã lập bản đồ map cho {len(pool_images_map)} căn nhà có hình ảnh cào gốc.")
        except Exception as e_pi:
            print(f"[⚠️ WARNING] Không thể đọc dữ liệu từ sheet Pool_Images: {str(e_pi)}")
            
    except Exception as e:
        print(f"[❌ LỖI] Lỗi kết nối Google Sheets: {str(e)}")
        return
        
    if len(all_values) < 2:
        print("[-] Không tìm thấy dữ liệu hoặc Sheets Pool rỗng!")
        return
        
    data_rows = all_values[1:] # Dữ liệu bắt đầu từ dòng 2 (index 1)
    print(f"  - Đang phân tích {len(data_rows)} dòng dữ liệu từ Google Sheets Pool...")

    # Build dynamic header index map for Source sheet to comply with Rule 6
    source_headers_map = {}
    if len(source_values) >= 2:
        row1 = source_values[0]
        row2 = source_values[1]
        for idx, h in enumerate(row2):
            h_clean = h.strip()
            if h_clean:
                source_headers_map[h_clean] = idx
        for idx, h in enumerate(row1):
            h_clean = h.strip()
            if h_clean and (h_clean not in source_headers_map or not row2[idx].strip()):
                source_headers_map[h_clean] = idx

    sys_id_idx = source_headers_map.get("System ID")
    huong_idx = source_headers_map.get("huong_nha")
    phuong_idx = source_headers_map.get("phuong")
    quan_idx = source_headers_map.get("quan")
    images_pub_idx = source_headers_map.get("Images_Public_JSON")

    # Xây dựng dictionary từ sheet Source để merge
    source_dict = {}
    if len(source_values) >= 3 and sys_id_idx is not None:
        # Dữ liệu bắt đầu từ dòng 3 (index 2), dòng 2 (index 1) là header snake_case
        for s_row in source_values[2:]:
            if len(s_row) > sys_id_idx:
                sys_id = s_row[sys_id_idx].strip()
                if sys_id:
                    source_dict[sys_id] = s_row
        print(f"  - Đang lập bản đồ map cho {len(source_dict)} căn đã biên tập từ Source...")

    # 3. Duyệt và ghi nhận vào SQLite cục bộ
    print("\n[3/4] Đang khôi phục dữ liệu vào SQLite và dọn dẹp hình ảnh...")
    
    conn = sqlite3.connect(db_file_temp, timeout=30.0)
    cursor = conn.cursor()
    
    restored_count = 0
    repaired_sheets_items = []
    seen_tk_ids = set()
    
    for idx, row_values in enumerate(data_rows, start=2):
        # Tránh các dòng rỗng hoàn toàn hoặc thiếu Mã Hàng
        if len(row_values) < 10 or not row_values[0]:
            continue
            
        # Đóng gói dữ liệu row_values khớp với POOL_HEADERS
        row_dict = {}
        for col_idx, header in enumerate(POOL_HEADERS):
            if col_idx < len(row_values):
                row_dict[header] = row_values[col_idx]
            else:
                row_dict[header] = ""
                
        # Trích xuất tk_id từ Link Gốc hoặc Mã Hàng
        link_goc = row_dict.get("Link Gốc", "")
        ma_hang = row_dict.get("Mã Hàng", "")
        
        tk_id = ""
        if link_goc:
            parts = link_goc.rstrip("/").split("/")
            if parts:
                tk_id = parts[-1].strip()
        if not tk_id and ma_hang:
            tk_id = ma_hang
            
        if not tk_id:
            continue
            
        if tk_id in seen_tk_ids:
            print(f"  - [⚠️ WARNING] Trùng tk_id '{tk_id}' ở dòng Pool {idx} (Mã Hàng: '{ma_hang}'). Bỏ qua dòng này để tránh lỗi UNIQUE constraint.")
            continue
        seen_tk_ids.add(tk_id)
            
        # 1. Đọc 5 ảnh sơ đồ thô/Cloudinary từ các cột sơ đồ
        sodo_imgs = []
        for i in range(1, 6):
            sodo_val = row_dict.get(f"Sơ đồ thửa đất {i}", "")
            if sodo_val and sodo_val.startswith("http"):
                sodo_imgs.append(sodo_val)
                
        # 2. Đọc 15 ảnh thường hiện tại trên Sheets (có nguy cơ lẫn sodo di cư ở đầu)
        interior_imgs = []
        for i in range(1, 16):
            img_val = row_dict.get(f"Ảnh {i}", "")
            if img_val and img_val.startswith("http"):
                interior_imgs.append(img_val)
                
        # Áp dụng thuật toán Zero-Comparison của anh Khang Ngô:
        # Số lượng sodo cào được của căn là N (độ dài sodo_imgs)
        sodo_count = len(sodo_imgs)
        
        # Cắt trực tiếp N hình đầu tiên khỏi cột Ảnh 1-15 trên Sheets (vì sodo bị gán nhầm lên đầu)
        if sodo_count > 0 and len(interior_imgs) >= sodo_count:
            clean_house_links = interior_imgs[sodo_count:]
        else:
            clean_house_links = list(interior_imgs)
            
        # Tạo mảng 15 ảnh thường mới sạch sẽ sau khi dồn
        new_interior_imgs = [""] * 15
        for i_idx, img in enumerate(clean_house_links):
            if i_idx < 15:
                new_interior_imgs[i_idx] = img
                
        # Kiểm tra xem mảng ảnh thường sau khi đôn sạch sodo có khác mảng cũ trên Sheets không
        has_difference = False
        for i in range(15):
            old_val = row_dict.get(f"Ảnh {i+1}", "")
            if old_val != new_interior_imgs[i]:
                has_difference = True
                break
                
        if has_difference:
            # Ghi nhận thay đổi để đồng bộ ngược lên Sheets Pool
            repaired_sheets_items.append({
                "row_idx": idx,
                "row_values": new_interior_imgs
            })
            # Cập nhật lại row_dict các cột Ảnh thường sạch
            for i in range(15):
                row_dict[f"Ảnh {i+1}"] = new_interior_imgs[i]
                
        # Chuẩn bị raw_drive_images đầy đủ cho SQLite (sơ đồ + ảnh sạch) để curation editor của client SPA hoạt động
        reconstructed_drive_images = sodo_imgs + clean_house_links
        
        # Mở rộng: Hợp nhất (Merge) dữ liệu đã biên tập từ sheet Source
        pool_sys_id = row_dict.get("System ID", "").strip()
        status = "raw_complete" # status mặc định
        
        if pool_sys_id and pool_sys_id in source_dict:
            status = "published"
            s_row = source_dict[pool_sys_id]
            
            # Map và ghi đè từ Source sheet sang row_dict
            SOURCE_TO_POOL_MAP = {
                "Mã Khang Ngô (ID)": 3,
                "Tiêu đề Public": 4,
                "DT Thực tế": 5,
                "Số Tầng": 6,
                "Mặt Tiền": 7,
                "Giá Public": 8,
                "Quận": 9,
                "Phường": 10,
                "Phân loại": 11,
                "Hướng": 12,
                "Phân loại Hẻm": 13,
                "Đường trước nhà (m)": 14,
                "Tình trạng nhà": 15,
                "Đánh giá (Admin)": 16,
                "Ngủ trệt (Admin)": 17,
                "CHDV (Admin)": 18,
                "Mô tả Public": 19,
                "Ảnh 1": 20,
                "Ảnh 2": 21,
                "Ảnh 3": 22,
                "Ảnh 4": 23,
                "Ảnh 5": 24,
                "Ảnh 6": 25,
                "Ảnh 7": 26,
                "Ảnh 8": 27,
                "Ảnh 9": 28,
                "Ảnh 10": 29,
                "Last Sync": 30,
                "Phường cũ (AI)": 31,
                "Số phòng ngủ": 32,
                "Số nhà vệ sinh": 33,
                "Đường": 34,
                "Trạng thái Public": 36,
                "System ID": 37,
                "Hình Mặt Tiền": 38
            }
            
            # Các cột văn bản đặc thù của curation, bắt buộc ghi đè
            curated_cols = ["Mã Khang Ngô (ID)", "Tiêu đề Public", "Mô tả Public", "Giá Public", "Trạng thái Public"]
            
            # Hướng sẽ được xử lý riêng để lưu vào custom_huong
            for header, s_col_idx in SOURCE_TO_POOL_MAP.items():
                if header == "Hướng":
                    continue
                if len(s_row) > s_col_idx:
                    s_val = s_row[s_col_idx].strip()
                    # Bỏ qua lỗi công thức của Google Sheets
                    if s_val.startswith("#") and s_val.endswith("!"):
                        continue
                        
                    if header in curated_cols:
                        row_dict[header] = s_val
                    elif s_val:
                        row_dict[header] = s_val
                        
        # US-110: Lấy giá trị Hướng biên tập từ Source sheet, mặc định bằng Hướng thô nếu chưa biên tập
        custom_huong_val = row_dict.get("Hướng", "").strip()
        custom_phuong_val = row_dict.get("Phường", "").strip()
        custom_quan_val = row_dict.get("Quận", "").strip()
        
        if pool_sys_id and pool_sys_id in source_dict:
            s_row = source_dict[pool_sys_id]
            if huong_idx is not None and len(s_row) > huong_idx:
                s_val = s_row[huong_idx].strip()
                if s_val and not (s_val.startswith("#") and s_val.endswith("!")):
                    custom_huong_val = s_val
            if phuong_idx is not None and len(s_row) > phuong_idx:
                s_val = s_row[phuong_idx].strip()
                if s_val and not (s_val.startswith("#") and s_val.endswith("!")):
                    custom_phuong_val = s_val
            if quan_idx is not None and len(s_row) > quan_idx:
                s_val = s_row[quan_idx].strip()
                if s_val and not (s_val.startswith("#") and s_val.endswith("!")):
                    custom_quan_val = s_val
                        
        # Reconstruct curated images config & populate listings_images table
        images_list = []
        
        # Images_Admin_JSON is ONLY stored on the Pool sheet
        images_admin_json_str = row_dict.get("Images_Admin_JSON", "").strip()
        if images_admin_json_str:
            try:
                parsed = json.loads(images_admin_json_str)
                role_map_en_to_vi = {
                    "diagram": "Sơ đồ",
                    "facade": "Mặt tiền",
                    "cover": "Bìa",
                    "alley": "Hẻm",
                    "interior": "Nội thất",
                    "hidden": "Ẩn",
                    "deleted": "deleted",
                    "sodo": "Sơ đồ"
                }
                if isinstance(parsed, list):
                    for img in parsed:
                        if isinstance(img, dict) and img.get("image_url"):
                            url = img.get("r2_url") or img.get("image_url")
                            en_role = img.get("role", "interior")
                            vi_role = role_map_en_to_vi.get(en_role, "Nội thất")
                            is_hidden = img.get("is_hidden", 0) == 1
                            images_list.append({
                                "url": url,
                                "role": vi_role,
                                "visible": not is_hidden,
                                "origin": img.get("origin", "crawl")
                            })
            except Exception:
                images_list = []

        # If published, override the visibility & order of images using the Source sheet's Images_Public_JSON
        if pool_sys_id and pool_sys_id in source_dict:
            s_row = source_dict[pool_sys_id]
            source_public_urls = []
            if images_pub_idx is not None and len(s_row) > images_pub_idx:
                pub_str = s_row[images_pub_idx].strip()
                if pub_str.startswith("[") and pub_str.endswith("]"):
                    try:
                        source_public_urls = json.loads(pub_str)
                    except Exception:
                        pass
                        
            # Normalize URLs for comparison
            def norm_url(u):
                if not u: return ""
                return u.split("?")[0].strip().lower()
                
            if images_list and source_public_urls:
                aligned_images = []
                # First, find public images in the exact order of source_public_urls
                for pub_url in source_public_urls:
                    if not pub_url: continue
                    norm_pub = norm_url(pub_url)
                    matched = None
                    for img in images_list:
                        if norm_url(img["url"]) == norm_pub:
                            matched = img
                            break
                    if matched:
                        matched["visible"] = True
                        aligned_images.append(matched)
                    else:
                        # Fallback if image not in curated config list
                        aligned_images.append({
                            "url": pub_url,
                            "role": "Nội thất",
                            "visible": True
                        })
                # Then, append any remaining images from images_list (which are hidden)
                for img in images_list:
                    if not any(norm_url(x["url"]) == norm_url(img["url"]) for x in aligned_images):
                        img["visible"] = False
                        aligned_images.append(img)
                images_list = aligned_images

        images_list = normalize_images_list(images_list)

        if images_list:
            reconstructed_drive_images = [img["url"] for img in images_list]

        # [US-152] Refactor: Chuyển đổi Khóa ngoại sang System ID
        pool_sys_id = row_dict.get("System ID", "").strip()
        curated_config = {
            "images": images_list,
            "system_id": pool_sys_id
        }
        curated_config_json_str = json.dumps(curated_config, ensure_ascii=False)

        # Build migrated_images list for listings_images and images_admin_json/images_public_json
        migrated_images = []
        role_map_vi_to_en = {
            "Sơ đồ": "diagram",
            "Mặt tiền": "facade",
            "Bìa": "cover",
            "Hẻm": "alley",
            "Nội thất": "interior",
            "Ẩn": "hidden",
            "deleted": "deleted",
            "sodo": "diagram"
        }
        for seq_idx, img in enumerate(images_list):
            vi_role = img.get("role", "Nội thất")
            resolved_role = role_map_vi_to_en.get(vi_role, "interior")
            is_visible = img.get("visible", True)
            origin = img.get("origin", "crawl")
            if origin in ["self", "user"]:
                origin = "self"
            else:
                origin = "crawl"
            is_hidden_val = 1 if (not is_visible or resolved_role in ["hidden", "deleted", "diagram", "facade"]) else 0
            
            migrated_images.append({
                "image_url": img["url"],
                "r2_url": img["url"],
                "role": resolved_role,
                "sequence_index": seq_idx,
                "origin": origin,
                "is_hidden": is_hidden_val
            })

        images_admin_json_str_to_save = json.dumps(migrated_images, ensure_ascii=False)
        
        public_urls = [
            img["r2_url"] if img["r2_url"] else img["image_url"]
            for img in migrated_images
            if img["is_hidden"] == 0 and img["role"] not in ["facade", "diagram", "deleted", "hidden"]
        ]
        images_public_json_str_to_save = json.dumps(public_urls, ensure_ascii=False)

        # Dựng manual_images_json động từ các ảnh có origin = "self"
        manual_list = [
            img["r2_url"] if img["r2_url"] else img["image_url"]
            for img in migrated_images
            if img.get("origin") == "self"
        ]
        manual_images_json_to_save = json.dumps(manual_list, ensure_ascii=False)

        # Write to listings_images
        try:
            cursor.execute("DELETE FROM listings_images WHERE tk_id = ?", (tk_id,))
            for img in migrated_images:
                cursor.execute("""
                    INSERT INTO listings_images (tk_id, system_id, image_url, r2_url, role, sequence_index, origin, is_hidden)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tk_id,
                    pool_sys_id,
                    img["image_url"],
                    img["r2_url"],
                    img["role"],
                    img["sequence_index"],
                    img["origin"],
                    img["is_hidden"]
                ))
        except Exception as e_img_save:
            print(f"  - [⚠️ WARNING] Lỗi chèn listings_images cho {tk_id}: {str(e_img_save)}")

        # [US-152] Đơn giản hóa: Gán link thô mặc định cho DB Tạm, vì khi merge ta loại bỏ hoàn toàn các cột thô (không merge sang Master).
        raw_images_tk_json_to_save = json.dumps(reconstructed_drive_images)

        # Trích xuất diện tích custom động từ Sheet Source
        custom_dt_thuc_te_val = ""
        custom_dt_so_val = ""
        if pool_sys_id and pool_sys_id in source_dict:
            s_row = source_dict[pool_sys_id]
            dt_thuc_te_idx = source_headers_map.get("dien_tich") or source_headers_map.get("DT_Thuc_te")
            if dt_thuc_te_idx is not None and len(s_row) > dt_thuc_te_idx:
                custom_dt_thuc_te_val = s_row[dt_thuc_te_idx].strip()
            dt_so_idx = source_headers_map.get("DT_tren_so") or source_headers_map.get("DT_Tren_so")
            if dt_so_idx is not None and len(s_row) > dt_so_idx:
                custom_dt_so_val = s_row[dt_so_idx].strip()

        # Chuẩn bị câu lệnh insert vào SQLite
        columns = [
            "tk_id", "status", "raw_images_tk_json", "raw_drive_images_json", 
            "custom_huong", "custom_phuong", "custom_quan", "curated_config_json", "Images_Admin_JSON", 
            "images_public_json", "manual_images_json", "custom_dt_thuc_te", "custom_dt_so"
        ]
        placeholders = ["?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?"]
        insert_vals = [
            tk_id, 
            status, 
            raw_images_tk_json_to_save, 
            json.dumps(reconstructed_drive_images), 
            custom_huong_val,
            custom_phuong_val,
            custom_quan_val,
            curated_config_json_str,
            images_admin_json_str_to_save,
            images_public_json_str_to_save,
            manual_images_json_to_save,
            custom_dt_thuc_te_val,
            custom_dt_so_val
        ]
        
        for header in POOL_HEADERS:
            safe_col = get_safe_col_name(header)
            columns.append(f"`{safe_col}`")
            placeholders.append("?")
            insert_vals.append(str(row_dict[header]) if row_dict[header] is not None else "")
            
        insert_sql = f"INSERT INTO listings ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(insert_sql, insert_vals)
        restored_count += 1

    conn.commit()
    conn.close()
    print(f"  - [💾 SQLite Temp Complete] Đã nạp thành công {restored_count} căn vào CSDL Tạm!")

    # Đồng bộ ngược links, blacklist và customer profiles từ Sheets vào CSDL Tạm
    try:
        restore_links_and_blacklist(client, db_file_temp)
    except Exception as e_lbl:
        print(f"  - [⚠️ WARNING Links/Blacklist/Profiles Sync] Lỗi đồng bộ vào CSDL Tạm: {str(e_lbl)}")

    # Thực hiện sao lưu CSDL Gốc và hợp nhất dữ liệu từ CSDL Tạm vào CSDL Gốc
    backup_master_database(DB_FILE)
    merge_temp_to_master(db_file_temp, DB_FILE)

    # Dọn dẹp tệp CSDL Tạm
    if os.path.exists(db_file_temp):
        try:
            os.remove(db_file_temp)
            print("  - Đã dọn dẹp file SQLite Tạm sau khi hợp nhất.")
        except Exception as e_rm:
            print(f"  - [⚠️ WARNING] Không thể xóa file SQLite Tạm: {str(e_rm)}")

    # 4. Đồng bộ ngược lên Google Sheets Pool các cột ảnh thường đã dọn dẹp (nếu được yêu cầu)
    if repaired_sheets_items:
        if repair_sheets:
            print(f"\n[4/4] Phát hiện {len(repaired_sheets_items)} căn bị lẫn sơ đồ trong Ảnh 1. Bắt đầu đồng bộ hàng loạt lên Sheets...")
            batch_size = 100
            groups = [repaired_sheets_items[i:i + batch_size] for i in range(0, len(repaired_sheets_items), batch_size)]
            
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
                sheet.batch_update(batch_data, value_input_option='USER_ENTERED')
                synced_count += len(group)
                time.sleep(1.0)
                
            print(f"  - [✅ Sheets Success] Đã đồng bộ chép đè an toàn thành công {synced_count} căn lên Google Sheets Pool!")
        else:
            print(f"\n[4/4] Phát hiện {len(repaired_sheets_items)} căn bị lẫn sơ đồ trong Ảnh 1.")
            print("  - [ℹ️ INFO] Bỏ qua việc tự động đồng bộ ngược lên Google Sheets theo cấu hình mặc định (Chỉ làm sạch ở DB SQLite cục bộ).")
            print("  - [ℹ️ INFO] Để làm sạch trang tính gốc trên Google Sheets, vui lòng chạy kèm tham số: --repair-sheets")
    else:
        print("\n[4/4] Tuyệt vời! Không phát hiện căn nào bị lẫn sơ đồ trong Ảnh 1.")

    print("======================================================================")
    print(f"🏁 KHÔI PHỤC DATABASE THÀNH CÔNG: Đã tái tạo {restored_count} căn, sửa sạch {len(repaired_sheets_items)} căn bị lỗi.")
    print("======================================================================")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Khôi phục SQLite database từ Google Sheets.")
    parser.add_argument("--repair-sheets", action="store_true", help="Đồng bộ ngược dọn dẹp làm sạch các cột hình ảnh phẳng trên Google Sheets.")
    args = parser.parse_args()
    restore_database(repair_sheets=args.repair_sheets)
