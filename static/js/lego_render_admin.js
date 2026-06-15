/**
 * Lego Admin Render Engine Module
 * Handles admin-facing property card generation with private/curated fields.
 */

window.LegoRenderAdmin = {
  /**
   * Creates a card DOM element for authenticated admin view
   * @param {Object} p - The property listing data object
   * @param {Object} curatedListing - The matching curated listing from DATA
   * @param {Object} options - Rendering configuration options
   * @param {Set} options.favs - Set of favorite property IDs
   * @param {Set} options.SELECTED_IDS - Set of currently selected card IDs
   * @param {string} [options.activeCollectionName] - Current active collection name
   * @returns {HTMLElement} The card element
   */
  createCard(p, curatedListing, options = {}) {
    const favs = options.favs || new Set();
    const SELECTED_IDS = options.SELECTED_IDS || new Set();
    const activeCollectionName = options.activeCollectionName || '';
    
    const imgUrls = (p.imgs || []).filter(u => !u.includes('facebook.com') && !u.includes('fb.watch') && !u.includes('fb.gg'));
    const cleanImgUrls = imgUrls.filter(u => !(window.isListingSodoUrl && window.isListingSodoUrl(u, p)));
    
    // Choose cover/thumbnail URL prioritizing image mat tien
    let thumbUrl = '';
    const effectiveImgMatTien = (curatedListing && curatedListing.img_mat_tien) ? curatedListing.img_mat_tien : p.img_mat_tien;
    if (effectiveImgMatTien) {
      thumbUrl = effectiveImgMatTien;
    } else {
      thumbUrl = cleanImgUrls[0] || imgUrls[0];
    }
    const thumb = thumbUrl ? window.fixImgUrl(thumbUrl, 'w400') : 'https://via.placeholder.com/300x200?text=No+Photo';
    
    const isOnAir = !!curatedListing;

    const c = document.createElement('div');
    c.className = p.isFromPoolOnly ? 'card is-pool-card' : 'card';
    c.dataset.pid = String(p.id);
    
    // Setup admin click handler (if raw and not on air, open pool detail screen)
    c.setAttribute('onclick', (p.isFromPoolOnly && !isOnAir) ? `openPoolS('${p.system_id}')` : `openS('${curatedListing ? curatedListing.id : p.id}')`);

    const favId = p.system_id ? String(p.system_id) : String(p.id);
    const isFav = favs.has(favId);
    
    const adminTitle = window.generateAdminTitleFromNộiDungChinh(p);
    const displayTitle = String(adminTitle).includes(p.gia + ' tỷ') ? adminTitle : adminTitle + ' ' + p.gia + ' tỷ';
    const isSelected = SELECTED_IDS.has(String(p.id));

    c.innerHTML = `
      <div class="crow">
        <div class="ibox">
          ${p.isFromPoolOnly ? (isOnAir ? '<div class="pool-badge-tag on-air">🟢 Đã lên sóng</div>' : '<div class="pool-badge-tag raw">⚪ Chưa lên sóng</div>') : ''}
          <img src="${thumb}" alt="${p.t}" loading="lazy" decoding="async" onload="this.parentElement.classList.add('is-loaded'); this.classList.add('loaded');">
          <input type="checkbox" class="card-sel" onclick="event.stopPropagation()" onchange="toggleSelect('${p.id}', this)" ${isSelected ? 'checked' : ''}>
          <button class="heart ${isFav ? 'on' : ''}" onclick="th('${favId}', this, event)">${isFav ? '♥' : '♡'}</button>
        </div>
        <div class="card-right">
          <div class="info">
            <div class="ititle" style="color: var(--red); font-weight: 850; font-size: 14.5px; line-height: 1.35; margin-bottom: 6px;">
              ${displayTitle}
            </div>
            <div style="font-size: 12px; margin-bottom: 4px; color: #2c3e50; font-weight: 600; display: flex; align-items: center; gap: 4px;">
              <span>📍</span> P.${p.phuong}, Q.${p.ql}
            </div>
            <div style="font-size: 12px; margin-bottom: 4px; color: #2c3e50; font-weight: 600; display: flex; align-items: center; gap: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
              <span>👤</span> ${p.raw_ten_dau_chu || 'Chưa rõ đầu chủ'}
            </div>
            <div style="font-size: 12.5px; color: var(--red); font-weight: 700; display: flex; align-items: center; gap: 4px;">
              <span>📞</span> 
              ${p.raw_dt_dau_chu ? `<a href="tel:${window.formatPhone(p.raw_dt_dau_chu)}" onclick="event.stopPropagation();" style="color: var(--red); text-decoration: underline; font-weight: 800;">${window.formatPhone(p.raw_dt_dau_chu)}</a>` : 'Chưa có SĐT'}
            </div>
          </div>
          <div class="cfoot" style="margin-top: 6px;">
            ${activeCollectionName ? `<button class="remove-from-col-btn" onclick="removeFromCol('${p.id}', '${activeCollectionName}', event)">✕ Bỏ</button>` : ''}
            <div style="font-size: 12px; font-weight: 700; color: #2c3e50; display: flex; align-items: center; gap: 6px;">
              <span style="background: rgba(39, 174, 96, 0.15); color: #27ae60; padding: 2px 6px; border-radius: 4px; font-size: 11px;">${p.gia} tỷ</span>
            </div>
          </div>
        </div>
      </div>`;
      
    return c;
  }
};
