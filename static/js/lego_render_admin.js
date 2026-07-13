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

    const shortenOwnerName = (name) => {
      if (!name || name === 'None') return 'Chưa rõ';
      name = name.trim();
      const words = name.split(/\s+/);
      if (words.length <= 1) return name;
      const initials = words.slice(0, -1).map(w => w ? w[0].toUpperCase() + '.' : '').join(' ');
      return `${initials} ${words[words.length - 1]}`;
    };
    const displayListed = formatDate(jsonUi.createdAtSigned || '');
    const displayUpdated = formatDate(jsonUi.updatedAt || '');

    const area = parseFloat(p.dt_tren_so_custom) || parseFloat(p.raw_dt_tren_so) || 0;
    const price = parseFloat(p.gia) || 0;
    const donGia = (area > 0 && price > 0) ? (price * 1000 / area) : 0;
    const donGiaStr = donGia > 0 ? `${window.formatDonGia(donGia)}/m²` : '';
    
    const currentPriceHtml = `
      <div style="display: flex; align-items: center; gap: 4px; justify-content: flex-end;">
        ${donGiaStr ? `<span style="font-size: 11px; color: #57606f; font-weight: 700; background: #f1f2f6; padding: 2px 6px; border-radius: 4px; border: 1px solid #ced6e0;">${donGiaStr}</span>` : ''}
        <span style="background: rgba(39, 174, 96, 0.15); color: #27ae60; padding: 2px 6px; border-radius: 4px; font-size: 11.5px; font-weight: 800;">${p.gia} tỷ</span>
      </div>
    `;

    let priceHistoryHtml = '';
    
    const formatPriceMoc = (pr) => {
      const pVal = parseFloat(pr);
      if (isNaN(pVal) || pVal <= 0) return '';
      const dg = (area > 0) ? (pVal * 1000 / area) : 0;
      const dgStr = dg > 0 ? ` (${window.formatDonGia(dg)})` : '';
      return `${pVal} tỷ${dgStr}`;
    };

    if (jsonUi.history && Array.isArray(jsonUi.history)) {
      const priceChanges = jsonUi.history.filter(h => h.type === 'price');
      if (priceChanges.length > 0) {
        const priceMocs = [];
        priceMocs.push(priceChanges[0].old);
        priceChanges.forEach(h => {
          if (parseFloat(h.new) !== parseFloat(priceMocs[priceMocs.length - 1])) {
            priceMocs.push(h.new);
          }
        });
        
        if (priceMocs.length > 1) {
          const oldMocs = priceMocs.slice(0, -1);
          const parts = oldMocs.map(pr => {
            const formatted = formatPriceMoc(pr);
            return `<span style="text-decoration: line-through; color: #7f8c8d; font-weight: normal;">${formatted}</span>`;
          });
          
          priceHistoryHtml = parts.join(' <span style="color: #7f8c8d; font-weight: normal; margin: 0 2px;">➔</span> ');
        }
      }
    }

    const st = window.getHouseStatus ? window.getHouseStatus(p) : 'Đang bán';
    let badgeColor = '#27ae60';
    let stAbbr = st;
    if (st === 'Đang bán') {
      badgeColor = '#27ae60';
      stAbbr = 'Đg. Bán';
    } else if (st === 'Đã cọc') {
      badgeColor = '#e67e22';
      stAbbr = 'Đ.Cọc';
    } else if (st === 'Đã bán') {
      badgeColor = 'var(--red)';
      stAbbr = 'Đã bán';
    } else if (st === 'Ngừng bán') {
      badgeColor = '#7f8c8d';
      stAbbr = 'Ngừng bán';
    }
    
    const statusBadgeHtml = `<div class="status-badge-tag" style="background: ${badgeColor}; color: #fff; position: absolute; top: 8px; right: 8px; left: auto !important; font-size: 10px; font-weight: 800; padding: 2px 6px; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.15); z-index: 5;">${stAbbr}</div>`;

    const houseType = window.getHouseTypeDisplay ? window.getHouseTypeDisplay(p) : '';
    let houseTypeAbbr = houseType;
    if (houseType === 'Mặt tiền') houseTypeAbbr = 'M.Tiền';
    else if (houseType === 'Chung cư') houseTypeAbbr = 'CC';

    c.innerHTML = `
      <div class="crow">
        <div class="ibox" style="position: relative;">
          ${statusBadgeHtml}
          ${p.isFromPoolOnly ? (isOnAir ? '<div class="pool-badge-tag on-air" style="top: 8px; left: 8px !important; right: auto;">🟢 Đã lên sóng</div>' : '<div class="pool-badge-tag raw" style="top: 8px; left: 8px !important; right: auto;">⚪ Chưa lên sóng</div>') : ''}
          <img src="${thumb}" alt="${p.t}" loading="lazy" decoding="async" onload="this.parentElement.classList.add('is-loaded'); this.classList.add('loaded');">
          <input type="checkbox" class="card-sel" onclick="event.stopPropagation()" onchange="toggleSelect('${p.id}', this)" ${isSelected ? 'checked' : ''}>
          <button class="heart ${isFav ? 'on' : ''}" onclick="th('${favId}', this, event)">${isFav ? '♥' : '♡'}</button>
        </div>
        <div class="card-right">
          <div class="info">
            <div class="ititle" style="color: var(--red); font-weight: 850; font-size: 14.5px; line-height: 1.35; margin-bottom: 6px;">
              ${displayTitle}
            </div>
            <div style="font-size: 12px; margin-bottom: 4px; color: #2c3e50; font-weight: 600; display: flex; align-items: center; justify-content: space-between; gap: 4px;">
              <div style="display: flex; align-items: center; gap: 4px;">
                <span>📍</span> P.${p.phuong}, Q.${p.ql}
              </div>
              <span style="color: ${badgeColor}; font-weight: 800; white-space: nowrap;">● ${stAbbr}</span>
            </div>
            <div style="font-size: 11px; margin-bottom: 4px; color: #2c3e50; font-weight: 600; display: flex; align-items: center; justify-content: space-between; gap: 2px; width: 100%;">
              <div style="display: flex; align-items: center; gap: 2px; min-width: 0; flex: 1;">
                ${p.raw_link_fb ? `
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="11" height="11" fill="#1877f2" style="vertical-align: middle; flex-shrink: 0; margin-right: 1px;">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                  </svg>
                ` : '<span>👤</span>'}
                <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0;">
                  ${p.raw_link_fb ? `<a href="${p.raw_link_fb}" target="_blank" onclick="event.stopPropagation();" style="color: var(--blue); text-decoration: underline; font-weight: 600;">${shortenOwnerName(p.raw_ten_dau_chu)}</a>` : shortenOwnerName(p.raw_ten_dau_chu)}
                </span>
              </div>
              <div style="display: flex; align-items: center; gap: 2px; flex-shrink: 0; text-align: right; justify-content: flex-end; color: var(--red); font-weight: 700; font-size: 11px;">
                ${p.raw_dt_dau_chu ? `<a href="tel:${window.formatPhone(p.raw_dt_dau_chu)}" onclick="event.stopPropagation();" style="color: var(--red); text-decoration: underline; font-weight: 800;">${window.formatPhone(p.raw_dt_dau_chu)}</a>` : 'Chưa có SĐT'}
              </div>
            </div>
            ${(displayListed || displayUpdated) ? `
              <div style="font-size: 11px; margin-top: 4px; color: #7f8c8d; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; line-height: 1.35; font-weight: 500;">
                ${displayListed ? `<span>📅 ${displayListed}</span>` : ''}
                ${(displayListed && displayUpdated) ? `<span style="opacity: 0.5;">·</span>` : ''}
                ${displayUpdated ? `<span>🔄 ${displayUpdated}</span>` : ''}
              </div>
            ` : ''}
            ${priceHistoryHtml ? `
              <div style="font-size: 11px; margin-top: 4px; color: #7f8c8d; font-weight: 600; display: flex; align-items: center; gap: 4px; flex-wrap: wrap; text-align: left; justify-content: flex-start; width: 100%;">
                <span>🏷️</span> ${priceHistoryHtml}
              </div>
            ` : ''}
          </div>
          <div class="cfoot" style="margin-top: 6px; display: flex; align-items: center; justify-content: space-between; width: 100%;">
            ${activeCollectionName ? `<button class="remove-from-col-btn" onclick="removeFromCol('${p.id}', '${activeCollectionName}', event)">✕ Bỏ</button>` : ''}
            <div style="font-size: 12px; font-weight: 700; color: #2c3e50; display: flex; align-items: center; justify-content: space-between; width: 100%; flex-wrap: wrap; gap: 4px;">
              <span class="house-type-badge" style="font-size: 10.5px; background: #f1f2f6; color: #57606f; padding: 2px 6px; border-radius: 4px; font-weight: 700; border: 1px solid #ced6e0; white-space: nowrap;">${houseTypeAbbr}</span>
              ${currentPriceHtml}
            </div>
          </div>
        </div>
      </div>`;
      
    return c;
  }
};
