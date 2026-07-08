# -*- coding: utf-8 -*-
"""
Detail view layout coordinator for BDS KhangNgo offline viewer.
Assembles header, styles, specs, contact info, criteria, and images into the final HTML document.
"""

from templates.components.styles import BASE_CSS
from templates.components.header import render_header
from templates.components.criteria_grid import render_criteria_grid
from templates.components.image_grid import render_image_grid
from templates.components.specs_table import render_specs_table, render_contact_table

def render_detail_view(listing, images, table_name):
    # Trích xuất các trường thông tin cơ bản
    ma_hang = listing.get("Ma_Hang") or listing.get("M__H_ng") or "N/A"
    
    so_nha = listing.get("Ngo_So_nha") or listing.get("Ng__S__nh_") or ""
    duong = listing.get("Duong") or listing.get("___ng") or ""
    phuong = listing.get("Phuong") or listing.get("Ph__ng") or ""
    quan = listing.get("Quan") or listing.get("Qu_n") or ""
    address = f"{so_nha} {duong}, Phường {phuong}, {quan}".strip(", ")
    
    mo_ta = listing.get("Mo_ta_chi_tiet") or listing.get("M_t__chi_ti?t") or ""
    noi_dung = listing.get("Noi_dung_chinh") or listing.get("N?i_dung_chnh") or ""
    link_goc = listing.get("Link_Goc") or listing.get("Link_G?c") or "#"
    
    header_html = render_header(listing, address, table_name)
    criteria_html = render_criteria_grid(listing)
    images_html = render_image_grid(images)
    specs_html = render_specs_table(listing)
    contact_html = render_contact_table(listing)
    
    # HTML Layout
    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chi tiết căn nhà - {ma_hang}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>{BASE_CSS}</style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        {header_html}
        
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
                {specs_html}
                {contact_html}
                <a href="{link_goc}" target="_blank" class="btn-link">Mở Link Gốc Nguồn Tin</a>
            </div>
        </div>
        
        <!-- IMAGES -->
        <div class="card" style="margin-bottom: 40px;">
            {images_html if (images.get("diagram") or images.get("facade") or images.get("alley") or images.get("interior") or images.get("cover")) else '<p style="text-align: center; color: var(--text-muted); padding: 40px 0;">Không tìm thấy hình ảnh nào của căn nhà này trong SQLite.</p>'}
        </div>
    </div>
</body>
</html>
"""
    return html_content
