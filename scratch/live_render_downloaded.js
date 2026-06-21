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
    const imgUrls = (p.imgs || []).filter(u => !u.includes('facebook.com') && !u.includes('fb.watch') && !u.includes('fb.gg'));
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

    c.innerHTML = `
      <div class="crow">
        <div class="ibox">
          ${p.isFromPoolOnly ? '<div class="pool-badge-tag">📦 Pool</div>' : ''}
          <img src="${thumb}" alt="${p.t}" loading="lazy" decoding="async" onload="this.parentElement.classList.add('is-loaded'); this.classList.add('loaded');">
          <button class="heart ${isFav ? 'on' : ''}" onclick="th('${favId}', this, event)">${isFav ? '♥' : '♡'}</button>
        </div>
        <div class="card-right">
          <div class="info">
            <div class="ititle">${p.t || p.raw_tieu_de_public || 'Chưa có tiêu đề public.'}</div>
            <div class="chips">
              <span class="chip">📐 ${p.dt}m²</span>
              <span class="chip">🏠 ${p.tang} tầng</span>${p.so_pn && p.so_pn !== '-' ? `
              <span class="chip">🛏️ ${p.so_pn} PN</span>` : ''}${p.danh_gia === 'Hàng Ngon' ? '<span class="chip" style="color:#27ae60;font-size:14px;padding:2px 4px;">▶</span>' : p.danh_gia === 'Hàng Lỗi' ? '<span class="chip" style="color:var(--red);font-size:13px;padding:2px 4px;">⏸</span>' : ''}
            </div>
            <div class="pr-loc">
              <div class="pr"><span class="pv">${p.gia} tỷ</span></div>
              <div class="loc">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>
                P.${p.phuong}, Q.${p.ql}
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
