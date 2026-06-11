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
    if not input_str:
        return ""
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỊịỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
    s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
    res = []
    for c in input_str:
        idx = s1.find(c)
        if idx != -1:
            res.append(s0[idx])
        else:
            res.append(c)
    return "".join(res)

def get_db_file():
    try:
        config_file = "settings.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                if cfg.get("active_pool_system") == "Pool2":
                    return "raw_archive_v2.db"
    except Exception:
        pass
    return "raw_archive.db"

def get_listings_table_name(db_file):
    if "raw_archive_v2.db" in db_file:
        return "listings_v2"
    return "listings"

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
    
    # Xây dựng câu truy vấn động
    where_clauses = ["tk_id LIKE :raw"]
    if "Ma_Hang" in cols:
        where_clauses.append("Ma_Hang LIKE :raw")
    elif "M__H_ng" in cols:
        where_clauses.append("M__H_ng LIKE :raw")
        
    if "System_ID" in cols:
        where_clauses.append("System_ID LIKE :raw")
    elif "System_ID" in cols:
        where_clauses.append("System_ID LIKE :raw")
        
    # Tìm kiếm theo địa chỉ
    address_cols = []
    if "Ngo_So_nha" in cols: address_cols.append("Ngo_So_nha")
    elif "Ng__S__nh_" in cols: address_cols.append("Ng__S__nh_")
    
    if "Duong" in cols: address_cols.append("Duong")
    elif "___ng" in cols: address_cols.append("___ng")
    
    if address_cols:
        concat_str = " || ' ' || ".join(address_cols)
        where_clauses.append(f"lower(remove_accents({concat_str})) LIKE :q")
        for c in address_cols:
            where_clauses.append(f"lower(remove_accents({c})) LIKE :q")
            
    sql = f"SELECT * FROM {table_name} WHERE " + " OR ".join(where_clauses) + " LIMIT 50"
    
    try:
        rows = cursor.execute(sql, {"raw": q_like_accents, "q": q_like_no_accents}).fetchall()
        # Chuyển đổi thành danh sách dict
        result = [dict(r) for r in rows]
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
    # Trích xuất các trường thông tin chính
    tk_id = listing.get("tk_id") or ""
    system_id = listing.get("System_ID") or listing.get("System_ID") or "N/A"
    ma_hang = listing.get("Ma_Hang") or listing.get("M__H_ng") or "N/A"
    
    # Địa chỉ
    so_nha = listing.get("Ngo_So_nha") or listing.get("Ng__S__nh_") or ""
    duong = listing.get("Duong") or listing.get("___ng") or ""
    phuong = listing.get("Phuong") or listing.get("Ph__ng") or ""
    quan = listing.get("Quan") or listing.get("Qu_n") or ""
    address = f"{so_nha} {duong}, Phường {phuong}, {quan}".strip(", ")
    
    # Giá & DT
    gia = listing.get("Gia_chao") or listing.get("Gi__ch_o") or "N/A"
    dt_thuc = listing.get("DT_Thuc_te") or listing.get("DT_Th?c_t?") or "N/A"
    dt_so = listing.get("DT_Tren_so") or listing.get("DT_Trn_s?") or "N/A"
    so_tang = listing.get("So_Tang") or listing.get("S__T?ng") or "N/A"
    mat_tien = listing.get("Mat_Tien") or listing.get("M?t_Ti?n") or "N/A"
    chieu_dai = listing.get("Chieu_dai") or "N/A"
    huong = listing.get("Huong") or listing.get("Hu_ng") or "N/A"
    duong_vao = listing.get("minimumRoadWidth") or listing.get("___ng_tr__c_nh___m_") or "N/A"
    
    # Liên hệ
    ten_chu = listing.get("Ten_Chu_Nha") or listing.get("Tn_Ch__Nh_") or "N/A"
    sdt_chu = listing.get("Dien_thoai_1") or listing.get("Đi?n_tho?i_1") or "N/A"
    ten_dc = listing.get("Ten_Dau_Chu") or listing.get("Tn_Đ?u_Ch__H?p_đ?ng_") or "N/A"
    sdt_dc = listing.get("Dien_thoai_Dau_Chu") or listing.get("Đi?n_tho?i_Đ?u_Ch_") or "N/A"
    
    # Mô tả
    mo_ta = listing.get("Mo_ta_chi_tiet") or listing.get("M_t__chi_ti?t") or ""
    noi_dung = listing.get("Noi_dung_chinh") or listing.get("N?i_dung_chnh") or ""
    
    # Link gốc
    link_goc = listing.get("Link_Goc") or listing.get("Link_G?c") or "#"
    
    # Phân loại criteria nhóm
    criteria_html = ""
    # Tìm kiếm các key Criteria_ trong listing
    criteria_fields = {k: v for k, v in listing.items() if k.startswith("Criteria_") and v}
    if criteria_fields:
        criteria_html += '<div class="section-title">Tiêu chí phân loại (Criteria)</div><div class="grid-criteria">'
        for k, v in criteria_fields.items():
            friendly_name = k.replace("Criteria_", "").replace("_", " ")
            criteria_html += f"""
            <div class="criteria-card">
                <span class="criteria-label">{friendly_name}</span>
                <span class="criteria-value">{v}</span>
            </div>
            """
        criteria_html += "</div>"

    # Xây dựng thư viện ảnh HTML
    images_html = ""
    
    # 1. Ảnh sơ đồ
    if images["diagram"]:
        images_html += '<div class="section-title">Sơ đồ thửa đất / Bản vẽ</div><div class="image-grid diagram-grid">'
        for img_url in images["diagram"]:
            images_html += f'<div class="image-wrapper"><img src="{img_url}" alt="Sơ đồ thửa đất" onerror="this.src=\'https://placehold.co/400x300?text=Loi+anh+so+do\'"></div>'
        images_html += '</div>'
        
    # 2. Ảnh mặt tiền
    if images["facade"]:
        images_html += '<div class="section-title">Hình ảnh Mặt Tiền</div><div class="image-grid facade-grid">'
        for img_url in images["facade"]:
            images_html += f'<div class="image-wrapper"><img src="{img_url}" alt="Ảnh mặt tiền" onerror="this.src=\'https://placehold.co/400x300?text=Loi+anh+mat+tien\'"></div>'
        images_html += '</div>'

    # 3. Ảnh hẻm
    if images["alley"]:
        images_html += '<div class="section-title">Hình ảnh Hẻm trước nhà</div><div class="image-grid alley-grid">'
        for img_url in images["alley"]:
            images_html += f'<div class="image-wrapper"><img src="{img_url}" alt="Ảnh hẻm" onerror="this.src=\'https://placehold.co/400x300?text=Loi+anh+hem\'"></div>'
        images_html += '</div>'

    # 4. Ảnh nội thất / Ảnh sản phẩm khác
    all_interiors = images["interior"] + images["cover"]
    if all_interiors:
        images_html += '<div class="section-title">Hình ảnh Nội thất / Chi tiết</div><div class="image-grid interior-grid">'
        for img_url in all_interiors:
            images_html += f'<div class="image-wrapper"><img src="{img_url}" alt="Ảnh nội thất" onerror="this.src=\'https://placehold.co/400x300?text=Loi+hinh+anh\'"></div>'
        images_html += '</div>'

    # HTML Template
    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chi tiết căn nhà - {ma_hang}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --primary-color: #38bdf8;
            --accent-color: #f43f5e;
            --success-color: #10b981;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            padding: 20px;
            background-image: radial-gradient(circle at 10% 20%, rgba(56, 189, 248, 0.05) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(244, 63, 94, 0.03) 0%, transparent 40%);
            background-attachment: fixed;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            margin-bottom: 20px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .header-title h1 {{
            font-size: 28px;
            font-weight: 700;
            color: var(--primary-color);
            letter-spacing: -0.5px;
        }}
        
        .header-title p {{
            font-size: 14px;
            color: var(--text-muted);
        }}
        
        .tag-status {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--primary-color);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }}
        
        .grid-info {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        @media (max-width: 768px) {{
            .grid-info {{
                grid-template-columns: 1fr;
            }}
            .header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }}
        }}
        
        .card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 16px;
            color: var(--primary-color);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
        }}
        
        .info-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .info-table td {{
            padding: 10px 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            vertical-align: top;
        }}
        
        .info-table td.label {{
            color: var(--text-muted);
            width: 40%;
            font-weight: 500;
        }}
        
        .info-table td.value {{
            color: var(--text-main);
            font-weight: 600;
        }}
        
        .description-box {{
            white-space: pre-wrap;
            color: #cbd5e1;
            font-size: 15px;
            margin-bottom: 16px;
            background: rgba(15, 23, 42, 0.4);
            padding: 16px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }}
        
        .usp-box {{
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #a7f3d0;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
        }}
        
        .grid-criteria {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 12px;
            margin-top: 10px;
            margin-bottom: 20px;
        }}
        
        .criteria-card {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            padding: 12px;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        
        .criteria-label {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-muted);
        }}
        
        .criteria-value {{
            font-size: 13px;
            font-weight: 600;
            color: var(--text-main);
        }}
        
        .image-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 30px;
        }}
        
        .image-wrapper {{
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            aspect-ratio: 4/3;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .image-wrapper img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }}
        
        .image-wrapper:hover img {{
            transform: scale(1.05);
        }}
        
        .diagram-grid .image-wrapper {{
            aspect-ratio: auto;
            max-height: 500px;
        }}
        
        .diagram-grid .image-wrapper img {{
            object-fit: contain;
            height: auto;
            max-height: 500px;
        }}
        
        .btn-link {{
            display: inline-block;
            background: var(--primary-color);
            color: #0f172a;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s ease;
            margin-top: 10px;
            text-align: center;
            width: 100%;
        }}
        
        .btn-link:hover {{
            background: #7dd3fc;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <div class="header-title">
                <h1>{ma_hang} / {system_id}</h1>
                <p>Địa chỉ gốc: {address}</p>
            </div>
            <div>
                <span class="tag-status">Chế độ: {table_name.upper()}</span>
            </div>
        </div>
        
        <!-- INFO GRID -->
        <div class="grid-info">
            <!-- LEFT COLUMN: CONTENT -->
            <div class="card">
                {f'<div class="usp-box"><strong>Nội dung chính (USP):</strong><br>{noi_dung}</div>' if noi_dung else ''}
                
                <div class="section-title">Mô tả chi tiết căn nhà</div>
                <div class="description-box">{mo_ta}</div>
                
                {criteria_html}
            </div>
            
            <!-- RIGHT COLUMN: SPECS -->
            <div class="card" style="height: fit-content;">
                <div class="section-title">Thông số kỹ thuật</div>
                <table class="info-table">
                    <tr>
                        <td class="label">Giá chào</td>
                        <td class="value" style="color: var(--accent-color); font-size: 18px;">{gia} Tỷ</td>
                    </tr>
                    <tr>
                        <td class="label">DT Thực tế</td>
                        <td class="value">{dt_thuc} m²</td>
                    </tr>
                    <tr>
                        <td class="label">DT Trên sổ</td>
                        <td class="value">{dt_so} m²</td>
                    </tr>
                    <tr>
                        <td class="label">Số Tầng</td>
                        <td class="value">{so_tang} Tầng</td>
                    </tr>
                    <tr>
                        <td class="label">Mặt Tiền</td>
                        <td class="value">{mat_tien} m</td>
                    </tr>
                    <tr>
                        <td class="label">Chiều Dài</td>
                        <td class="value">{chieu_dai} m</td>
                    </tr>
                    <tr>
                        <td class="label">Hướng</td>
                        <td class="value">{huong}</td>
                    </tr>
                    <tr>
                        <td class="label">Hẻm trước nhà</td>
                        <td class="value">{duong_vao} m</td>
                    </tr>
                </table>
                
                <div class="section-title" style="margin-top: 24px;">Thông tin liên hệ</div>
                <table class="info-table">
                    <tr>
                        <td class="label">Chủ nhà</td>
                        <td class="value">{ten_chu}</td>
                    </tr>
                    <tr>
                        <td class="label">SĐT Chủ</td>
                        <td class="value" style="color: var(--success-color);">{sdt_chu}</td>
                    </tr>
                    <tr>
                        <td class="label">Đầu chủ</td>
                        <td class="value">{ten_dc}</td>
                    </tr>
                    <tr>
                        <td class="label">SĐT Đầu chủ</td>
                        <td class="value">{sdt_dc}</td>
                    </tr>
                </table>
                
                <a href="{link_goc}" target="_blank" class="btn-link">Mở Link Gốc Nguồn Tin</a>
            </div>
        </div>
        
        <!-- IMAGES -->
        <div class="card" style="margin-bottom: 40px;">
            {images_html if (images["diagram"] or images["facade"] or images["alley"] or images["interior"]) else '<p style="text-align: center; color: var(--text-muted); padding: 40px 0;">Không tìm thấy hình ảnh nào của căn nhà này trong SQLite.</p>'}
        </div>
    </div>
</body>
</html>
"""
    return html_content

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
