# -*- coding: utf-8 -*-
"""
Specs and Contact tables component for BDS KhangNgo offline viewer.
"""

def render_specs_table(listing):
    gia = listing.get("Gia_chao") or listing.get("Gi__ch_o") or "N/A"
    dt_thuc = listing.get("DT_Thuc_te") or listing.get("DT_Th?c_t?") or "N/A"
    dt_so = listing.get("DT_Tren_so") or listing.get("DT_Trn_s?") or "N/A"
    so_tang = listing.get("So_Tang") or listing.get("S__T?ng") or "N/A"
    mat_tien = listing.get("Mat_Tien") or listing.get("M?t_Ti?n") or "N/A"
    chieu_dai = listing.get("Chieu_dai") or "N/A"
    huong = listing.get("Huong") or listing.get("Hu_ng") or "N/A"
    duong_vao = listing.get("minimumRoadWidth") or listing.get("___ng_tr__c_nh___m_") or "N/A"
    
    html = f"""
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
    """
    return html

def render_contact_table(listing):
    ten_chu = listing.get("Ten_Chu_Nha") or listing.get("Tn_Ch__Nh_") or "N/A"
    sdt_chu = listing.get("Dien_thoai_1") or listing.get("Đi?n_tho?i_1") or "N/A"
    ten_dc = listing.get("Ten_Dau_Chu") or listing.get("Tn_Đ?u_Ch__H?p_đ?ng_") or "N/A"
    sdt_dc = listing.get("Dien_thoai_Dau_Chu") or listing.get("Đi?n_tho?i_Đ?u_Ch_") or "N/A"
    
    html = f"""
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
    """
    return html
