# -*- coding: utf-8 -*-
import os
import sys
import json
import sqlite3

# Import path helper
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pool_lego

def test_sync():
    db_file = "test_custom_sync.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        
    print("[*] Initializing test database schema...")
    # Temporarily override settings config load to force Pool2 mode
    original_exists = os.path.exists
    def mock_exists(path):
        if path == "settings.json":
            return True
        return original_exists(path)
    
    original_open = open
    def mock_open(path, *args, **kwargs):
        if path == "settings.json":
            import io
            return io.StringIO('{"active_pool_system": "Pool2"}')
        return original_open(path, *args, **kwargs)
        
    os.path.exists = mock_exists
    # We will invoke pool_lego.init_db
    pool_lego.init_db(db_file)
    
    # Restore mock overrides
    os.path.exists = original_exists
    
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Verify tables
    tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"[+] Tables created: {tables}")
    
    # Insert a raw mock listing into listings_v2
    tk_id = "test-custom-tk-id"
    cursor.execute("""
        INSERT INTO listings_v2 (tk_id, status, System_ID, Ma_Hang, Gia_chao, DT_Thuc_te, Mat_Tien, Chieu_dai)
        VALUES (?, 'raw_text', 'SYS-12345678-ABC', 'TK-ABC', '10.0', '50.0', '4.0', '12.5')
    """, (tk_id,))
    conn.commit()
    
    # Mock payload sent from curator.html
    data = {
        "tieu_de_public": "Căn hộ xinh xắn Quận 10",
        "mo_ta_public": "Mô tả public",
        "ngo_so_nha": "123",
        "quan": "Quận 10",
        "phuong": "Phường 12",
        "duong": "Nguyễn Tri Phương",
        "ma_khang_ngo": "Q10-NTP-123",
        "gia_public": "9.5",
        "phan_loai_hem": "Hẻm xe hơi",
        "duong_truoc_nha": "5",
        "mat_tien": "4.2",      # Edited Mặt tiền
        "chieu_dai": "13.0",     # Edited Chiều dài
        "so_phong_ngu": "3",
        "so_nha_ve_sinh": "3",
        "danh_gia": "Hàng Ngon",
        "ngu_tret": "Y",
        "chdv": "N",
        "tinh_trang_nha": "Mới",
        "phuong_cu_ai": "Phường cũ A",
        "hinh_nhan_dien": "https://url-hinh-nhan-dien",
        "hinh_mat_tien": "https://url-hinh-mat-tien",
        "so_do_1": "https://url-so-do-1",
        "so_do_2": "",
        "hem_imgs": ["https://url-hem-1", "https://url-hem-2"],
        "public_imgs": ["https://url-pub-1", "https://url-pub-2"],
        "anh_public_vd_1_3_5": "1,2",
        "anh_hem_public_vd_1_2": "1",
        "curated_config": {
            "images": [
                {"url": "https://url-pub-1", "role": "interior"},
                {"url": "https://url-hem-1", "role": "alley"}
            ]
        }
    }
    
    # Simulating the PUT logic in manager.py
    curated_config = data.get("curated_config")
    
    # 1. Update listings_v2 curated_config_json
    cursor.execute(
        "UPDATE listings_v2 SET curated_config_json = ? WHERE tk_id = ?",
        (json.dumps(curated_config), tk_id)
    )
    
    # 2. Update listings_v2 fields
    from pool_lego import get_safe_col_name
    fields_to_update = {
        "Tiêu đề Public": data.get("tieu_de_public"),
        "Mô tả Public": data.get("mo_ta_public"),
        "Giá Public": data.get("gia_public"),
        "Mã Khang Ngô (ID)": data.get("ma_khang_ngo"),
        "Phân loại Hẻm": data.get("phan_loai_hem"),
        "Đường trước nhà (m)": data.get("duong_truoc_nha"),
        "Mặt Tiền": data.get("mat_tien"),
        "Chiều dài": data.get("chieu_dai"),
        "Tình trạng nhà": data.get("tinh_trang_nha"),
        "Số phòng ngủ": data.get("so_phong_ngu"),
        "Số nhà vệ sinh": data.get("so_nha_ve_sinh"),
        "Đánh giá (Admin)": data.get("danh_gia"),
        "Ngủ trệt (Admin)": data.get("ngu_tret"),
        "CHDV (Admin)": data.get("chdv"),
        "Phường cũ (AI)": data.get("phuong_cu_ai"),
        "Ngõ/Số nhà": data.get("ngo_so_nha"),
        "Quận": data.get("quan"),
        "Phường": data.get("phuong"),
        "Đường": data.get("duong"),
        "Hình Nhận Diện": data.get("hinh_nhan_dien"),
        "Hình Mặt Tiền": data.get("hinh_mat_tien"),
        "Sơ đồ thửa đất 1": data.get("so_do_1"),
        "Sơ đồ thửa đất 2": data.get("so_do_2"),
        "Ảnh Public (VD: 1,3,5)": data.get("anh_public_vd_1_3_5"),
        "Ảnh Hẻm Public (VD: 1,2)": data.get("anh_hem_public_vd_1_2")
    }
    
    cursor.execute("PRAGMA table_info(listings_v2)")
    db_cols = {row[1] for row in cursor.fetchall()}

    update_cols = []
    update_vals = []
    for key, val in fields_to_update.items():
        safe_col = get_safe_col_name(key)
        if safe_col in db_cols:
            update_cols.append(f"`{safe_col}` = ?")
            update_vals.append(str(val) if val is not None else "")
        
    update_vals.append(tk_id)
    update_sql = f"UPDATE listings_v2 SET {', '.join(update_cols)} WHERE tk_id = ?"
    cursor.execute(update_sql, update_vals)
    
    # 3. Synchronize to listings_custom_v2
    row_v2 = cursor.execute("SELECT * FROM listings_v2 WHERE tk_id = ?", (tk_id,)).fetchone()
    if row_v2:
        d_v2 = dict(row_v2)
        system_id = d_v2.get("System_ID")
        if system_id:
            custom_exists = cursor.execute(
                "SELECT 1 FROM listings_custom_v2 WHERE System_ID = ?", (system_id,)
            ).fetchone()
            
            images_metadata = []
            if curated_config and isinstance(curated_config, dict):
                images_list = curated_config.get("images", [])
                safe_roles = ["interior", "alley", "cover", "interior_public", "alley_public"]
                images_metadata = [img for img in images_list if img.get("role") in safe_roles or not img.get("role")]
            
            custom_data = {
                "System_ID": system_id,
                "Ma_Khang_Ngo": data.get("ma_khang_ngo") or d_v2.get("Ma_Khang_Ngo_ID") or "",
                "Gia_Public": data.get("gia_public") or d_v2.get("Gia_Public") or "",
                "Tieu_De_Public": data.get("tieu_de_public") or d_v2.get("Tieu_de_Public") or "",
                "Mo_ta_Public": data.get("mo_ta_public") or d_v2.get("Mo_ta_Public") or "",
                "Note_Noi_Bo": data.get("note_noi_bo") or d_v2.get("Note_Noi_Bo") or "",
                "Trang_Thai_Giao_Dich": data.get("tinh_trang_nha") or d_v2.get("Tinh_trang_nha") or "",
                "Ngu_Tret": data.get("ngu_tret") or d_v2.get("Ngu_tret_Admin") or "",
                "CHDV": data.get("chdv") or d_v2.get("CHDV_Admin") or "",
                "Trang_Thai_KN": data.get("danh_gia") or d_v2.get("Danh_gia_Admin") or "",
                "images_metadata_json": json.dumps(images_metadata),
                "Dia_Chi_That": d_v2.get("Dia_Chi_That") or "",
                "So_Nha": data.get("ngo_so_nha") or d_v2.get("Ngo_So_nha") or "",
                "Ten_Duong": data.get("duong") or d_v2.get("Duong") or "",
                "Quan": data.get("quan") or d_v2.get("Quan") or "",
                "Phuong": data.get("phuong") or d_v2.get("Phuong") or "",
                "Duong": data.get("duong") or d_v2.get("Duong") or "",
                "Ngo_So_nha": data.get("ngo_so_nha") or d_v2.get("Ngo_So_nha") or "",
                "bedrooms": data.get("so_phong_ngu") or d_v2.get("So_phong_ngu") or "",
                "restrooms": data.get("so_nha_ve_sinh") or d_v2.get("So_nha_ve_sinh") or "",
                "minimumRoadWidth": data.get("duong_truoc_nha") or d_v2.get("Duong_truoc_nha_m") or "",
                "Noi_dung_chinh": d_v2.get("Noi_dung_chinh") or "",
                "Mo_ta_chi_tiet": d_v2.get("Mo_ta_chi_tiet") or "",
                "Gia_chao": d_v2.get("Gia_chao") or "",
                "DT_Thuc_te": d_v2.get("DT_Thuc_te") or "",
                "DT_Tren_so": d_v2.get("DT_Tren_so") or "",
                "So_Tang": d_v2.get("So_Tang") or "",
                "Mat_Tien": data.get("mat_tien") or d_v2.get("Mat_Tien") or "",
                "Chieu_dai": data.get("chieu_dai") or d_v2.get("Chieu_dai") or "",
                "Huong": d_v2.get("Huong") or "",
            }
            
            cursor.execute("PRAGMA table_info(listings_custom_v2)")
            custom_db_cols = [r[1] for r in cursor.fetchall()]
            valid_custom_data = {k: v for k, v in custom_data.items() if k in custom_db_cols}
            
            if custom_exists:
                update_pairs = []
                update_custom_vals = []
                for col_k, col_v in valid_custom_data.items():
                    if col_k != "System_ID":
                        update_pairs.append(f"`{col_k}` = ?")
                        update_custom_vals.append(str(col_v) if col_v is not None else "")
                update_custom_vals.append(system_id)
                cursor.execute(
                    f"UPDATE listings_custom_v2 SET {', '.join(update_pairs)} WHERE System_ID = ?",
                    update_custom_vals
                )
            else:
                cols_list = list(valid_custom_data.keys())
                placeholders = ["?"] * len(cols_list)
                insert_vals = [str(valid_custom_data[col_k]) if valid_custom_data[col_k] is not None else "" for col_k in cols_list]
                cursor.execute(
                    f"INSERT INTO listings_custom_v2 ({', '.join(cols_list)}) VALUES ({', '.join(placeholders)})",
                    insert_vals
                )
                
    conn.commit()
    
    # Verification
    print("\n[*] Verifying data updates...")
    res_v2 = cursor.execute("SELECT Mat_Tien, Chieu_dai, curated_config_json FROM listings_v2 WHERE tk_id = ?", (tk_id,)).fetchone()
    print(f"  - listings_v2 - Mat_Tien: {res_v2['Mat_Tien']} (Expected: 4.2)")
    print(f"  - listings_v2 - Chieu_dai: {res_v2['Chieu_dai']} (Expected: 13.0)")
    assert res_v2['Mat_Tien'] == '4.2', "listings_v2 Mat_Tien mismatch"
    assert res_v2['Chieu_dai'] == '13.0', "listings_v2 Chieu_dai mismatch"
    
    res_custom = cursor.execute("SELECT Mat_Tien, Chieu_dai, images_metadata_json FROM listings_custom_v2 WHERE System_ID = ?", (system_id,)).fetchone()
    print(f"  - listings_custom_v2 - Mat_Tien: {res_custom['Mat_Tien']} (Expected: 4.2)")
    print(f"  - listings_custom_v2 - Chieu_dai: {res_custom['Chieu_dai']} (Expected: 13.0)")
    assert res_custom['Mat_Tien'] == '4.2', "listings_custom_v2 Mat_Tien mismatch"
    assert res_custom['Chieu_dai'] == '13.0', "listings_custom_v2 Chieu_dai mismatch"
    
    print("\n[✅ SUCCESS] All test assertions passed successfully!")
    conn.close()
    if os.path.exists(db_file):
        os.remove(db_file)

if __name__ == "__main__":
    test_sync()
