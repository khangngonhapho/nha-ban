# -*- coding: utf-8 -*-
"""
==================================================
KHANG NGÔ NHÀ PHỐ - CÔNG CỤ TRUY VẤN CSDL TỰ ĐỘNG
Hỗ trợ hiển thị trực quan thông tin chi tiết và hình ảnh dạng HTML
==================================================
"""

import os
import sys
import json
import sqlite3
import webbrowser
from datetime import datetime

# Ép terminal Windows hiển thị UTF-8 tránh lỗi font tiếng Việt
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def remove_accents(input_str):
    """⚠️ DELEGATED: Đã chuyển sang core.business_rules.remove_accents()"""
    from core.business_rules import remove_accents as _remove_accents
    return _remove_accents(input_str)

def get_db_file():
    """⚠️ DELEGATED: Đã chuyển sang core.db.get_db_file()"""
    from core.db import get_db_file as _get_db_file
    return _get_db_file()

def get_listings_table_name(db_file):
    """⚠️ DELEGATED: Đã chuyển sang core.db.get_listings_table_name()"""
    from core.db import get_listings_table_name as _get_table_name
    return _get_table_name(db_file)

def get_db_stats(db_file, table_name):
    if not os.path.exists(db_file):
        return None
    try:
        conn = sqlite3.connect(db_file, timeout=10.0)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            conn.close()
            return None
            
        total = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        raw_text = cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE status = 'raw_text'").fetchone()[0]
        raw_complete = cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE status = 'raw_complete'").fetchone()[0]
        published = cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE status = 'published'").fetchone()[0]
        
        # Image count if Pool2
        image_count = 0
        if table_name == "listings_v2":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='listings_images'")
            if cursor.fetchone():
                image_count = cursor.execute("SELECT COUNT(*) FROM listings_images").fetchone()[0]
                
        conn.close()
        return {
            "total": total,
            "raw_text": raw_text,
            "raw_complete": raw_complete,
            "published": published,
            "image_count": image_count
        }
    except Exception as e:
        print(f"[❌ LỖI] Không thể đọc thống kê CSDL: {str(e)}")
        return None

def search_db(db_file, table_name, search_term):
    conn = sqlite3.connect(db_file, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.create_function("remove_accents", 1, remove_accents)
    cursor = conn.cursor()
    
    # Clean search input
    search_term_clean = search_term.strip()
    q_like_accents = f"%{search_term_clean}%"
    q_like_no_accents = "%" + remove_accents(search_term_clean).lower().replace(" ", "%") + "%"
    
    # Lấy thông tin các cột thực tế của bảng để tránh lỗi cú pháp SQL
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = [r[1] for r in cursor.fetchall()]
    
    t_prefix = "listings_v2." if table_name == "listings_v2" else ""
    # Xây dựng câu truy vấn động
    where_clauses = [f"{t_prefix}tk_id LIKE :raw"]
    if "Ma_Hang" in cols:
        where_clauses.append(f"{t_prefix}Ma_Hang LIKE :raw")
    elif "M__H_ng" in cols:
        where_clauses.append(f"{t_prefix}M__H_ng LIKE :raw")
        
    if "System_ID" in cols:
        where_clauses.append(f"{t_prefix}System_ID LIKE :raw")
        
    # Tìm kiếm theo địa chỉ
    address_cols = []
    if "Ngo_So_nha" in cols: address_cols.append("Ngo_So_nha")
    elif "Ng__S__nh_" in cols: address_cols.append("Ng__S__nh_")
    
    if "Duong" in cols: address_cols.append("Duong")
    elif "___ng" in cols: address_cols.append("___ng")
    
    if address_cols:
        concat_str = " || ' ' || ".join([f"{t_prefix}`{c}`" for c in address_cols])
        where_clauses.append(f"lower(remove_accents({concat_str})) LIKE :q")
        for c in address_cols:
            where_clauses.append(f"lower(remove_accents({t_prefix}`{c}`)) LIKE :q")
            
    if table_name == "listings_v2":
        sql = """
            SELECT listings_v2.*, 
                   listings_custom_v2.Ma_Khang_Ngo AS custom_Ma_Khang_Ngo, 
                   listings_custom_v2.Gia_Public AS custom_Gia_Public, 
                   listings_custom_v2.Tieu_De_Public AS custom_Tieu_De_Public, 
                   listings_custom_v2.Mo_ta_Public AS custom_Mo_ta_Public, 
                   listings_custom_v2.Note_Noi_Bo AS custom_Note_Noi_Bo, 
                   listings_custom_v2.Trang_Thai_Giao_Dich AS custom_Trang_Thai_Giao_Dich, 
                   listings_custom_v2.Ngu_Tret AS custom_Ngu_Tret, 
                   listings_custom_v2.CHDV AS custom_CHDV, 
                   listings_custom_v2.Trang_Thai_KN AS custom_Trang_Thai_KN, 
                   listings_custom_v2.images_metadata_json AS custom_images_metadata_json, 
                   listings_custom_v2.Dia_Chi_That AS custom_Dia_Chi_That, 
                   listings_custom_v2.So_Nha AS custom_So_Nha, 
                   listings_custom_v2.Ten_Duong AS custom_Ten_Duong,
                   listings_custom_v2.bedrooms AS custom_bedrooms,
                   listings_custom_v2.restrooms AS custom_restrooms,
                   listings_custom_v2.minimumRoadWidth AS custom_minimumRoadWidth,
                   listings_custom_v2.Noi_dung_chinh AS custom_Noi_dung_chinh,
                   listings_custom_v2.Mo_ta_chi_tiet AS custom_Mo_ta_chi_tiet,
                   listings_custom_v2.Gia_chao AS custom_Gia_chao,
                   listings_custom_v2.DT_Thuc_te AS custom_DT_Thuc_te,
                   listings_custom_v2.DT_Tren_so AS custom_DT_Tren_so,
                   listings_custom_v2.So_Tang AS custom_So_Tang,
                   listings_custom_v2.Mat_Tien AS custom_Mat_Tien,
                   listings_custom_v2.Chieu_dai AS custom_Chieu_dai,
                   listings_custom_v2.Huong AS custom_Huong,
                   listings_custom_v2.Criteria_Duong_truoc_nha AS custom_Criteria_Duong_truoc_nha,
                   listings_custom_v2.Criteria_Noi_that AS custom_Criteria_Noi_that,
                   listings_custom_v2.Criteria_Thang_may AS custom_Criteria_Thang_may,
                   listings_custom_v2.Criteria_Loai_ngo AS custom_Criteria_Loai_ngo,
                   listings_custom_v2.Criteria_Khoang_cach_bai_do_xe AS custom_Criteria_Khoang_cach_bai_do_xe,
                   listings_custom_v2.Criteria_Kinh_doanh_Dong_tien AS custom_Criteria_Kinh_doanh_Dong_tien,
                   listings_custom_v2.Criteria_Huong_nha AS custom_Criteria_Huong_nha,
                   listings_custom_v2.Criteria_Khoang_cach_duong_oto AS custom_Criteria_Khoang_cach_duong_oto
            FROM listings_v2 
            LEFT JOIN listings_custom_v2 ON listings_v2.System_ID = listings_custom_v2.System_ID
            WHERE 
        """ + " OR ".join(where_clauses) + " LIMIT 50"
    else:
        sql = f"SELECT * FROM {table_name} WHERE " + " OR ".join(where_clauses) + " LIMIT 50"
        
    try:
        rows = cursor.execute(sql, {"raw": q_like_accents, "q": q_like_no_accents}).fetchall()
        # Chuyển đổi thành danh sách dict và áp dụng custom overrides
        result = []
        for r in rows:
            d = dict(r)
            if table_name == "listings_v2" and "custom_Ma_Khang_Ngo" in d:
                if d.get("custom_Ma_Khang_Ngo"): d["Ma_Khang_Ngo_ID"] = d["custom_Ma_Khang_Ngo"]
                if d.get("custom_Tieu_De_Public"): d["Tieu_de_Public"] = d["custom_Tieu_De_Public"]
                if d.get("custom_Mo_ta_Public"): d["Mo_ta_Public"] = d["custom_Mo_ta_Public"]
                if d.get("custom_Gia_Public"): d["Gia_Public"] = d["custom_Gia_Public"]
                if d.get("custom_Note_Noi_Bo"): d["Note_Noi_Bo"] = d["custom_Note_Noi_Bo"]
                if d.get("custom_Trang_Thai_Giao_Dich"): d["Tinh_trang_nha"] = d["custom_Trang_Thai_Giao_Dich"]
                if d.get("custom_Ngu_Tret"): d["Ngu_tret_Admin"] = d["custom_Ngu_Tret"]
                if d.get("custom_CHDV"): d["CHDV_Admin"] = d["custom_CHDV"]
                if d.get("custom_Trang_Thai_KN"): d["Danh_gia_Admin"] = d["custom_Trang_Thai_KN"]
                
                # Nhóm đè địa chỉ / kỹ thuật
                if d.get("custom_So_Nha"): d["Ngo_So_nha"] = d["custom_So_Nha"]
                if d.get("custom_Ten_Duong"): d["Duong"] = d["custom_Ten_Duong"]
                if d.get("custom_Quan"): d["Quan"] = d["custom_Quan"]
                if d.get("custom_Phuong"): d["Phuong"] = d["custom_Phuong"]
                if d.get("custom_bedrooms"): d["bedrooms"] = d["custom_bedrooms"]
                if d.get("custom_restrooms"): d["restrooms"] = d["custom_restrooms"]
                if d.get("custom_minimumRoadWidth"): d["minimumRoadWidth"] = d["custom_minimumRoadWidth"]
                if d.get("custom_Noi_dung_chinh"): d["Noi_dung_chinh"] = d["custom_Noi_dung_chinh"]
                if d.get("custom_Mo_ta_chi_tiet"): d["Mo_ta_chi_tiet"] = d["custom_Mo_ta_chi_tiet"]
                if d.get("custom_Gia_chao"): d["Gia_chao"] = d["custom_Gia_chao"]
                if d.get("custom_DT_Thuc_te"): d["DT_Thuc_te"] = d["custom_DT_Thuc_te"]
                if d.get("custom_DT_Tren_so"): d["DT_Tren_so"] = d["custom_DT_Tren_so"]
                if d.get("custom_So_Tang"): d["So_Tang"] = d["custom_So_Tang"]
                if d.get("custom_Mat_Tien"): d["Mat_Tien"] = d["custom_Mat_Tien"]
                if d.get("custom_Chieu_dai"): d["Chieu_dai"] = d["custom_Chieu_dai"]
                huong_val = d.get("custom_huong") or d.get("custom_Huong")
                if huong_val: d["Huong"] = huong_val
                phuong_val = d.get("custom_phuong") or d.get("custom_Phuong")
                if phuong_val: d["Phuong"] = phuong_val
                quan_val = d.get("custom_quan") or d.get("custom_Quan")
                if quan_val: d["Quan"] = quan_val
                
            # US-153: Apply custom fields override for both Pool1 and Pool2
            custom_huong_val = d.get("custom_huong") or d.get("custom_Huong")
            if custom_huong_val:
                d["Huong"] = custom_huong_val
                
            custom_phuong_val = d.get("custom_phuong") or d.get("custom_Phuong")
            if custom_phuong_val:
                d["Phuong"] = custom_phuong_val
                
            custom_quan_val = d.get("custom_quan") or d.get("custom_Quan")
            if custom_quan_val:
                d["Quan"] = custom_quan_val

            custom_dt_thuc_te_val = d.get("custom_dt_thuc_te")
            if custom_dt_thuc_te_val:
                d["DT_Thuc_te"] = custom_dt_thuc_te_val

            custom_dt_so_val = d.get("custom_dt_so")
            if custom_dt_so_val:
                d["DT_Tren_so"] = custom_dt_so_val

            # Nhóm Tiêu chí
            for ck in ["Criteria_Duong_truoc_nha", "Criteria_Noi_that", "Criteria_Thang_may", "Criteria_Loai_ngo", "Criteria_Khoang_cach_bai_do_xe", "Criteria_Kinh_doanh_Dong_tien", "Criteria_Huong_nha", "Criteria_Khoang_cach_duong_oto"]:
                custom_ck = "custom_" + ck
                if d.get(custom_ck):
                    d[ck] = d[custom_ck]

            result.append(d)
        conn.close()
        return result
    except Exception as e:
        print(f"[❌ LỖI] Lỗi truy vấn tìm kiếm: {str(e)}")
        conn.close()
        return []

def get_images_for_listing(db_file, table_name, tk_id, listing_dict):
    """
    Lấy danh sách hình ảnh của căn nhà hỗ trợ cả Pool1 (dạng cột) và Pool2 (dạng bảng dòng).
    """
    images = {"diagram": [], "interior": [], "facade": [], "alley": [], "cover": []}
    
    conn = sqlite3.connect(db_file, timeout=10.0)
    cursor = conn.cursor()
    
    if table_name == "listings_v2":
        # Pool2: Lấy từ bảng listings_images
        try:
            cursor.execute("""
                SELECT image_url, role, sequence_index 
                FROM listings_images 
                WHERE tk_id = ? 
                ORDER BY sequence_index ASC
            """, (tk_id,))
            rows = cursor.fetchall()
            for r in rows:
                url, role, seq = r
                role = role or "interior"
                if role in images:
                    images[role].append(url)
                else:
                    images["interior"].append(url)
        except Exception as e:
            print(f"[⚠️ WARNING] Lỗi đọc bảng listings_images: {str(e)}")
    else:
        # Pool1: Bóc tách từ 89 cột của listing_dict
        # Sơ đồ
        for i in range(1, 6):
            col = f"S____th__đ?t_{i}"
            if col in listing_dict and listing_dict[col]:
                images["diagram"].append(listing_dict[col])
            elif f"So_do_thua_dat_{i}" in listing_dict and listing_dict[f"So_do_thua_dat_{i}"]:
                images["diagram"].append(listing_dict[f"So_do_thua_dat_{i}"])
                
        # Mặt tiền
        if "Hnh_M?t_Ti?n" in listing_dict and listing_dict["Hnh_M?t_Ti?n"]:
            images["facade"].append(listing_dict["Hnh_M?t_Ti?n"])
        elif "Hinh_Mat_Tien" in listing_dict and listing_dict["Hinh_Mat_Tien"]:
            images["facade"].append(listing_dict["Hinh_Mat_Tien"])
            
        # Hẻm
        for i in range(1, 11):
            col = f"Hnh_H?m_{i}"
            if col in listing_dict and listing_dict[col]:
                images["alley"].append(listing_dict[col])
            elif f"Hinh_Hem_{i}" in listing_dict and listing_dict[f"Hinh_Hem_{i}"]:
                images["alley"].append(listing_dict[f"Hinh_Hem_{i}"])
                
        # Ảnh nội thất
        for i in range(1, 26):
            col = f"?nh_{i}"
            if col in listing_dict and listing_dict[col]:
                images["interior"].append(listing_dict[col])
            elif f"Anh_{i}" in listing_dict and listing_dict[f"Anh_{i}"]:
                images["interior"].append(listing_dict[f"Anh_{i}"])
                
    conn.close()
    return images

def generate_html_viewer(listing, images, table_name):
    """
    BUSINESS RULES: docs/business_rules/INDEX.md
    RELATED FILES: templates/components/detail_view.py
    TESTS: tests/test_templates.py
    OWNER: US-120A
    """
    from templates.components.detail_view import render_detail_view
    return render_detail_view(listing, images, table_name)

def main():
    db_file = get_db_file()
    table_name = get_listings_table_name(db_file)
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("============================================================")
        print("       CÔNG CỤ TRA CỨU CSDL SQLITE - KHANG NGÔ LAND")
        print(f"       Database hiện tại: {db_file} ({table_name})")
        print("============================================================")
        print("[1] Xem báo cáo thống kê tổng quan (Phân bổ trạng thái)")
        print("[2] Tìm kiếm & Xem chi tiết căn nhà (Dựng HTML hiển thị ảnh)")
        print("[3] Thoát")
        print("============================================================")
        
        choice = input("👉 Chọn chức năng [1-3]: ").strip()
        
        if choice == "1":
            stats = get_db_stats(db_file, table_name)
            if not stats:
                print(f"\n[-] Chưa tìm thấy dữ liệu bảng '{table_name}' trong {db_file}.")
            else:
                print("\n📊 BÁO CÁO THỐNG KÊ CƠ SỞ DỮ LIỆU:")
                print(f"📍 Tổng số căn đã cào về SQLite: {stats['total']} căn")
                print(f"🔸 Đang chờ di cư ảnh (status='raw_text'): {stats['raw_text']} căn")
                print(f"🔹 Đã di cư ảnh xong (status='raw_complete'): {stats['raw_complete']} căn")
                print(f"✅ Đã biên tập & xuất bản lên Sheets (status='published'): {stats['published']} căn")
                if stats['image_count'] > 0:
                    print(f"🖼️ Tổng số dòng hình ảnh lưu ở listings_images: {stats['image_count']} dòng")
            input("\nNhấn [ENTER] để quay lại menu...")
            
        elif choice == "2":
            search_str = input("\n👉 Nhập Mã TK, Mã Hàng, hoặc Số nhà + Tên đường để tìm kiếm: ").strip()
            if not search_str:
                continue
                
            results = search_db(db_file, table_name, search_str)
            if not results:
                print("\n[-] Không tìm thấy căn nhà nào khớp với từ khóa.")
                input("\nNhấn [ENTER] để tiếp tục...")
                continue
                
            print(f"\n[+] Tìm thấy {len(results)} kết quả phù hợp:")
            for idx, r in enumerate(results, 1):
                ma_hang = r.get("Ma_Hang") or r.get("M__H_ng") or "N/A"
                sys_id = r.get("System_ID") or r.get("System_ID") or "N/A"
                so_nha = r.get("Ngo_So_nha") or r.get("Ng__S__nh_") or ""
                duong = r.get("Duong") or r.get("___ng") or ""
                phuong = r.get("Phuong") or r.get("Ph__ng") or ""
                quan = r.get("Quan") or r.get("Qu_n") or ""
                gia = r.get("Gia_chao") or r.get("Gi__ch_o") or "N/A"
                print(f"  [{idx}] {ma_hang} ({sys_id}) | Địa chỉ: {so_nha} {duong}, P.{phuong}, {quan} | Giá chào: {gia} tỷ")
                
            try:
                selected_idx = int(input(f"\n👉 Chọn số thứ tự để xem chi tiết [1-{len(results)}] (Hoặc nhấn 0 để quay lại): ").strip())
                if selected_idx < 1 or selected_idx > len(results):
                    continue
            except ValueError:
                continue
                
            selected_listing = results[selected_idx - 1]
            tk_id = selected_listing.get("tk_id")
            
            # Tải ảnh
            images = get_images_for_listing(db_file, table_name, tk_id, selected_listing)
            
            # Tạo trang HTML
            html_code = generate_html_viewer(selected_listing, images, table_name)
            
            # Ghi ra file tạm thời
            viewer_file = "temp_viewer.html"
            try:
                with open(viewer_file, "w", encoding="utf-8") as f:
                    f.write(html_code)
                
                print(f"\n[🚀 RUNNING] Đang tự động mở trang chi tiết trên trình duyệt...")
                webbrowser.open(os.path.abspath(viewer_file))
                time_to_wait = 2
            except Exception as e:
                print(f"[❌ LỖI] Không thể ghi file HTML viewer: {str(e)}")
            input("\nNhấn [ENTER] để quay lại menu...")
            
        elif choice == "3":
            print("\nCảm ơn anh Khang đã sử dụng công cụ! Tạm biệt.")
            break

if __name__ == "__main__":
    main()
