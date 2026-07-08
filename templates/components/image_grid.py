# -*- coding: utf-8 -*-
"""
Image grid component for BDS KhangNgo offline viewer.
"""

def render_image_grid(images):
    images_html = ""
    
    # 1. Ảnh sơ đồ
    if images.get("diagram"):
        images_html += '<div class="section-title">Sơ đồ thửa đất / Bản vẽ</div><div class="image-grid diagram-grid">'
        for img_url in images["diagram"]:
            if img_url:
                images_html += f'<div class="image-wrapper"><img src="{img_url}" alt="Sơ đồ thửa đất" onerror="this.src=\'https://placehold.co/400x300?text=Loi+anh+so+do\'"></div>'
        images_html += '</div>'
        
    # 2. Ảnh mặt tiền
    if images.get("facade"):
        images_html += '<div class="section-title">Hình ảnh Mặt Tiền</div><div class="image-grid facade-grid">'
        for img_url in images["facade"]:
            if img_url:
                images_html += f'<div class="image-wrapper"><img src="{img_url}" alt="Ảnh mặt tiền" onerror="this.src=\'https://placehold.co/400x300?text=Loi+anh+mat+tien\'"></div>'
        images_html += '</div>'

    # 3. Ảnh hẻm
    if images.get("alley"):
        images_html += '<div class="section-title">Hình ảnh Hẻm trước nhà</div><div class="image-grid alley-grid">'
        for img_url in images["alley"]:
            if img_url:
                images_html += f'<div class="image-wrapper"><img src="{img_url}" alt="Ảnh hẻm" onerror="this.src=\'https://placehold.co/400x300?text=Loi+anh+hem\'"></div>'
        images_html += '</div>'

    # 4. Ảnh nội thất / Ảnh sản phẩm khác
    interiors = images.get("interior") or []
    covers = images.get("cover") or []
    all_interiors = interiors + covers
    if all_interiors:
        images_html += '<div class="section-title">Hình ảnh Nội thất / Chi tiết</div><div class="image-grid interior-grid">'
        for img_url in all_interiors:
            if img_url:
                images_html += f'<div class="image-wrapper"><img src="{img_url}" alt="Ảnh nội thất" onerror="this.src=\'https://placehold.co/400x300?text=Loi+hinh+anh\'"></div>'
        images_html += '</div>'
        
    return images_html
