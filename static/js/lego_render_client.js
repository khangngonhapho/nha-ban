/**
 * Lego Client Render Engine Module
 * Handles client-facing property card generation using DocumentFragment and DOM elements.
 */

window.LegoRenderClient = {
  /**
   * Creates a card DOM element for public client view
   * @param {Object} p - The property listing data object
   * @param {Object} options - Rendering configuration options
   * @param {Set} options.favs - Set of favorite property IDs
   * @param {string} [options.activeCollectionName] - Current active collection name
   * @returns {HTMLElement} The card element
   */
  createCard(p, options = {}) {
    const favs = options.favs || new Set();
    const activeCollectionName = options.activeCollectionName || '';
    
    // Filter out Facebook and sodo images to get public cover
    const baseImgs = (p.images_public && p.images_public.length > 0) ? p.images_public : (p.imgs || []);
    const imgUrls = baseImgs.filter(u => !u.includes('facebook.com') && !u.includes('fb.watch') && !u.includes('fb.gg'));
    const cleanImgUrls = imgUrls.filter(u => !(window.isListingSodoUrl && window.isListingSodoUrl(u, p)));
    const thumbUrl = cleanImgUrls[0] || imgUrls[0];
    const thumb = thumbUrl ? window.fixImgUrl(thumbUrl, 'w400') : 'https://via.placeholder.com/300x200?text=No+Photo';

    const c = document.createElement('div');
    c.className = p.isFromPoolOnly ? 'card is-pool-card' : 'card';
    c.dataset.pid = String(p.id);
    
    // Setup client click handler
    c.setAttribute('onclick', p.isFromPoolOnly ? `openPoolS('${p.system_id}')` : `openS('${p.id}')`);

    const favId = p.system_id ? String(p.system_id) : String(p.id);
    const isFav = favs.has(favId);

    const area = parseFloat(p.dt_tren_so_custom) || parseFloat(p.raw_dt_tren_so) || 0;
    const price = parseFloat(p.gia) || 0;
    const donGia = (area > 0 && price > 0) ? (price * 1000 / area) : 0;
    const donGiaText = donGia > 0 ? ` (${donGia.toFixed(1)}tr)` : '';

    const st = window.getHouseStatus ? window.getHouseStatus(p) : 'Đang bán';
    let badgeColor = '#27ae60';
    if (st === 'Đã cọc') badgeColor = '#e67e22';
    else if (st === 'Đã bán') badgeColor = 'var(--red)';
    else if (st === 'Ngừng bán') badgeColor = '#7f8c8d';
    
    const statusBadgeHtml = `<div class="status-badge-tag" style="background: ${badgeColor}; color: #fff; position: absolute; top: 8px; right: 8px; left: auto !important; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.15); z-index: 5;">${st}</div>`;

    c.innerHTML = `
      <div class="crow">
        <div class="ibox" style="position: relative;">
          ${p.isFromPoolOnly ? '<div class="pool-badge-tag" style="top: 8px; left: 8px !important; right: auto;">📦 Pool</div>' : ''}
          <img src="${thumb}" alt="${p.t}" loading="lazy" decoding="async" onload="this.parentElement.classList.add('is-loaded'); this.classList.add('loaded');">
          <button class="heart ${isFav ? 'on' : ''}" onclick="th('${favId}', this, event)">${isFav ? '♥' : '♡'}</button>
        </div>
        <div class="card-right">
          <div class="info">
            <div class="ititle">${p.t || p.raw_tieu_de_public || 'Chưa có tiêu đề public.'}</div>
            <div class="chips">
              <span class="chip">📐 ${p.dt}m²</span>
              <span class="chip">🏠 ${p.tang} tầng</span>${p.so_pn && p.so_pn !== '-' ? `
              <span class="chip">🛏️ ${p.so_pn} PN</span>` : ''}
              ${p.danh_gia === 'Hàng Ngon' ? '<span class="chip" style="color:#27ae60;font-size:14px;padding:2px 4px;">▶</span>' : p.danh_gia === 'Hàng Lỗi' ? '<span class="chip" style="color:var(--red);font-size:13px;padding:2px 4px;">⏸</span>' : ''}
            </div>
            <div class="loc" style="font-size: 11.5px; color: var(--sub); display: flex; align-items: center; gap: 4px; margin-top: 4px; margin-bottom: 6px;">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>
              P.${p.phuong}, Q.${p.ql}
            </div>
            <div class="pr-loc" style="display: flex; align-items: center; justify-content: space-between; width: 100%; margin-top: auto;">
              <div class="pr" style="display: flex; align-items: center; justify-content: space-between; width: 100%; flex-wrap: wrap; gap: 4px;">
                <span class="house-type-badge" style="font-size: 10.5px; background: #f1f2f6; color: #57606f; padding: 2px 6px; border-radius: 4px; font-weight: 700; border: 1px solid #ced6e0; white-space: nowrap;">${window.getHouseTypeDisplay(p)}</span>
                <div style="display: flex; align-items: center; gap: 4px;">
                  ${donGia > 0 ? `<span style="font-size: 11px; color: #57606f; font-weight: 700; background: #f1f2f6; padding: 2px 6px; border-radius: 4px; border: 1px solid #ced6e0;">${donGia.toFixed(1)}tr/m²</span>` : ''}
                  <span class="pv" style="color: #27ae60; font-weight: 800; font-size: 14.5px; background: rgba(39, 174, 96, 0.15); padding: 2px 6px; border-radius: 4px; display: inline-block;">${p.gia} tỷ</span>
                </div>
              </div>
            </div>
          </div>
          <div class="cfoot">
            ${activeCollectionName ? `<button class="remove-from-col-btn" onclick="removeFromCol('${p.id}', '${activeCollectionName}', event)">✕ Bỏ</button>` : ''}
            <div class="id-large">#${p.id}</div>
          </div>
        </div>
      </div>`;
      
    return c;
  }
};
