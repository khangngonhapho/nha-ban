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
    
    // Prioritize facadeImg from curated_config if available
    let facadeImg = '';
    if (p.curated_config && p.curated_config.images) {
      const found = p.curated_config.images.find(img => img.role === 'Mặt tiền' || img.role === 'facade');
      if (found) facadeImg = found.url;
    }
    
    const effectiveImgMatTien = (curatedListing && curatedListing.img_mat_tien) ? curatedListing.img_mat_tien : p.img_mat_tien;
    
    if (facadeImg) {
      thumbUrl = facadeImg;
    } else if (effectiveImgMatTien) {
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

    // Format ISO date string to DD/MM/YYYY
    const formatDate = (isoStr) => {
      if (!isoStr || isoStr === 'None') return '';
      try {
        const d = new Date(isoStr);
        if (isNaN(d.getTime())) return isoStr;
        const date = String(d.getDate()).padStart(2, '0');
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const year = d.getFullYear();
        return `${date}/${month}/${year}`;
      } catch (e) {
        return isoStr;
      }
    };

    const jsonUi = p.json_ui_parsed || {};
    const displayListed = formatDate(jsonUi.createdAtSigned || '');
    const displayUpdated = formatDate(jsonUi.updatedAt || '');

    const area = parseFloat(p.dt_tren_so_custom) || parseFloat(p.raw_dt_tren_so) || 0;
    const price = parseFloat(p.gia) || 0;
    const donGia = (area > 0 && price > 0) ? (price * 1000 / area) : 0;
    const donGiaText = donGia > 0 ? ` (${donGia.toFixed(1)}tr)` : '';

    let priceHistoryHtml = `<span style="background: rgba(39, 174, 96, 0.15); color: #27ae60; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 800;">${p.gia} tỷ${donGiaText}</span>`;
    if (jsonUi.history && Array.isArray(jsonUi.history)) {
      const priceChanges = jsonUi.history.filter(h => h.type === 'price');
      if (priceChanges.length > 0) {
        const lastChange = priceChanges[priceChanges.length - 1];
        const oldPrice = parseFloat(lastChange.old);
        const newPrice = parseFloat(lastChange.new);
        
        const formatGiabq = (price, a) => {
          if (!a || a <= 0) return '';
          return ` (${((price * 1000) / a).toFixed(1)}tr)`;
        };
        
        const oldGiabqStr = formatGiabq(oldPrice, area);
        const newGiabqStr = formatGiabq(newPrice, area);
        
        priceHistoryHtml = `
          <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 4px; font-size: 11.5px;">
            <span style="text-decoration: line-through; color: #7f8c8d; background: #f2f2f2; padding: 2px 6px; border-radius: 4px;">
              ${oldPrice} tỷ${oldGiabqStr}
            </span>
            <span style="color: #27ae60; font-weight: 800;">➔</span>
            <span style="background: rgba(39, 174, 96, 0.15); color: #27ae60; padding: 2px 6px; border-radius: 4px; font-weight: 800;">
              ${newPrice} tỷ${newGiabqStr}
            </span>
          </div>
        `;
      }
    }

    const st = window.getHouseStatus ? window.getHouseStatus(p) : 'Đang bán';
    let statusBadgeHtml = '';
    if (st !== 'Đang bán') {
      let badgeColor = '#27ae60';
      if (st === 'Đã cọc') badgeColor = '#e67e22';
      else if (st === 'Đã bán') badgeColor = 'var(--red)';
      else if (st === 'Ngừng bán') badgeColor = '#7f8c8d';
      statusBadgeHtml = `<div class="status-badge-tag" style="background: ${badgeColor}; color: #fff; position: absolute; top: 8px; left: 8px; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.15); z-index: 5;">${st}</div>`;
    }

    c.innerHTML = `
      <div class="crow">
        <div class="ibox" style="position: relative;">
          ${statusBadgeHtml}
          ${p.isFromPoolOnly ? (isOnAir ? '<div class="pool-badge-tag on-air" style="top: 8px; right: 8px; left: auto;">🟢 Đã lên sóng</div>' : '<div class="pool-badge-tag raw" style="top: 8px; right: 8px; left: auto;">⚪ Chưa lên sóng</div>') : ''}
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
            ${(displayListed || displayUpdated) ? `
              <div style="font-size: 11px; margin-top: 4px; color: #7f8c8d; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; line-height: 1.35; font-weight: 500;">
                ${displayListed ? `<span>📅 ${displayListed}</span>` : ''}
                ${(displayListed && displayUpdated) ? `<span style="opacity: 0.5;">·</span>` : ''}
                ${displayUpdated ? `<span>🔄 ${displayUpdated}</span>` : ''}
              </div>
            ` : ''}
          </div>
          <div class="cfoot" style="margin-top: 6px;">
            ${activeCollectionName ? `<button class="remove-from-col-btn" onclick="removeFromCol('${p.id}', '${activeCollectionName}', event)">✕ Bỏ</button>` : ''}
            <div style="font-size: 12px; font-weight: 700; color: #2c3e50; display: flex; align-items: center; gap: 6px;">
              ${priceHistoryHtml}
            </div>
          </div>
        </div>
      </div>`;
      
    return c;
  }
};
