# -*- coding: utf-8 -*-
"""
Header component for BDS KhangNgo offline viewer.
"""

def render_header(listing, address, table_name):
    ma_hang = listing.get("Ma_Hang") or listing.get("M__H_ng") or "N/A"
    system_id = listing.get("System_ID") or "N/A"
    
    html = f"""
        <div class="header">
            <div class="header-title">
                <h1>{ma_hang} / {system_id}</h1>
                <p>Địa chỉ gốc: {address}</p>
            </div>
            <div>
                <span class="tag-status">Chế độ: {str(table_name).upper()}</span>
            </div>
        </div>
    """
    return html
