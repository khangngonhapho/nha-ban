// Lego Frontend - Admin Curation & Detail View Module
// US-094F: Cô lập Module Chi tiết, Preview & Curation dành riêng cho Admin

(function() {
  'use strict';

  // Export module LegoDetailAdmin
  window.LegoDetailAdmin = {
    render: render
  };

  
  function render(p, sbody, autoExpandPreview = false) {
    const targetMatTien = p.img_mat_tien || (p.pool_row_data ? p.pool_row_data[29] : '') || '';
    const normMatTien = window.normalizeImgUrl ? window.normalizeImgUrl(targetMatTien) : '';
    const isFacadeUrl = (url) => {
      if (!url) return false;
      const norm = window.normalizeImgUrl ? window.normalizeImgUrl(url) : '';
      return norm !== '' && norm === normMatTien;
    };

    const cleanRawNoiDungChinh = (text) => {
      if (!text) return '';
      const keyword = 'nguồn';
      const idx = text.toLowerCase().indexOf(keyword);
      if (idx !== -1) {
        return text.substring(0, idx).trim();
      }
      return text.trim();
    };
    const cleanedNoiDungChinh = cleanRawNoiDungChinh(p.raw_noi_dung_chinh);

    const extractSource = (text) => {
      if (!text) return 'Đầu chủ';
      const lower = text.toLowerCase();
      if (lower.includes('nguồn đối tác') || lower.includes('nguon doi tac') || lower.includes('nguon i tc') || lower.includes('nguồn đt') || lower.includes('nguon dt')) {
        return 'Đối tác';
      }
      if (lower.includes('nguồn đầu chủ') || lower.includes('nguon dau chu') || lower.includes('nguon u ch')) {
        return 'Đầu chủ';
      }
      const match = text.match(/nguồn\s+([a-zàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ\s]+)/i);
      if (match) return match[1].trim();
      const matchNguon = text.match(/nguon\s+([A-Za-z\s]+)/i);
      if (matchNguon) return matchNguon[1].trim();
      return 'Đầu chủ';
    };

    const extractCommission = (p) => {
      if (typeof window.extractCommission === 'function') {
        return window.extractCommission(p);
      }
      return '-';
    };

    const formatRawDescription = (text) => {
      if (typeof window.formatRawDescription === 'function') {
        return window.formatRawDescription(text);
      }
      return text || '';
    };

    const renderImageEditorWidget = (p) => {
      if (typeof window.renderImageEditorWidget === 'function') {
        return window.renderImageEditorWidget(p);
      }
      return '';
    };

    // RENDER HTML TEMPLATE
    sbody.innerHTML = `          <!-- QUICK LINK COPY BAR (US-049) -->
          <div class="admin-quick-link-bar" style="margin-bottom: 16px; display: flex; justify-content: flex-end; gap: 8px;">
            <button type="button" onclick="downloadAllListingImages('${p.id || p.system_id}')" style="background: #27ae60; color: #fff; border: none; padding: 7px 14px; border-radius: 16px; font-size: 11px; font-weight: 850; cursor: pointer; font-family: inherit; transition: all 0.2s; box-shadow: 0 4px 10px rgba(39, 174, 96, 0.15);" onmouseover="this.style.transform='translateY(-1px)'" onmouseout="this.style.transform='none'">
              📥 Tải toàn bộ ảnh
            </button>
            <button type="button" onclick="copyQuickClientLink('${p.system_id}')" style="background: var(--gold); color: #1c1c1e; border: none; padding: 7px 14px; border-radius: 16px; font-size: 11px; font-weight: 850; cursor: pointer; font-family: inherit; transition: all 0.2s; box-shadow: 0 4px 10px rgba(255, 191, 36, 0.15);" onmouseover="this.style.transform='translateY(-1px)'" onmouseout="this.style.transform='none'">
              Copy link nhanh
            </button>
          </div>

          <!-- THÔNG TIN THÔ - POOL (HIỂN THỊ PHẲNG TRỰC TIẾP) -->
          <div id="accPool" style="margin-bottom: 24px; padding: 0 4px;">
            <!-- Carousels -->
            <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px;">
              <div>
                <div class="admin-raw-title" style="margin-bottom: 6px;">Bất động sản</div>
                <div id="carouselNha" style="position: relative;">
                  <div class="admin-scroll-carousel"></div>
                  <div class="admin-carousel-dots"></div>
                </div>
              </div>
              ${(p.raw_sodo1 || p.raw_sodo2) ? `
              <div>
                <div class="admin-raw-title" style="margin-bottom: 6px; margin-top: 8px;">Sổ thửa đất</div>
                <div id="carouselSo" style="position: relative;">
                  <div class="admin-scroll-carousel"></div>
                  <div class="admin-carousel-dots"></div>
                </div>
              </div>
              ` : ''}
            </div>

            <!-- Mô tả chi tiết (gộp, không tiêu đề) -->
            <div class="admin-mota-box red-text" style="margin-top:14px; margin-bottom:8px; font-size:12px; white-space:normal;">${(cleanedNoiDungChinh || 'Chưa có nội dung chính.').replace(/\r/g,'').replace(/\n/g,' ').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</div>
            <div class="admin-mota-box black-text" id="adminMotaGocBox" style="margin-bottom:14px; font-size:12px;">${formatRawDescription(p.raw_mo_ta_chi_tiet || p.m) || 'Chưa có mô tả chi tiết.'}</div>

            <!-- Technical Specs Dotted Grid -->
            <div class="admin-raw-section">
              <div class="admin-raw-title">Thông tin</div>
              <div class="admin-raw-grid">
                <div class="admin-raw-cell">
                  <span class="label">Diện tích thực tế:</span>
                  <span class="value dotted">${p.raw_dt_thuc_te || p.dt || '-'} m²</span>
                </div>
                <div class="admin-raw-cell">
                  <span class="label">Diện tích trên sổ:</span>
                  <span class="value dotted">${p.raw_dt_tren_so || p.dt || '-'} m²</span>
                </div>
                <div class="admin-raw-cell">
                  <span class="label">Chiều ngang:</span>
                  <span class="value dotted">${p.raw_mat_tien || p.mat || '-'} m</span>
                </div>
                <div class="admin-raw-cell">
                  <span class="label">Chiều dài:</span>
                  <span class="value dotted">${p.dai_nha || '-'} m</span>
                </div>
                <div class="admin-raw-cell">
                  <span class="label">Đường trước nhà:</span>
                  <span class="value dotted">${p.raw_duong_truoc_nha || p.duong_truoc_nha || '-'} m</span>
                </div>
                <div class="admin-raw-cell">
                  <span class="label">Số tầng:</span>
                  <span class="value dotted">${p.raw_so_tang || p.tang || '-'} tầng</span>
                </div>
                <div class="admin-raw-cell">
                  <span class="label">Số phòng ngủ:</span>
                  <span class="value dotted">${p.raw_so_pn || p.so_pn || '-'} PN</span>
                </div>
                <div class="admin-raw-cell">
                  <span class="label">Số WC:</span>
                  <span class="value dotted">${p.raw_so_wc || '-'} WC</span>
                </div>
                <div class="admin-raw-cell">
                  <span class="label">Giá chào:</span>
                  <span class="value dotted" style="color:var(--red); font-weight:800;">${p.gia || '-'} tỷ</span>
                </div>
                <div class="admin-raw-cell">
                  <span class="label">Trích thưởng:</span>
                  <span class="value dotted" style="color:#27ae60; font-weight:800;">${extractCommission(p)}</span>
                </div>
              </div>
            </div>

            <div class="admin-raw-section" style="margin-top: 14px;">
              <div class="admin-raw-title">Thông tin nguồn</div>
              <div class="admin-raw-source">
                <div style="display:flex; justify-content:space-between; margin-bottom: 4px;">
                  <span style="color:#57606f;">Nguồn:</span>
                  <span style="font-weight:700;">${extractSource(p.raw_noi_dung_chinh)}</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                  <span style="color:#57606f;">Link Facebook:</span>
                  <span>
                    ${p.raw_link_fb ? `<a href="${p.raw_link_fb}" target="_blank" class="dotted-val" style="color:var(--blue);">Xem FB Đầu Chủ ↗</a>` : '-'}
                  </span>
                </div>
              </div>
            </div>

            <div class="admin-raw-section" style="margin-top: 14px;">
              <div class="admin-raw-title">Thông tin đầu chủ</div>
              <div class="admin-raw-source">
                <div style="display:flex; justify-content:space-between; margin-bottom: 4px;">
                  <span style="color:#57606f;">Tên đầu chủ:</span>
                  <span style="font-weight:700;">${p.raw_ten_dau_chu || '-'}</span>
                </div>
                <div style="display:flex; justify-content:space-between;">
                  <span style="color:#57606f;">SĐT đầu chủ:</span>
                  <span>
                    ${p.raw_dt_dau_chu ? `<a href="tel:${formatPhone(p.raw_dt_dau_chu)}" class="dotted-val" style="color:var(--blue); font-weight:700;">${formatPhone(p.raw_dt_dau_chu)}</a>` : '-'}
                  </span>
                </div>
              </div>
            </div>

            <!-- Google Maps Embed -->
            <div class="admin-raw-title" style="margin-top:14px;">Bản đồ thực địa</div>
            <div class="admin-map-container"></div>
          </div>

          <div class="admin-accordion">
            <!-- ACCORDION 2: BIÊN TẬP CUSTOM - SOURCE -->
            <div class="accordion-item" id="accSource">
              <div class="accordion-header is-red" onclick="toggleAdminAccordion(this)">
                <span>BIÊN TẬP</span>
                <span class="arrow">▶</span>
              </div>
              <div class="accordion-content">
                <form class="admin-edit-form" onsubmit="event.preventDefault()">
                  <div class="admin-edit-group">
                    <label for="editNote">Ghi chú riêng (Note - Chỉ Admin thấy):</label>
                    <textarea id="editNote" rows="3" placeholder="Nhập ghi chú riêng..." style="font-size: 10px; font-weight: 500; font-family: inherit; padding: 6px; line-height: 1.4;">${p.note || ''}</textarea>
                  </div>

                  <div class="admin-edit-group">
                    <label for="editMaKhangNgo">Mã Khang Ngô (ID):</label>
                    <input type="text" id="editMaKhangNgo" value="${p.isFromPoolOnly ? (generateMaKhangNgo(p.raw_so_nha, p.raw_ten_duong) || p.id) : p.id}" placeholder="Mã Khang Ngô..." style="font-weight: 700; color: var(--red);">
                  </div>

                  <div class="admin-edit-group">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                      <label for="editTieuDeBds" style="margin-bottom: 0;">Tiêu đề public (dưới 85 ký tự):</label>
                      ${p.isFromPoolOnly ? `<button type="button" id="btnAutoFillCuration" onclick="autoFillCurationDetails()" style="background: rgba(255, 191, 36, 0.15); color: var(--gold); border: 1px solid var(--gold); border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: 700; cursor: pointer;">⚡ Tự động điền</button>` : ''}
                    </div>
                    <textarea id="editTieuDeBds" rows="2" placeholder="Nhập tiêu đề BĐS ngắn gọn..." style="font-size: 10px; font-weight: 700; line-height: 1.4; font-family: inherit; padding: 6px; resize: vertical;">${p.isFromPoolOnly ? '' : ((p.original_row_data && (p.original_row_data[4] || p.original_row_data[39])) || p.raw_tieu_de_public || '')}</textarea>
                  </div>

                  <div class="admin-edit-group">
                    <label for="editMoTaBds">Mô tả public:</label>
                    <textarea id="editMoTaBds" rows="12" placeholder="Nhập mô tả công khai cho khách hàng..." style="font-size: 10px; font-weight: 500; line-height: 1.4; font-family: inherit; padding: 6px;">${p.isFromPoolOnly ? '' : (p.m || p.raw_mo_ta_public || '')}</textarea>
                  </div>

                  ${p.isFromPoolOnly ? `<div id="poolSaveNotice" style="margin-top: -6px; margin-bottom: 12px; font-size: 10px; color: #e74c3c; font-weight: 700; background: rgba(231,76,60,0.08); padding: 8px 12px; border-radius: 6px; border: 1px dashed rgba(231,76,60,0.3); line-height: 1.4; box-sizing: border-box; width: 100%;">⚠️ Nhập đầy đủ cả <b>Tiêu đề Public</b> và <b>Mô tả Public</b> (hoặc bấm Tự động điền) để kích hoạt nút Lên sóng ⚡</div>` : ''}

                  ${renderImageEditorWidget(p)}

                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="admin-edit-group">
                      <label for="editHuong">Hướng nhà:</label>
                      <select id="editHuong">
                        <option value="-">Chưa xác định</option>
                        <option value="Đông">Đông</option>
                        <option value="Tây">Tây</option>
                        <option value="Nam">Nam</option>
                        <option value="Bắc">Bắc</option>
                        <option value="Đông Nam">Đông Nam</option>
                        <option value="Đông Bắc">Đông Bắc</option>
                        <option value="Tây Nam">Tây Nam</option>
                        <option value="Tây Bắc">Tây Bắc</option>
                      </select>
                    </div>
                    
                    <div class="admin-edit-group">
                      <label for="editDuong">Đường trước nhà:</label>
                      <select id="editDuong">
                        <option value="-">Chưa xác định</option>
                        <option value="Hẻm ba gác">Hẻm ba gác</option>
                        <option value="Hẻm ô tô lý thuyết">Hẻm ô tô lý thuyết</option>
                        <option value="Hẻm ô tô">Hẻm ô tô</option>
                        <option value="Mặt tiền đường">Mặt tiền đường</option>
                      </select>
                    </div>
                  </div>

                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="admin-edit-group">
                      <label for="editDuongTruocNha">Đường trước nhà (m):</label>
                      <input type="number" step="0.1" id="editDuongTruocNha" value="${p.custom_rong_hem || p.raw_duong_truoc_nha || p.duong_truoc_nha || ''}" placeholder="Độ rộng hẻm (m)...">
                    </div>

                    <div class="admin-edit-group">
                      <label for="editDanhGia">Đánh giá:</label>
                      <select id="editDanhGia">
                        <option value="">Bình thường</option>
                        <option value="Hàng Ngon">💎 Ngon</option>
                        <option value="Hàng Lỗi">⚠️ Lỗi</option>
                      </select>
                    </div>
                  </div>

                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="admin-edit-group">
                      <label for="editTinhTrang">Tình trạng:</label>
                      <select id="editTinhTrang">
                        <option value="Bình thường">Bình thường</option>
                        <option value="Mới">Mới</option>
                        <option value="Nát">Nát</option>
                        <option value="Đã bán">Đã bán</option>
                        <option value="Ẩn">Ẩn</option>
                      </select>
                    </div>
                    <div></div>
                  </div>
                  
                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="admin-edit-group">
                      <label for="editSoPn">Số phòng ngủ:</label>
                      <input type="number" id="editSoPn" value="${p.so_pn !== '-' ? p.so_pn : ''}" placeholder="Số phòng...">
                    </div>

                    <div class="admin-edit-group">
                      <label for="editSoWc">Số WC:</label>
                      <input type="number" id="editSoWc" value="${(p.original_row_data && p.original_row_data[33] !== '-') ? p.original_row_data[33] : (p.raw_so_wc || '')}" placeholder="Số WC...">
                    </div>
                  </div>

                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 4px;">
                    <div class="admin-edit-group row-group">
                      <input type="checkbox" id="editNguTret" ${p.ngu_tang_tret === 'Có' ? 'checked' : ''}>
                      <label for="editNguTret" style="font-weight:700;">Có ngủ trệt</label>
                    </div>

                    <div class="admin-edit-group row-group">
                      <input type="checkbox" id="editChdv" ${p.chdv === 'Có' ? 'checked' : ''}>
                      <label for="editChdv" style="font-weight:700;">Có CHDV</label>
                    </div>
                  </div>
                </form>
              </div>
            </div>

            ${(p.id && !p.isFromPoolOnly) ? `
            <!-- ACCORDION 3: PREVIEW KHÁCH HÀNG -->
            <div class="accordion-item" id="accPreview">
              <div class="accordion-header is-red" onclick="toggleAdminAccordion(this)">
                <span>📄 PREVIEW KHÁCH HÀNG</span>
                <span class="arrow">▶</span>
              </div>
              <div class="accordion-content">
                <div class="preview-webview-container" style="position: relative; width: 100%; height: 600px; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; overflow: hidden; background: #1c1c1e; box-shadow: 0 4px 15px rgba(0,0,0,0.25);">
                  <iframe src="${window.location.origin}${window.location.pathname}?s=${p.system_id}&preview=true" style="width: 100%; height: 100%; border: none;"></iframe>
                </div>
              </div>
            </div>
            ` : ''}
          </div>`;

    // POST-RENDER INITIALIZATION
    if (isAdmin && (p.original_row_data || p.isFromPoolOnly)) {
        window.CURRENT_EDITING_LISTING = p;
        setTimeout(() => {
          const editHuong = document.getElementById('editHuong');
          if (editHuong) editHuong.value = p.huong || '-';

          const editDuong = document.getElementById('editDuong');
          if (editDuong) editDuong.value = p.duong_truoc_nha || '-';

          const editDuongTruocNha = document.getElementById('editDuongTruocNha');
          if (editDuongTruocNha) editDuongTruocNha.value = p.custom_rong_hem || p.raw_duong_truoc_nha || p.duong_truoc_nha || '';

          const editDanhGia = document.getElementById('editDanhGia');
          if (editDanhGia) editDanhGia.value = p.danh_gia || '';

          const editTinhTrang = document.getElementById('editTinhTrang');
          if (editTinhTrang) editTinhTrang.value = p.tinh_trang || 'Bình thường';

          const mapContainer = document.querySelector('.admin-map-container');
          if (mapContainer) {
            const fullAddress = `${p.raw_so_nha || ''} ${p.raw_ten_duong || ''}, Phường ${p.phuong || ''}, ${p.ql || ''}, Hồ Chí Minh`.trim();
            mapContainer.innerHTML = `<iframe width="100%" height="100%" frameborder="0" style="border:0;" src="https://maps.google.com/maps?q=${encodeURIComponent(fullAddress)}&t=&z=16&ie=UTF8&iwloc=&output=embed" allowfullscreen></iframe>`;
          }

          const sImgs = [];
          const s1 = p.pool_row_data ? p.pool_row_data[27] : p.raw_sodo1;
          const s2 = p.pool_row_data ? p.pool_row_data[28] : p.raw_sodo2;
          const s3 = p.pool_row_data ? p.pool_row_data[80] : p.raw_sodo3;
          const s4 = p.pool_row_data ? p.pool_row_data[81] : p.raw_sodo4;
          const s5 = p.pool_row_data ? p.pool_row_data[82] : p.raw_sodo5;
          if (s1) sImgs.push(s1);
          if (s2) sImgs.push(s2);
          if (s3) sImgs.push(s3);
          if (s4) sImgs.push(s4);
          if (s5) sImgs.push(s5);

          const sodoUrls = sImgs.map(url => normalizeImgUrl(url));
          const nImgs = (p.imgs || []).filter(url => {
            const norm = normalizeImgUrl(url);
            return norm !== '' && !sodoUrls.includes(norm) && !isFacadeUrl(url);
          });

          setupScrollCarousel('carouselNha', nImgs, false);
          setupScrollCarousel('carouselSo', sImgs, true);

          // Kiểm tra và cập nhật trạng thái hợp lệ của Curation Form (US-039.7)
          const editTieuDe = document.getElementById('editTieuDeBds');
          const editMoTa = document.getElementById('editMoTaBds');

          const validateCurationForm = () => {
            const tieuDeVal = (editTieuDe ? editTieuDe.value : '').trim();
            const moTaVal = (editMoTa ? editMoTa.value : '').trim();
            const isFilled = tieuDeVal.length > 0 && moTaVal.length > 0;
            const floatActions = document.getElementById('adminDetailFloatActions');

            if (p.isFromPoolOnly) {
              const savePoolBtn = document.getElementById('savePoolBtn');
              const poolSaveNotice = document.getElementById('poolSaveNotice');
              if (isFilled) {
                const accPreview = document.getElementById('accPreview');
                if (accPreview) {
                  accPreview.style.display = 'block';
                  accPreview.classList.add('expanded');
                  const content = accPreview.querySelector('.accordion-content');
                  if (content) content.style.display = 'block';
                  const arrow = accPreview.querySelector('.arrow');
                  if (arrow) arrow.textContent = '▼';
                }
                if (floatActions) floatActions.style.display = 'flex';
                if (savePoolBtn) savePoolBtn.style.setProperty('display', 'flex', 'important');

                if (poolSaveNotice) {
                  poolSaveNotice.style.color = '#27ae60';
                  poolSaveNotice.style.background = 'rgba(39,174,96,0.08)';
                  poolSaveNotice.style.borderColor = 'rgba(39,174,96,0.3)';
                  poolSaveNotice.innerHTML = '✅ Đã đủ điều kiện! Nút Lên sóng ⚡ đã sẵn sàng ở góc dưới bên phải.';
                }
              } else {
                if (floatActions) floatActions.style.display = 'none';
                if (savePoolBtn) savePoolBtn.style.setProperty('display', 'none', 'important');

                if (poolSaveNotice) {
                  poolSaveNotice.style.color = '#e74c3c';
                  poolSaveNotice.style.background = 'rgba(231,76,60,0.08)';
                  poolSaveNotice.style.borderColor = 'rgba(231,76,60,0.3)';
                  poolSaveNotice.innerHTML = '⚠️ Nhập đầy đủ cả <b>Tiêu đề Public</b> và <b>Mô tả Public</b> (hoặc bấm Tự động điền) để kích hoạt nút Lên sóng ⚡';
                }
              }
            } else {
              const accPreview = document.getElementById('accPreview');
              if (accPreview) accPreview.style.display = 'block';
              if (floatActions) floatActions.style.display = 'flex';
              const saveSourceBtn = document.getElementById('saveSourceBtn');
              if (saveSourceBtn) saveSourceBtn.style.setProperty('display', 'flex', 'important');
            }
          };
          window.validateCurationForm = validateCurationForm;

          if (editTieuDe && editMoTa) {
            editTieuDe.addEventListener('input', validateCurationForm);
            editMoTa.addEventListener('input', validateCurationForm);
            validateCurationForm();
          }

          // Auto expand preview accordion if flagged (US-046.2)
          if (autoExpandPreview) {
            const accPreview = document.getElementById('accPreview');
            const accSource = document.getElementById('accSource');
            if (accPreview) {
              accPreview.classList.add('expanded');
              const content = accPreview.querySelector('.accordion-content');
              if (content) content.style.display = 'block';
              const arrow = accPreview.querySelector('.arrow');
              if (arrow) arrow.textContent = '▼';
              
              // Smooth scroll to the preview section
              setTimeout(() => {
                accPreview.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }, 150);
            }
            if (accSource) {
              accSource.classList.remove('expanded');
              const content = accSource.querySelector('.accordion-content');
              if (content) content.style.display = 'none';
              const arrow = accSource.querySelector('.arrow');
              if (arrow) arrow.textContent = '▶';
            }
            if (typeof window.gotoImageEditorSlide === 'function') {
              window.gotoImageEditorSlide(window.activeImageEditorIndex || 0);
            }
          }
        }, 50);
      }
  }


  
  // === isListingSodoUrl ===
    window.isListingSodoUrl = function(url, p) {
      if (!url || !p) return false;
      const normFn = window.normalizeImgUrl;
      if (!normFn) return false;
      const norm = normFn(url);
      if (norm === '') return false;
      
      // 1. Nhận diện theo mẫu tên file Cloudinary được uploader tạo ra (cực kỳ tối ưu và nhanh)
      const urlLower = String(url).toLowerCase();
      if (urlLower.includes('/sodo1_') || urlLower.includes('/sodo2_') || 
          urlLower.includes('/sodo3_') || urlLower.includes('/sodo4_') || urlLower.includes('/sodo5_')) {
        return true;
      }

      // 2. Lấy 5 giá trị sodo hiện có của căn nhà (ưu tiên đọc từ DOM để phản hồi ngay lập tức khi thay đổi trên Form)
      const getSodoVal = (idx) => {
        let el = document.getElementById(`editSodo${idx}Url`);
        if (el) return el.value.trim();
        const colIdx = window.getPoolSodoColIdx ? window.getPoolSodoColIdx(idx) : null;
        if (p.pool_row_data && colIdx !== null) return p.pool_row_data[colIdx];
        return p[`raw_sodo${idx}`] || '';
      };

      const sodo1Val = getSodoVal(1);
      const sodo2Val = getSodoVal(2);
      const sodo3Val = getSodoVal(3);
      const sodo4Val = getSodoVal(4);
      const sodo5Val = getSodoVal(5);

      const normS1 = normFn(sodo1Val);
      const normS2 = normFn(sodo2Val);
      const normS3 = normFn(sodo3Val);
      const normS4 = normFn(sodo4Val);
      const normS5 = normFn(sodo5Val);

      if (norm === normS1 || norm === normS2 || norm === normS3 || norm === normS4 || norm === normS5) {
        return true;
      }
      return false;
    };
  // === renderImageEditorWidget ===
    function renderImageEditorWidget(p) {
      const slidesBefore = window.imageEditorSlides || [];
      const activeIdxBefore = window.activeImageEditorIndex || 0;
      let activeCardId = null;
      if (activeIdxBefore >= 0 && activeIdxBefore < slidesBefore.length) {
        const activeCard = slidesBefore[activeIdxBefore];
        activeCardId = { type: activeCard.type, index: activeCard.index };
      }
      console.log("Image Editor Debug - Before:", {
        activeIdxBefore,
        slidesCountBefore: slidesBefore.length,
        activeCardId
      });

      const domCover = document.getElementById('editCoverImgUrl');
      const domPublicCover = document.getElementById('editPublicCoverUrl');
      const domPublicInterior = document.getElementById('editPublicInteriorIndices');
      const domPublicAlley = document.getElementById('editPublicAlleyIndices');
      const domSodo1 = document.getElementById('editSodo1Url');
      const domSodo2 = document.getElementById('editSodo2Url');
      const domSodo3 = document.getElementById('editSodo3Url');
      const domSodo4 = document.getElementById('editSodo4Url');
      const domSodo5 = document.getElementById('editSodo5Url');

      const cards = [];
      
      const sodo1Url = domSodo1 ? domSodo1.value : (p.pool_row_data ? p.pool_row_data[window.getPoolSodoColIdx(1)] : p.raw_sodo1);
      if (sodo1Url) cards.push({ type: "sodo", index: 1, url: sodo1Url });
      
      const sodo2Url = domSodo2 ? domSodo2.value : (p.pool_row_data ? p.pool_row_data[window.getPoolSodoColIdx(2)] : p.raw_sodo2);
      if (sodo2Url) cards.push({ type: "sodo", index: 2, url: sodo2Url });

      const sodo3Url = domSodo3 ? domSodo3.value : (p.pool_row_data ? p.pool_row_data[window.getPoolSodoColIdx(3)] : p.raw_sodo3);
      if (sodo3Url) cards.push({ type: "sodo", index: 3, url: sodo3Url });

      const sodo4Url = domSodo4 ? domSodo4.value : (p.pool_row_data ? p.pool_row_data[window.getPoolSodoColIdx(4)] : p.raw_sodo4);
      if (sodo4Url) cards.push({ type: "sodo", index: 4, url: sodo4Url });

      const sodo5Url = domSodo5 ? domSodo5.value : (p.pool_row_data ? p.pool_row_data[window.getPoolSodoColIdx(5)] : p.raw_sodo5);
      if (sodo5Url) cards.push({ type: "sodo", index: 5, url: sodo5Url });
      
      const facadeUrl = p.pool_row_data ? p.pool_row_data[29] : p.img_mat_tien;
      if (facadeUrl) cards.push({ type: "facade", index: 0, url: facadeUrl });
      
      for (let i = 1; i <= 25; i++) {
        const idx = window.getPoolInteriorColIdx(i);
        const url = p.pool_row_data ? p.pool_row_data[idx] : (p.imgs && p.imgs[i - 1]);
        if (url) cards.push({ type: "interior", index: i, url: url });
      }
      
      for (let i = 1; i <= 10; i++) {
        const url = p.pool_row_data ? p.pool_row_data[window.getPoolAlleyColIdx(i)] : null;
        if (url) cards.push({ type: "alley", index: i, url: url });
      }

      const isSodoUrl = (url) => {
        return window.isListingSodoUrl(url, p);
      };

      // Priority duplicate filtering:
      const priorityList = [
        ...cards.filter(c => (c.type === 'interior' && c.index > 1) || c.type === 'alley'),
        ...cards.filter(c => (c.type === 'interior' && c.index === 1) || c.type === 'sodo' || c.type === 'facade')
      ];

      const renderedUrls = new Set();
      priorityList.forEach(c => {
        const normUrl = normalizeImgUrl(c.url);
        if (!normUrl) {
          c.shouldRender = false;
          return;
        }
        if ((c.type === 'interior' || c.type === 'alley') && isSodoUrl(c.url)) {
          c.shouldRender = false;
          return;
        }
        if (!renderedUrls.has(normUrl)) {
          c.shouldRender = true;
          renderedUrls.add(normUrl);
        } else {
          c.shouldRender = false;
        }
      });

      const renderedCards = cards.filter(c => c.shouldRender);

      // Recover current selected public interior/alley indices
      let currentCover = domCover ? domCover.value : ((p.isFromPoolOnly && p.pool_row_data) ? '' : (p.img_mat_tien || ''));
      let currentPublicCover = '';
      if (domPublicCover) {
        currentPublicCover = domPublicCover.value;
      } else {
        if (!p.isFromPoolOnly) {
          if (p.original_row_data && p.original_row_data[20]) {
            currentPublicCover = p.original_row_data[20];
          } else if (p.pool_row_data) {
            currentPublicCover = p.pool_row_data[40] || '';
          } else if (p.imgs && p.imgs.length > 0) {
            currentPublicCover = p.imgs[0];
          }
        }
      }
      
      let currentInteriorIndices = '';
      let currentAlleyIndices = '';

      if (domPublicInterior && domPublicAlley) {
        currentInteriorIndices = domPublicInterior.value;
        currentAlleyIndices = domPublicAlley.value;
      } else {
        if (!p.isFromPoolOnly && p.pool_row_data && (p.pool_row_data[62] || p.pool_row_data[63])) {
          currentInteriorIndices = String(p.pool_row_data[62] || '').trim();
          currentAlleyIndices = String(p.pool_row_data[63] || '').trim();
        } else if (!p.isFromPoolOnly && p.pool_row_data) {
          const cleanPublicImages = [];
          if (p.original_row_data) {
            for (let i = 20; i <= 29; i++) {
              if (p.original_row_data[i]) cleanPublicImages.push(p.original_row_data[i]);
            }
          } else {
            cleanPublicImages.push(...(p.imgs || []));
          }
          const normPublic = cleanPublicImages.map(url => normalizeImgUrl(url));

          const intIndices = [];
          for (let i = 1; i <= 25; i++) {
            const url = p.pool_row_data[window.getPoolInteriorColIdx(i)];
            if (url) {
              let isMatched = normPublic.includes(normalizeImgUrl(url));
              if (isMatched) {
                intIndices.push(i);
              }
            }
          }
          currentInteriorIndices = intIndices.join(',');

          const alleyIndices = [];
          for (let i = 1; i <= 10; i++) {
            const url = p.pool_row_data[window.getPoolAlleyColIdx(i)];
            if (url) {
              let isMatched = normPublic.includes(normalizeImgUrl(url));
              if (isMatched) {
                alleyIndices.push(i);
              }
            }
          }
          currentAlleyIndices = alleyIndices.join(',');
        } else if (!p.isFromPoolOnly) {
          const intIndices = [];
          if (p.imgs) {
            p.imgs.forEach((url, idx) => {
              intIndices.push(idx + 1);
            });
          }
          currentInteriorIndices = intIndices.join(',');
        }
      }

      // Compute active public display order list (finalImages) to sort public images by their exact selection order (US-084 Curation Order Thumbnail Sorting)
      const poolRowData = p.pool_row_data;
      const targetMatTien = p.isFromPoolOnly ? '' : (p.pool_row_data ? (p.pool_row_data[29] || '') : (p.img_mat_tien || ''));
      const normMatTien = normalizeImgUrl(targetMatTien);
      const isFacadeUrl = (url) => {
        if (!url) return false;
        const norm = normalizeImgUrl(url);
        return norm !== '' && norm === normMatTien;
      };

      const finalImages = [];
      if (poolRowData) {
        const noithatIndices = currentInteriorIndices.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n) && n >= 1 && n <= 25);
        const hemIndices = currentAlleyIndices.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n) && n >= 1 && n <= 10);

        let publicCover = currentPublicCover;
        if (publicCover && ((window.isListingSodoUrl && window.isListingSodoUrl(publicCover, p)) || isFacadeUrl(publicCover))) {
          publicCover = '';
        }
        if (!publicCover) {
          const candidates = [];
          const interior1Idx = window.getPoolInteriorColIdx(1);
          if (poolRowData[interior1Idx] && (!window.isListingSodoUrl || !window.isListingSodoUrl(poolRowData[interior1Idx], p)) && !isFacadeUrl(poolRowData[interior1Idx])) {
            candidates.push(poolRowData[interior1Idx]);
          }
          for (let i = 0; i < noithatIndices.length; i++) {
            const url = poolRowData[window.getPoolInteriorColIdx(noithatIndices[i])];
            if (url && (!window.isListingSodoUrl || !window.isListingSodoUrl(url, p)) && !isFacadeUrl(url)) {
              candidates.push(url);
              break;
            }
          }
          publicCover = candidates[0] || '';
        }

        if (publicCover && (!window.isListingSodoUrl || !window.isListingSodoUrl(publicCover, p)) && !isFacadeUrl(publicCover)) {
          finalImages.push(publicCover);
        }
        
        const maxHem = 2;
        let addedHem = 0;
        for (let i = 0; i < hemIndices.length && addedHem < maxHem; i++) {
          const hemIdx = hemIndices[i];
          const hemUrl = poolRowData[window.getPoolAlleyColIdx(hemIdx)];
          if (hemUrl && (!window.isListingSodoUrl || !window.isListingSodoUrl(hemUrl, p)) && !isFacadeUrl(hemUrl)) {
            finalImages.push(hemUrl);
            addedHem++;
          }
        }
        
        for (let i = 0; i < noithatIndices.length; i++) {
          const imgIdx = noithatIndices[i];
          const imgUrl = poolRowData[window.getPoolInteriorColIdx(imgIdx)];
          if (imgUrl && imgUrl !== publicCover && (!window.isListingSodoUrl || !window.isListingSodoUrl(imgUrl, p)) && !isFacadeUrl(imgUrl) && finalImages.length < 15) {
            finalImages.push(imgUrl);
          }
        }
      } else {
        const publicCover = currentPublicCover || (p.imgs && p.imgs[0]);
        if (publicCover && (!window.isListingSodoUrl || !window.isListingSodoUrl(publicCover, p)) && !isFacadeUrl(publicCover)) {
          finalImages.push(publicCover);
        }
        if (p.imgs) {
          p.imgs.forEach(url => {
            if (url && url !== publicCover && !finalImages.includes(url) && (!window.isListingSodoUrl || !window.isListingSodoUrl(url, p)) && !isFacadeUrl(url)) {
              finalImages.push(url);
            }
          });
        }
      }
      const normFinalImages = finalImages.filter(Boolean).map(url => normalizeImgUrl(url));

      const getCardSortWeight = (c) => {
        const normUrl = normalizeImgUrl(c.url);
        if (!normUrl) return 99;

        if (isSodoUrl(c.url)) return 1;

        if (normMatTien && normUrl === normMatTien) return 2;

        const publicIdx = normFinalImages.indexOf(normUrl);
        if (publicIdx !== -1) {
          return 3 + publicIdx / 100;
        }

        return 5;
      };

      renderedCards.sort((a, b) => getCardSortWeight(a) - getCardSortWeight(b));

      let newActiveIdx = 0;
      if (activeCardId) {
        const foundIdx = renderedCards.findIndex(s => s.type === activeCardId.type && s.index === activeCardId.index);
        if (foundIdx !== -1) {
          newActiveIdx = foundIdx;
        }
      }
      console.log("Image Editor Debug - After:", {
        newActiveIdx,
        slidesCountAfter: renderedCards.length,
        activeImageEditorIndex: window.activeImageEditorIndex,
        isJustMounted: window.carouselJustMounted
      });
      window.imageEditorSlides = renderedCards;
      window.activeImageEditorIndex = newActiveIdx;

      let slidesHtml = '';
      renderedCards.forEach((c, idx) => {
        slidesHtml += `
          <div class="carousel-slide-item" data-slide-index="${idx}">
            <img src="${fixImgUrl(c.url, 'w600')}" alt="Slide ${idx + 1}" style="cursor: zoom-in;" onclick="window.openZoomOverlay('${c.url.replace(/'/g, "\\'")}')">
            <div class="carousel-slide-badge">${c.type === "facade" ? "Mặt Tiền" : (c.type === "sodo" ? `Sổ ${c.index}` : (c.type === "interior" ? `Nội Thất ${c.index}` : `Hẻm ${c.index}`))}</div>
            <div class="carousel-order-indicator" id="carouselOrderIndicator-${idx}" style="display: none;">#1</div>
            <div class="carousel-role-indicator" id="carouselRoleIndicator-${idx}" style="display: none;"></div>
          </div>
        `;
      });

      let html = `
        <div class="admin-edit-group" id="imageEditorCurationGroup" style="margin-top: 10px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <label style="font-weight: 800; color: var(--gold); display: block; font-size: 12px; margin: 0;">🖼️ BIÊN TẬP HÌNH ẢNH (CAROUSEL TRƯỢT 📱)</label>
            <span id="editorDebugLabel" style="font-size: 9px; font-weight: 700; color: rgba(255,255,255,0.45); font-family: monospace;">v1.4</span>
          </div>
          
          <!-- LOCAL IMAGE UPLOADER (US-053) -->
          <div class="local-uploader-panel" style="display: flex; align-items: center; gap: 8px; background: rgba(255, 191, 36, 0.08); padding: 8px 12px; border-radius: 10px; border: 1.5px solid rgba(255, 191, 36, 0.2); margin-bottom: 10px; flex-wrap: wrap; backdrop-filter: blur(10px); box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); width: 100%; box-sizing: border-box;">
            <div style="font-size: 11px; font-weight: 800; color: var(--gold); display: flex; align-items: center; gap: 4px;">
              📁 TẢI LÊN:
            </div>
            <select id="localUploadType" style="background: rgba(0,0,0,0.6); color: #fff; border: 1px solid rgba(255,191,36,0.3); border-radius: 6px; padding: 4px 8px; font-size: 11px; font-weight: 700; cursor: pointer; outline: none; font-family: inherit;">
              <option value="interior">Ảnh thường (Có nén)</option>
              <option value="sodo">Ảnh sổ (Ko nén)</option>
            </select>
            <button type="button" id="uploadLocalBtn" onclick="document.getElementById('localImageFileInput').click()" style="background: var(--gold); color: #1c1c1e; border: none; padding: 6px 12px; border-radius: 6px; font-size: 11px; font-weight: 800; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 4px; font-family: inherit; text-transform: uppercase;">
              ➕ UP ẢNH
            </button>
            <input type="file" id="localImageFileInput" multiple accept="image/*" style="display: none;" onchange="window.handleLocalImageUpload(event)" />
            <div id="localUploadProgress" style="font-size: 11px; font-weight: 700; color: #fff; margin-left: auto; display: none;">
              ⌛ Đang tải: <span id="localUploadProgressTxt">0/0</span>
            </div>
          </div>

          <!-- CAROUSEL VIEWPORT -->
          <div class="image-editor-carousel-container">
            <div class="carousel-viewport-wrapper" id="carouselViewportWrapper" 
                 ontouchstart="window.handleCarouselTouchStart(event)" 
                 ontouchmove="window.handleCarouselTouchMove(event)" 
                 ontouchend="window.handleCarouselTouchEnd(event)">
              <div class="carousel-slides-track" id="carouselSlidesTrack" style="transform: translateX(-${newActiveIdx * 100}%);">
                ${slidesHtml}
              </div>
              <button type="button" class="carousel-nav-btn prev-btn" onclick="window.slideImageEditorCarousel(-1)">◀</button>
              <button type="button" class="carousel-nav-btn next-btn" onclick="window.slideImageEditorCarousel(1)">▶</button>
            </div>

            <!-- THUMBNAIL STRIP -->
            <div class="thumbnail-strip-wrapper">
              <div class="thumbnail-strip-scroll" id="thumbnailStripScroll">
                ${renderedCards.map((c, idx) => `
                  <div class="thumbnail-item-card" id="thumbCard-${idx}" onclick="window.gotoImageEditorSlide(${idx}, true)">
                    <img src="${fixImgUrl(c.url, 'w100')}" alt="Thumb ${idx + 1}" loading="lazy">
                    <span class="thumb-mini-badge" id="thumbMiniBadge-${idx}"></span>
                    <span class="thumb-mini-badge public-badge" id="thumbPublicBadge-${idx}"></span>
                  </div>
                `).join('')}
              </div>
            </div>

            <!-- CONTROL PANEL -->
            <div class="image-editor-control-panel">
              <div class="control-row">
                <button type="button" id="ctrlFacadeBtn" class="control-btn" onclick="window.activeImageToggleFacade()">
                  🔒 Mặt tiền
                </button>
                <button type="button" id="ctrlCoverBtn" class="control-btn" onclick="window.activeImageToggleCover()">
                  ⭐ Ảnh nền
                </button>
                <button type="button" id="ctrlSodoBtn" class="control-btn" onclick="window.activeImageToggleSodo()">
                  📜 Sổ đỏ
                </button>
              </div>
              <div class="control-row" style="margin-top: 5px;">
                <button type="button" id="ctrlPublicBtn" class="control-btn" onclick="window.activeImageTogglePublic()">
                  👁️ Hiện
                </button>
                <button type="button" class="control-btn" onclick="window.activeImageMoveOrder(-1)">
                  ◀ Lên
                </button>
                <button type="button" class="control-btn" onclick="window.activeImageMoveOrder(1)">
                  Xuống ▶
                </button>
              </div>
              <div class="control-row" style="margin-top: 5px;">
                ${!p.isFromPoolOnly ? `
                <button type="button" class="control-btn" onclick="window.uncheckAllCurationImages()" style="background: rgba(192, 57, 43, 0.15); border-color: var(--red); color: var(--red); width: 100%;">
                  ✕ Bỏ hết
                </button>
                ` : ''}
              </div>
            </div>
          </div>

          <!-- Hidden Inputs to hold current selections -->
          <input type="hidden" id="editCoverImgUrl" value="${currentCover}">
          <input type="hidden" id="editPublicCoverUrl" value="${currentPublicCover}">
          <input type="hidden" id="editPublicInteriorIndices" value="${currentInteriorIndices}">
          <input type="hidden" id="editPublicAlleyIndices" value="${currentAlleyIndices}">
          <input type="hidden" id="editSodo1Url" value="${sodo1Url || ''}">
          <input type="hidden" id="editSodo2Url" value="${sodo2Url || ''}">
          <input type="hidden" id="editSodo3Url" value="${sodo3Url || ''}">
          <input type="hidden" id="editSodo4Url" value="${sodo4Url || ''}">
          <input type="hidden" id="editSodo5Url" value="${sodo5Url || ''}">
        </div>
      `;

      return html;
    }
  // === slideImageEditorCarousel ===
    window.slideImageEditorCarousel = function(direction) {
      const slides = window.imageEditorSlides || [];
      if (slides.length === 0) return;
      let nextIdx = window.activeImageEditorIndex + direction;
      if (nextIdx < 0) nextIdx = slides.length - 1;
      if (nextIdx >= slides.length) nextIdx = 0;
      window.gotoImageEditorSlide(nextIdx, true);
    };
  // === gotoImageEditorSlide ===
    window.gotoImageEditorSlide = function(idx, enableTransition = false) {
      const slides = window.imageEditorSlides || [];
      if (slides.length === 0) return;
      if (idx < 0) idx = 0;
      if (idx >= slides.length) idx = slides.length - 1;
      
      window.activeImageEditorIndex = idx;
      
      const track = document.getElementById('carouselSlidesTrack');
      if (track) {
        const debugLabel = document.getElementById('editorDebugLabel');
        if (debugLabel) {
          debugLabel.innerText = `v1.4 [Idx:${idx} (Trans:${enableTransition})]`;
        }
        if (enableTransition) {
          track.classList.add('has-transition');
        } else {
          track.classList.remove('has-transition');
        }
        track.style.transform = `translateX(-${idx * 100}%)`;
      }
      
      document.querySelectorAll('.thumbnail-item-card').forEach((card, cidx) => {
        if (cidx === idx) {
          card.classList.add('active');
          card.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        } else {
          card.classList.remove('active');
        }
      });
      
      window.refreshImageEditorUI();
    };
  // === handleCarouselTouchStart ===
    window.handleCarouselTouchStart = function(event) {
      touchStartX = event.changedTouches[0].screenX;
    };
  // === handleCarouselTouchMove ===
    window.handleCarouselTouchMove = function(event) {
      // Swipe detection is handled on touchend
    };
  // === handleCarouselTouchEnd ===
    window.handleCarouselTouchEnd = function(event) {
      touchEndX = event.changedTouches[0].screenX;
      window.handleCarouselSwipe();
    };
  // === handleCarouselSwipe ===
    window.handleCarouselSwipe = function() {
      const minSwipeDistance = 50;
      const diffX = touchEndX - touchStartX;
      if (Math.abs(diffX) > minSwipeDistance) {
        if (diffX > 0) {
          window.slideImageEditorCarousel(-1);
        } else {
          window.slideImageEditorCarousel(1);
        }
      }
    };
  // === removeImageFromPublicLists ===
    window.removeImageFromPublicLists = function(url, type, index) {
      if (type === "interior") {
        const input = document.getElementById('editPublicInteriorIndices');
        if (input) {
          let indices = input.value.split(',').map(s => s.trim()).filter(Boolean);
          indices = indices.filter(i => i !== String(index));
          input.value = indices.join(',');
        }
      } else if (type === "alley") {
        const input = document.getElementById('editPublicAlleyIndices');
        if (input) {
          let indices = input.value.split(',').map(s => s.trim()).filter(Boolean);
          indices = indices.filter(i => i !== String(index));
          input.value = indices.join(',');
        }
      }
    };
  // === removeImageFromSodo ===
    window.removeImageFromSodo = function(url) {
      const normUrl = normalizeImgUrl(url);
      if (!normUrl) return;
      
      const sodoInputs = [
        document.getElementById('editSodo1Url'),
        document.getElementById('editSodo2Url'),
        document.getElementById('editSodo3Url'),
        document.getElementById('editSodo4Url'),
        document.getElementById('editSodo5Url')
      ];
      
      sodoInputs.forEach(input => {
        if (input && normalizeImgUrl(input.value) === normUrl) {
          input.value = "";
        }
      });
    };
  // === activeImageToggleFacade ===
    window.activeImageToggleFacade = function() {
      const slides = window.imageEditorSlides || [];
      const activeIdx = window.activeImageEditorIndex;
      const slide = slides[activeIdx];
      if (!slide) return;
      
      const input = document.getElementById('editCoverImgUrl');
      if (!input) return;
      
      const currentVal = input.value.trim();
      const slideUrl = slide.url.trim();
      
      if (normalizeImgUrl(currentVal) === normalizeImgUrl(slideUrl)) {
        input.value = "";
      } else {
        input.value = slideUrl;
        window.removeImageFromPublicLists(slideUrl, slide.type, slide.index);
        const coverInput = document.getElementById('editPublicCoverUrl');
        if (coverInput && normalizeImgUrl(coverInput.value) === normalizeImgUrl(slideUrl)) {
          coverInput.value = "";
        }
      }
      
      window.reRenderCurationEditorInPlace();

    };
  // === activeImageToggleCover ===
    window.activeImageToggleCover = function() {
      const slides = window.imageEditorSlides || [];
      const activeIdx = window.activeImageEditorIndex;
      const slide = slides[activeIdx];
      if (!slide) return;
      
      const input = document.getElementById('editPublicCoverUrl');
      if (!input) return;
      
      const currentVal = input.value.trim();
      const slideUrl = slide.url.trim();
      
      if (normalizeImgUrl(currentVal) === normalizeImgUrl(slideUrl)) {
        input.value = "";
      } else {
        input.value = slideUrl;
        
        const facadeInput = document.getElementById('editCoverImgUrl');
        if (facadeInput && normalizeImgUrl(facadeInput.value) === normalizeImgUrl(slideUrl)) {
          facadeInput.value = "";
        }
        
        window.removeImageFromSodo(slideUrl);
        
        if (slide.type === "interior") {
          const publicIntInput = document.getElementById('editPublicInteriorIndices');
          if (publicIntInput) {
            let indices = publicIntInput.value.split(',').map(s => s.trim()).filter(Boolean);
            if (!indices.includes(String(slide.index))) {
              indices.push(String(slide.index));
              publicIntInput.value = indices.join(',');
            }
          }
        } else if (slide.type === "alley") {
          const publicAlleyInput = document.getElementById('editPublicAlleyIndices');
          if (publicAlleyInput) {
            let indices = publicAlleyInput.value.split(',').map(s => s.trim()).filter(Boolean);
            if (!indices.includes(String(slide.index))) {
              indices.push(String(slide.index));
              publicAlleyInput.value = indices.join(',');
            }
          }
        }
      }
      
      window.reRenderCurationEditorInPlace();

    };
  // === activeImageToggleSodo ===
    window.activeImageToggleSodo = function() {
      const slides = window.imageEditorSlides || [];
      const activeIdx = window.activeImageEditorIndex;
      const slide = slides[activeIdx];
      if (!slide) return;
      
      const sodoInputs = [
        document.getElementById('editSodo1Url'),
        document.getElementById('editSodo2Url'),
        document.getElementById('editSodo3Url'),
        document.getElementById('editSodo4Url'),
        document.getElementById('editSodo5Url')
      ];
      if (sodoInputs.some(input => !input)) return;
      
      const slideUrl = slide.url.trim();
      const normUrl = normalizeImgUrl(slideUrl);
      if (!normUrl) return;
      
      const vals = sodoInputs.map(input => input.value.trim());
      const normVals = vals.map(val => normalizeImgUrl(val));
      
      const existingIdx = normVals.indexOf(normUrl);
      if (existingIdx !== -1) {
        sodoInputs[existingIdx].value = "";
        showToast(`Đã hủy gán Sổ ${existingIdx + 1} cho ảnh này!`, "info");
      } else {
        let assigned = false;
        let badgeNum = 1;
        const emptyIdx = vals.indexOf("");
        if (emptyIdx !== -1) {
          sodoInputs[emptyIdx].value = slideUrl;
          assigned = true;
          badgeNum = emptyIdx + 1;
        } else {
          sodoInputs[0].value = slideUrl;
          assigned = true;
          badgeNum = 1;
          showToast("Tất cả 5 vị trí Sổ đỏ đã đầy. Tự động ghi đè vị trí Sổ 1!", "warning");
        }
        
        if (assigned) {
          window.removeImageFromPublicLists(slideUrl, slide.type, slide.index);
          
          const facadeInput = document.getElementById('editCoverImgUrl');
          if (facadeInput && normalizeImgUrl(facadeInput.value) === normUrl) {
            facadeInput.value = "";
          }
          
          const coverInput = document.getElementById('editPublicCoverUrl');
          if (coverInput && normalizeImgUrl(coverInput.value) === normUrl) {
            coverInput.value = "";
          }
          
          showToast(`Đã gán ảnh này làm Sổ ${badgeNum}!`, "success");
        }
      }
      
      window.reRenderCurationEditorInPlace();

    };
  // === activeImageTogglePublic ===
    window.activeImageTogglePublic = function() {
      const slides = window.imageEditorSlides || [];
      const activeIdx = window.activeImageEditorIndex;
      const slide = slides[activeIdx];
      if (!slide) return;
      
      if (slide.type === "facade" || slide.type === "sodo") {
        showToast("Không thể chọn hiển thị public cho hình Mặt Tiền hoặc Sổ đỏ!", "warning");
        return;
      }
      
      const slideUrl = slide.url.trim();
      const normUrl = normalizeImgUrl(slideUrl);
      
      const facadeInput = document.getElementById('editCoverImgUrl');
      if (facadeInput && normalizeImgUrl(facadeInput.value) === normUrl) {
        showToast("Không thể chọn hiển thị public cho hình Mặt Tiền!", "warning");
        return;
      }
      
      const sodoInputs = [
        document.getElementById('editSodo1Url'),
        document.getElementById('editSodo2Url'),
        document.getElementById('editSodo3Url'),
        document.getElementById('editSodo4Url'),
        document.getElementById('editSodo5Url')
      ];
      const sodoVals = sodoInputs.map(input => normalizeImgUrl(input?.value || ''));
      if (sodoVals.includes(normUrl)) {
        showToast("Không thể chọn hiển thị public cho hình Sổ đỏ!", "warning");
        return;
      }
      
      if (slide.type === "interior") {
        const input = document.getElementById('editPublicInteriorIndices');
        if (!input) return;
        let indices = input.value.split(',').map(s => s.trim()).filter(Boolean);
        const indexStr = String(slide.index);
        
        if (indices.includes(indexStr)) {
          indices = indices.filter(i => i !== indexStr);
          const coverInput = document.getElementById('editPublicCoverUrl');
          if (coverInput && normalizeImgUrl(coverInput.value) === normUrl) {
            coverInput.value = "";
          }
        } else {
          indices.push(indexStr);
        }
        input.value = indices.join(',');
      } else if (slide.type === "alley") {
        const input = document.getElementById('editPublicAlleyIndices');
        if (!input) return;
        let indices = input.value.split(',').map(s => s.trim()).filter(Boolean);
        const indexStr = String(slide.index);
        
        if (indices.includes(indexStr)) {
          indices = indices.filter(i => i !== indexStr);
          const coverInput = document.getElementById('editPublicCoverUrl');
          if (coverInput && normalizeImgUrl(coverInput.value) === normUrl) {
            coverInput.value = "";
          }
        } else {
          indices.push(indexStr);
        }
        input.value = indices.join(',');
      }
      
      window.reRenderCurationEditorInPlace();

    };
  // === activeImageMoveOrder ===
    window.activeImageMoveOrder = function(direction) {
      const p = window.activeCurationListing;
      if (!p) return;
      const activeIdx = window.activeImageEditorIndex;
      const slides = window.imageEditorSlides || [];
      if (activeIdx < 0 || activeIdx >= slides.length) return;
      const slide = slides[activeIdx];
      
      if (slide.type === "interior") {
        const input = document.getElementById('editPublicInteriorIndices');
        if (!input) return;
        let indices = input.value.split(',').map(s => s.trim()).filter(Boolean);
        const pos = indices.indexOf(String(slide.index));
        if (pos === -1) {
          showToast("Hình này chưa được chọn hiển thị public để sắp xếp!", "warning");
          return;
        }
        const newPos = pos + direction;
        if (newPos >= 0 && newPos < indices.length) {
          const temp = indices[pos];
          indices[pos] = indices[newPos];
          indices[newPos] = temp;
          input.value = indices.join(',');
          
          window.reRenderCurationEditorInPlace();

        }
      } else if (slide.type === "alley") {
        const input = document.getElementById('editPublicAlleyIndices');
        if (!input) return;
        let indices = input.value.split(',').map(s => s.trim()).filter(Boolean);
        const pos = indices.indexOf(String(slide.index));
        if (pos === -1) {
          showToast("Hình này chưa được chọn hiển thị public để sắp xếp!", "warning");
          return;
        }
        const newPos = pos + direction;
        if (newPos >= 0 && newPos < indices.length) {
          const temp = indices[pos];
          indices[pos] = indices[newPos];
          indices[newPos] = temp;
          input.value = indices.join(',');
          
          window.reRenderCurationEditorInPlace();

        }
      } else {
        showToast("Chỉ có thể sắp xếp thứ tự của hình Nội Thất hoặc Hẻm hiển thị public!", "warning");
      }
    };
  // === reRenderCurationEditorInPlace ===
    window.reRenderCurationEditorInPlace = function() {
      const p = window.activeCurationListing;
      if (!p) return;

      const editGroup = document.getElementById("imageEditorCurationGroup");
      if (!editGroup) return;

      window.carouselJustMounted = true;

      const newHtml = renderImageEditorWidget(p);

      const parent = editGroup.parentNode;
      const tempDiv = document.createElement("div");
      tempDiv.innerHTML = newHtml;
      parent.replaceChild(tempDiv.firstElementChild, editGroup);

      if (typeof window.gotoImageEditorSlide === 'function') {
        window.gotoImageEditorSlide(window.activeImageEditorIndex);
      }
    };
  // === refreshImageEditorUI ===
    window.refreshImageEditorUI = function() {
      const p = window.activeCurationListing;
      if (!p) return;
      
      const slides = window.imageEditorSlides || [];
      if (slides.length === 0) return;
      
      const facadeUrl = (document.getElementById('editCoverImgUrl')?.value || '').trim();
      const coverUrl = (document.getElementById('editPublicCoverUrl')?.value || '').trim();
      const publicIntStr = (document.getElementById('editPublicInteriorIndices')?.value || '').trim();
      const publicAlleyStr = (document.getElementById('editPublicAlleyIndices')?.value || '').trim();
      
      const sodoUrls = [
        (document.getElementById('editSodo1Url')?.value || '').trim(),
        (document.getElementById('editSodo2Url')?.value || '').trim(),
        (document.getElementById('editSodo3Url')?.value || '').trim(),
        (document.getElementById('editSodo4Url')?.value || '').trim(),
        (document.getElementById('editSodo5Url')?.value || '').trim()
      ];
      
      const normFacade = normalizeImgUrl(facadeUrl);
      const normCover = normalizeImgUrl(coverUrl);
      const normSodos = sodoUrls.map(url => normalizeImgUrl(url));
      
      const publicIntIndices = publicIntStr.split(',').map(s => s.trim()).filter(Boolean);
      const publicAlleyIndices = publicAlleyStr.split(',').map(s => s.trim()).filter(Boolean);
      
      const publicImages = window.getPublicImagesFromForm(p);
      const normPublicImages = publicImages.map(url => normalizeImgUrl(url));

      slides.forEach((c, idx) => {
        const normUrl = normalizeImgUrl(c.url);
        const isFacade = normUrl && normUrl === normFacade;
        const isCover = normUrl && normUrl === normCover;
        
        let sodoNum = 0;
        if (normUrl) {
          const sidx = normSodos.indexOf(normUrl);
          if (sidx !== -1) {
            sodoNum = sidx + 1;
          }
        }
        
        let isPublic = false;
        if (c.type === "interior") {
          isPublic = publicIntIndices.includes(String(c.index));
        } else if (c.type === "alley") {
          isPublic = publicAlleyIndices.includes(String(c.index));
        }
        
        const orderInd = document.getElementById(`carouselOrderIndicator-${idx}`);
        const roleInd = document.getElementById(`carouselRoleIndicator-${idx}`);
        
        if (orderInd) {
          if (isPublic || isCover) {
            const orderIdx = normPublicImages.indexOf(normUrl);
            if (orderIdx !== -1) {
              orderInd.style.display = 'block';
              orderInd.innerHTML = `#${orderIdx + 1}`;
              orderInd.className = 'carousel-order-indicator public-order';
            } else {
              orderInd.style.display = 'none';
            }
          } else {
            orderInd.style.display = 'none';
          }
        }
        
        if (roleInd) {
          if (isFacade) {
            roleInd.style.display = 'block';
            roleInd.innerHTML = '🔒 Mặt Tiền';
            roleInd.className = 'carousel-role-indicator role-facade';
          } else if (sodoNum > 0) {
            roleInd.style.display = 'block';
            roleInd.innerHTML = `📜 Sổ ${sodoNum}`;
            roleInd.className = 'carousel-role-indicator role-sodo';
          } else if (isCover) {
            roleInd.style.display = 'block';
            roleInd.innerHTML = '⭐ Ảnh Nền';
            roleInd.className = 'carousel-role-indicator role-cover';
          } else {
            roleInd.style.display = 'none';
          }
        }
        
        const thumbCard = document.getElementById(`thumbCard-${idx}`);
        const miniBadge = document.getElementById(`thumbMiniBadge-${idx}`);
        const publicBadge = document.getElementById(`thumbPublicBadge-${idx}`);
        
        if (thumbCard) {
          thumbCard.className = `thumbnail-item-card ${idx === window.activeImageEditorIndex ? 'active' : ''}`;
          if (isFacade) {
            thumbCard.className += ' is-facade';
          } else if (sodoNum > 0) {
            thumbCard.className += ' is-sodo';
          } else if (isCover) {
            thumbCard.className += ' is-cover';
          } else if (isPublic) {
            thumbCard.className += ' is-public';
          }
        }
        
        if (miniBadge) {
          if (isFacade) {
            miniBadge.style.display = 'flex';
            miniBadge.innerHTML = '🔒';
            miniBadge.className = 'thumb-mini-badge badge-facade';
          } else if (sodoNum > 0) {
            miniBadge.style.display = 'flex';
            miniBadge.innerHTML = `S${sodoNum}`;
            miniBadge.className = 'thumb-mini-badge badge-sodo';
          } else if (isCover) {
            miniBadge.style.display = 'flex';
            miniBadge.innerHTML = '⭐';
            miniBadge.className = 'thumb-mini-badge badge-cover';
          } else {
            miniBadge.style.display = 'none';
          }
        }
        
        if (publicBadge) {
          if (isPublic || isCover) {
            const orderIdx = normPublicImages.indexOf(normUrl);
            if (orderIdx !== -1) {
              publicBadge.style.display = 'flex';
              publicBadge.innerHTML = `#${orderIdx + 1}`;
              publicBadge.className = 'thumb-mini-badge public-badge active-public';
            } else {
              publicBadge.style.display = 'none';
            }
          } else {
            publicBadge.style.display = 'none';
          }
        }
      });
      
      const activeIdx = window.activeImageEditorIndex;
      const activeSlide = slides[activeIdx];
      if (!activeSlide) return;
      
      const activeUrlNorm = normalizeImgUrl(activeSlide.url);
      const isActiveFacade = activeUrlNorm && activeUrlNorm === normFacade;
      const isActiveCover = activeUrlNorm && activeUrlNorm === normCover;
      const isActiveSodo = activeUrlNorm && normSodos.includes(activeUrlNorm);
      
      let isActivePublic = false;
      if (activeSlide.type === "interior") {
        isActivePublic = publicIntIndices.includes(String(activeSlide.index));
      } else if (activeSlide.type === "alley") {
        isActivePublic = publicAlleyIndices.includes(String(activeSlide.index));
      }
      
      const btnFacade = document.getElementById('ctrlFacadeBtn');
      const btnCover = document.getElementById('ctrlCoverBtn');
      const btnSodo = document.getElementById('ctrlSodoBtn');
      const btnPublic = document.getElementById('ctrlPublicBtn');
      
      if (btnFacade) {
        if (isActiveFacade) {
          btnFacade.style.background = 'var(--red)';
          btnFacade.style.color = '#fff';
        } else {
          btnFacade.style.background = '';
          btnFacade.style.color = '';
        }
      }
      
      if (btnCover) {
        if (isActiveCover) {
          btnCover.style.background = 'var(--gold)';
          btnCover.style.color = '#1c1c1e';
        } else {
          btnCover.style.background = '';
          btnCover.style.color = '';
        }
      }
      
      if (btnSodo) {
        if (isActiveSodo) {
          btnSodo.style.background = '#8e44ad';
          btnSodo.style.color = '#fff';
        } else {
          btnSodo.style.background = '';
          btnSodo.style.color = '';
        }
      }
      
      if (btnPublic) {
        if (activeSlide.type === "facade" || activeSlide.type === "sodo" || isActiveFacade || isActiveSodo) {
          btnPublic.disabled = true;
          btnPublic.style.opacity = '0.4';
          btnPublic.style.background = '';
          btnPublic.style.color = '';
        } else {
          btnPublic.disabled = false;
          btnPublic.style.opacity = '1';
          if (isActivePublic) {
            btnPublic.style.background = '#27ae60';
            btnPublic.style.color = '#fff';
          } else {
            btnPublic.style.background = '';
            btnPublic.style.color = '';
          }
        }
      }
    };
  // === compressImageClientSide ===
    function compressImageClientSide(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = (event) => {
          const img = new Image();
          img.src = event.target.result;
          img.onload = () => {
            const canvas = document.createElement("canvas");
            let width = img.width;
            let height = img.height;
            const maxDim = 1600;

            if (width > maxDim || height > maxDim) {
              if (width > height) {
                height = Math.round((height * maxDim) / width);
                width = maxDim;
              } else {
                width = Math.round((width * maxDim) / height);
                height = maxDim;
              }
            }

            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0, width, height);

            canvas.toBlob(
              (blob) => {
                if (blob) {
                  const compressedFile = new File([blob], file.name, {
                    type: "image/jpeg",
                    lastModified: Date.now()
                  });
                  resolve(compressedFile);
                } else {
                  reject(new Error("Canvas toBlob failed"));
                }
              },
              "image/jpeg",
              0.8
            );
          };
          img.onerror = (err) => reject(err);
        };
        reader.onerror = (err) => reject(err);
      });
    }
  // === uploadFileToR2 ===
    async function uploadFileToR2(file, type = "interior", listingId = "") {
      let sodoIndex = 1;
      if (type === "sodo") {
        for (let i = 1; i <= 5; i++) {
          const val = document.getElementById(`editSodo${i}Url`)?.value.trim();
          if (!val) {
            sodoIndex = i;
            break;
          }
        }
      }

      const filename = type === "sodo" 
        ? `${listingId}_sodo${sodoIndex}_${Date.now()}.jpg`
        : `${listingId}_interior_${Date.now()}.jpg`;

      const base64Data = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
      });

      const response = await fetch('/api/upload-r2', {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          file: base64Data,
          filename: filename,
          type: type
        })
      });

      if (!response.ok) {
        let errMsg = "Lỗi tải ảnh lên Cloudflare R2";
        try {
          const errData = await response.json();
          errMsg = errData.error || errMsg;
        } catch (e) {}
        throw new Error(errMsg);
      }

      const data = await response.json();
      return data.url;
    }
  // === handleLocalImageUpload ===
    window.handleLocalImageUpload = async function(event) {
      const files = Array.from(event.target.files);
      if (!files.length) return;

      const p = window.activeCurationListing;
      if (!p) {
        showToast("Không tìm thấy thông tin căn nhà hiện hành!", "error");
        return;
      }

      const uploadType = document.getElementById("localUploadType").value;
      const progressDiv = document.getElementById("localUploadProgress");
      const progressTxt = document.getElementById("localUploadProgressTxt");

      if (progressDiv) progressDiv.style.display = "block";
      if (progressTxt) progressTxt.innerText = `0/${files.length}`;

      const uploadLocalBtn = document.getElementById("uploadLocalBtn");
      if (uploadLocalBtn) uploadLocalBtn.disabled = true;

      let successCount = 0;
      let lastUploadedUrl = "";

      for (let i = 0; i < files.length; i++) {
        let file = files[i];
        if (progressTxt) progressTxt.innerText = `${i + 1}/${files.length}`;

        try {
          if (uploadType === "interior") {
            file = await compressImageClientSide(file);
          }

          let sodoIndex = 1;
          if (uploadType === "sodo") {
            for (let s = 1; s <= 5; s++) {
              const val = document.getElementById(`editSodo${s}Url`)?.value.trim();
              if (!val) {
                sodoIndex = s;
                break;
              }
            }
          }

          const uploadedUrl = await uploadFileToR2(file, uploadType, p.id || p.system_id);
          lastUploadedUrl = uploadedUrl;

          if (uploadType === "sodo") {
            const sodoInput = document.getElementById(`editSodo${sodoIndex}Url`);
            if (sodoInput) {
              sodoInput.value = uploadedUrl;
              
              const pIdx = window.getPoolSodoColIdx(sodoIndex);
              if (p.pool_row_data) p.pool_row_data[pIdx] = uploadedUrl;
              p[`raw_sodo${sodoIndex}`] = uploadedUrl;

              showToast(`Tải lên Sổ ${sodoIndex} thành công!`, "success");
              successCount++;
            }
          } else {
            let assignedIdx = -1;
            if (p.pool_row_data) {
              while (p.pool_row_data.length < 90) p.pool_row_data.push("");

              for (let j = 1; j <= 25; j++) {
                const colIdx = window.getPoolInteriorColIdx(j);
                if (!p.pool_row_data[colIdx]) {
                  p.pool_row_data[colIdx] = uploadedUrl;
                  assignedIdx = j;
                  break;
                }
              }
            }

            if (assignedIdx === -1) {
              if (!p.imgs) p.imgs = [];
              p.imgs.push(uploadedUrl);
              assignedIdx = p.imgs.length;
            }

            const publicInteriorInput = document.getElementById('editPublicInteriorIndices');
            if (publicInteriorInput && assignedIdx <= 15) {
              let currentVal = publicInteriorInput.value.trim();
              let indices = currentVal ? currentVal.split(',').map(s => s.trim()).filter(Boolean) : [];
              if (!indices.includes(String(assignedIdx))) {
                indices.push(String(assignedIdx));
                publicInteriorInput.value = indices.join(',');
              }
            }

            showToast(`Tải lên Ảnh Nội Thất ${assignedIdx} thành công!`, "success");
            successCount++;
          }
        } catch (err) {
          console.error("Lỗi upload file:", err);
          showToast(`Lỗi upload file ${file.name}: ${err.message}`, "error");
        }
      }

      event.target.value = "";
      if (progressDiv) progressDiv.style.display = "none";
      if (uploadLocalBtn) uploadLocalBtn.disabled = false;

      if (lastUploadedUrl) {
        window.reRenderCurationEditorInPlace();
        const normLast = normalizeImgUrl(lastUploadedUrl);
        const slides = window.imageEditorSlides || [];
        const newIdx = slides.findIndex(s => normalizeImgUrl(s.url) === normLast);
        if (newIdx !== -1) {
          window.activeImageEditorIndex = newIdx;
          if (typeof window.gotoImageEditorSlide === 'function') {
            window.gotoImageEditorSlide(newIdx);
          }
        }
      } else {
        window.reRenderCurationEditorInPlace();
      }


    };
  // === uncheckAllCurationImages ===
    window.uncheckAllCurationImages = function() {
      const agree = confirm("Bạn có đồng ý xóa hết tất cả các hình đã chọn (bao gồm hình mặt tiền, hình sổ, hình nền và các hình public) để chọn lại từ đầu không?");
      if (!agree) return;

      const coverInput = document.getElementById('editCoverImgUrl');
      const publicCoverInput = document.getElementById('editPublicCoverUrl');
      const publicInteriorInput = document.getElementById('editPublicInteriorIndices');
      const publicAlleyInput = document.getElementById('editPublicAlleyIndices');
      const sodo1Input = document.getElementById('editSodo1Url');
      const sodo2Input = document.getElementById('editSodo2Url');
      const sodo3Input = document.getElementById('editSodo3Url');
      const sodo4Input = document.getElementById('editSodo4Url');
      const sodo5Input = document.getElementById('editSodo5Url');

      if (coverInput) coverInput.value = '';
      if (publicCoverInput) publicCoverInput.value = '';
      if (publicInteriorInput) publicInteriorInput.value = '';
      if (publicAlleyInput) publicAlleyInput.value = '';
      if (sodo1Input) sodo1Input.value = '';
      if (sodo2Input) sodo2Input.value = '';
      if (sodo3Input) sodo3Input.value = '';
      if (sodo4Input) sodo4Input.value = '';
      if (sodo5Input) sodo5Input.value = '';

      window.reRenderCurationEditorInPlace();


      showToast("Đã bỏ chọn toàn bộ hình ảnh!", "success");
    };
  // === openPoolS ===
    window.openPoolS = function(systemId) {
      if (!POOL_ROWS || !POOL_ROWS.length) {
        showToast("Dữ liệu Pool chưa được nạp!", "error");
        return;
      }
      
      // Kiểm tra xem căn pool này đã lên sóng (ở Source) chưa (US-039.7)
      const curatedListing = DATA.find(x => x.system_id && String(x.system_id).trim() === String(systemId).trim());
      if (curatedListing) {
        openS(curatedListing.id);
        return;
      }
      
      const row = POOL_ROWS.find(r => String(r[72] || r[71] || '').trim() === String(systemId).trim());
      if (!row) {
        showToast("Không tìm thấy căn nhà này trong Pool thô!", "error");
        return;
      }

      // Map row to p structure
      const dt = parseFloat(row[13] || row[14]) || 0;
      const gia = parseGia(row[11] || row[58]);
      const giabq = (dt > 0 && gia > 0) ? Math.round((gia * 1000) / dt) : 0;

      let rawQ = row[3] || '';
      let cleanQ = String(rawQ).replace(/^(Quận|Q)\.?\s*/i, '').trim();
      if (cleanQ.endsWith('.0')) cleanQ = cleanQ.substring(0, cleanQ.length - 2);
      const cleanQLower = cleanQ.toLowerCase();
      if (cleanQLower.includes('phú nhuận') || cleanQLower === 'pn') cleanQ = 'pn';
      else if (cleanQLower.includes('tân bình') || cleanQLower === 'tb') cleanQ = 'tb';
      else if (cleanQLower.includes('bình thạnh') || cleanQLower === 'bt') cleanQ = 'bt';
      else if (cleanQLower.includes('gò vấp') || cleanQLower === 'gv') cleanQ = 'gv';
      else if (cleanQLower.includes('tân phú') || cleanQLower === 'tp') cleanQ = 'tp';
      else if (cleanQLower.includes('bình tân') || cleanQLower === 'btan') cleanQ = 'btan';
      else if (cleanQLower.includes('thủ đức') || cleanQLower === 'td') cleanQ = 'td';
      else if (cleanQLower.includes('hóc môn') || cleanQLower === 'hm') cleanQ = 'hm';
      else if (cleanQLower.includes('nhà bè') || cleanQLower === 'nb') cleanQ = 'nb';
      else if (cleanQLower.includes('bình chánh') || cleanQLower === 'bc') cleanQ = 'bc';
      else if (cleanQLower.includes('củ chi') || cleanQLower === 'cc') cleanQ = 'cc';

      const poolImgs = [];
      for (let c = 40; c <= 54; c++) {
        if (row[c]) poolImgs.push(row[c]);
      }
      for (let c = 83; c <= 92; c++) {
        if (row[c]) poolImgs.push(row[c]);
      }

      const p = {
        temp_id: "pool_" + systemId,
        id: row[55] || systemId || '',
        cu_phap: "",
        t: row[56] || row[55] || row[9] || 'Căn nhà thô từ Pool',
        dt: row[13] || row[14] || '',
        tang: row[15] || '',
        mat: row[16] || '',
        gia: gia,
        q: (isNaN(cleanQ) || cleanQ === '') ? cleanQ.toLowerCase() : 'q' + cleanQ,
        ql: cleanQ.toUpperCase(),
        phuong: row[4] || '-',
        loai_hinh: (row[6] || "").toString().includes(".") ? "Hẻm" : "Mặt tiền",
        huong: row[17] || '-',
        duong_truoc_nha: row[59] || '-',
        rong_hem: row[60] || '-',
        tinh_trang: row[61] || '-',
        danh_gia: row[67] || '',
        is_invisible: false,
        ngu_tang_tret: row[68] || '-',
        chdv: row[69] || '-',
        giabq: giabq > 0 ? `${giabq} tr/m²` : '-',
        m: row[57] || '',
        imgs: poolImgs,
        system_id: systemId,
        so_pn: row[64] || '-',
        img_mat_tien: row[29] || '',

        raw_ten_dau_chu: row[75] || '',
        raw_dt_dau_chu: row[74] || '',
        raw_link_fb: row[76] || '',
        raw_noi_dung_chinh: String(row[9] || '').replace(/\r\n|\r|\n/g, ' '),
        raw_mo_ta_chi_tiet: row[10] || '',
        raw_sodo1: row[27] || '',
        raw_sodo2: row[28] || '',
        raw_sodo3: row[80] || '',
        raw_sodo4: row[81] || '',
        raw_sodo5: row[82] || '',
        raw_so_nha: row[6] || '',
        raw_ten_duong: row[5] || '',
        raw_dt_thuc_te: row[13] || '',
        raw_dt_tren_so: row[14] || '',
        raw_gia_chao: row[11] || row[58] || '',
        raw_so_tang: row[15] || '',
        raw_mat_tien: row[16] || '',
        raw_duong_truoc_nha: row[59] || '',
        raw_do_rong_hem: row[60] || '',
        raw_so_pn: row[64] || '',
        raw_so_wc: row[65] || '',
        raw_tieu_de_public: row[56] || '',
        raw_mo_ta_public: row[57] || '',
        pool_row_index: POOL_ROWS.indexOf(row) + 2,

        isFromPoolOnly: true,
        pool_row_data: row
      };
      p.dai_nha = getDaiNha(p);

      openS(null, p);
    };
  // === onPoolSearchToolKeyup ===
    window.onPoolSearchToolKeyup = function() {
      const query = document.getElementById('poolSearchToolInput').value.trim();
      const resultsContainer = document.getElementById('poolSearchToolResults');
      if (!resultsContainer) return;
      resultsContainer.innerHTML = '';

      if (!query) return;

      const matched = searchPoolRows(query);
      if (matched.length === 0) {
        resultsContainer.innerHTML = '<div style="font-size: 12px; color: rgba(255,255,255,0.4); text-align: center; padding: 10px;">Không tìm thấy căn nào trong Pool thô</div>';
        return;
      }

      matched.slice(0, 10).forEach(row => {
        const isAlready = isPoolRowOnAir(row);
        const systemId = row[72] || row[71] || '';
        const id = row[55] || systemId || '';
        const soNha = row[6] || '';
        const duong = row[5] || '';
        const gia = row[11] || row[58] || '';
        const dt = row[14] || '';
        const dauChu = row[75] || '';
        const sdt = row[74] || '';

        const div = document.createElement('div');
        div.style.cssText = 'padding: 8px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; gap: 8px; cursor: pointer; transition: background 0.2s;';
        
        div.onmouseenter = () => div.style.background = 'rgba(255,255,255,0.1)';
        div.onmouseleave = () => div.style.background = 'rgba(255,255,255,0.05)';
        
        if (isAlready) {
          // If already on air, click card to open standard detail view (openS)
          div.onclick = () => openS(id);
        } else {
          // If not yet on air, click card to open raw curation detail view (openPoolS)
          div.onclick = () => openPoolS(systemId);
        }
        
        div.innerHTML = `
          <div style="flex: 1; min-width: 0; text-align: left;">
            <div style="font-size: 12px; font-weight: 700; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              🏠 ${soNha} ${duong}
            </div>
            <div style="font-size: 10.5px; color: rgba(255,255,255,0.65); margin-top: 2px;">
              💰 ${gia} tỷ - 📐 ${dt} m² - 📞 ${dauChu} (${sdt})
            </div>
          </div>
          <div style="flex-shrink: 0;">
            ${isAlready ? `
              <span style="font-size: 10.5px; font-weight: 700; color: #2ecc71; background: rgba(46, 204, 113, 0.15); padding: 4px 8px; border-radius: 6px; white-space: nowrap;">✅ Đã lên sóng</span>
            ` : `
              <button onclick="pullListingFromPoolRow(event, '${systemId}', '${id}', '${soNha.replace(/'/g, "\\'")}', '${duong.replace(/'/g, "\\'")}')" 
                style="background: #27ae60; color: white; border: none; padding: 5px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; cursor: pointer; white-space: nowrap; font-family: inherit;">
                ⚡ Lên sóng
              </button>
            `}
          </div>
        `;
        resultsContainer.appendChild(div);
      });
    };
  // === pullListingFromPoolRow ===
    window.pullListingFromPoolRow = async function(event, systemId, id, soNha, duong) {
      if (event) event.stopPropagation();
      if (!confirm(`Bạn có chắc chắn muốn lên sóng căn nhà này từ Pool không?\nĐịa chỉ: ${soNha} ${duong}`)) {
        return;
      }
      const btnElement = event.target;
      await executePullFromPool(systemId, id, soNha, duong, btnElement);
    };
  // === executePullFromPool ===
    async function executePullFromPool(systemId, id, soNha, duong, btnElement) {
      let token;
      try {
        token = await ensureValidGoogleToken();
      } catch (err) {
        alert("Không thể xác thực Google. Lên sóng thất bại: " + err.message);
        return;
      }
      
      let oldText = "";
      if (btnElement) {
        oldText = btnElement.innerHTML;
        btnElement.disabled = true;
        btnElement.innerHTML = '⌛...';
      }
      
      const POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw';
      const SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE';
      
      try {
        // Step 1: Đọc toàn bộ Sheet Pool
        const poolUrl = `https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!A2:BZ`;
        const poolRes = await fetch(poolUrl, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!poolRes.ok) {
          throw new Error(`Không thể kết nối Sheet Pool (Mã: ${poolRes.status}). Kiểm tra quyền truy cập Sheet!`);
        }
        
        const poolData = await poolRes.json();
        const rows = poolData.values || [];
        
        // Helper chuẩn hóa địa chỉ để so khớp thông minh
        const norm = (str) => {
          if (!str) return "";
          return str.toString()
                    .toLowerCase()
                    .replace(/cách mạng tháng (tám|8)|cmt8/g, "cmt8")
                    .replace(/ba tháng hai|3 tháng 2|3\/2|3\-2/g, "3/2")
                    .replace(/đường số /g, "ds")
                    .replace(/\s+/g, "")
                    .trim();
        };
        
        const targetSystemId = systemId ? systemId.trim() : "";
        const targetId = id ? id.trim() : "";
        const targetSoNha = norm(soNha);
        const targetDuong = norm(duong);
        
        const matchedRow = rows.find(r => {
          const rowSysId = r[72] || r[71] || ''; // System ID
          const rowId = r[55] || r[54] || ''; // Mã KN
          const rowSoNha = norm(r[6]);
          const rowDuong = norm(r[5]);
          return (targetSystemId && rowSysId === targetSystemId) || 
                 (targetId && rowId === targetId) ||
                 (rowSoNha === targetSoNha && rowDuong === targetDuong);
        });
        
        if (!matchedRow) {
          throw new Error(`Căn nhà này chưa được cào về kho Pool hoặc không khớp địa chỉ.`);
        }
        
        // Step 2: Đọc dữ liệu Sheet Source để tránh trùng lặp
        const sourceUrl = `https://sheets.googleapis.com/v4/spreadsheets/${SOURCE_SHEET_ID}/values/Source!A2:AO`;
        const sourceRes = await fetch(sourceUrl, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!sourceRes.ok) {
          throw new Error(`Không thể kết nối Sheet Source (Mã: ${sourceRes.status}). Kiểm tra quyền truy cập Sheet!`);
        }
        
        const sourceData = await sourceRes.json();
        const sourceRows = sourceData.values || [];
        
        const sysIdMatched = matchedRow[72] || matchedRow[71] || '';
        if (!sysIdMatched) {
          throw new Error("Dữ liệu căn nhà trong Pool thiếu System ID.");
        }
        
        const existIdx = sourceRows.findIndex(sr => sr[37] === sysIdMatched);
        const targetRowNumber = existIdx !== -1 ? (existIdx + 2) : (sourceRows.length + 2);
        
        // Step 3: Map dữ liệu 78 cột từ Pool -> 41 cột sang Source
        const finalImages = [];
        const anhDuocChon = (matchedRow[61] || "").toString().replace(/\s/g, '');
        const anhHemDuocChon = (matchedRow[62] || "").toString().replace(/\s/g, '');
        
        if (anhDuocChon === "") {
          alert("⚠️ Căn nhà này chưa được dán nhãn ảnh nội thất an toàn ở Curator App! Vui lòng nhờ Trang biên tập ảnh trước.");
          if (btnElement) {
            btnElement.disabled = false;
            btnElement.innerHTML = oldText;
          }
          return;
        }
        
        const noithatIndices = anhDuocChon.split(',');
        
        // 1. Cover
        const firstNoithatIdx = parseInt(noithatIndices[0]);
        if (!isNaN(firstNoithatIdx) && firstNoithatIdx >= 1 && firstNoithatIdx <= 25) {
          const coverImgUrl = matchedRow[window.getPoolInteriorColIdx(firstNoithatIdx)];
          if (coverImgUrl) finalImages.push(coverImgUrl);
        }
        
        // 2. Alley
        const maxHem = 2;
        if (anhHemDuocChon !== "") {
          const hemIndices = anhHemDuocChon.split(',');
          let addedHem = 0;
          for (let i = 0; i < hemIndices.length && addedHem < maxHem; i++) {
            const hemIdx = parseInt(hemIndices[i]);
            if (!isNaN(hemIdx) && hemIdx >= 1 && hemIdx <= 10) {
              const hemUrl = matchedRow[window.getPoolAlleyColIdx(hemIdx)];
              if (hemUrl) {
                finalImages.push(hemUrl);
                addedHem++;
              }
            }
          }
        } else {
          const availableHem = [];
          for (let i = 1; i <= 10; i++) {
            const hemUrl = matchedRow[window.getPoolAlleyColIdx(i)];
            if (hemUrl) availableHem.push(hemUrl);
          }
          for (let i = availableHem.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            const temp = availableHem[i];
            availableHem[i] = availableHem[j];
            availableHem[j] = temp;
          }
          for (let i = 0; i < Math.min(maxHem, availableHem.length); i++) {
            finalImages.push(availableHem[i]);
          }
        }
        
        // 3. Nội thất khác
        for (let i = 1; i < noithatIndices.length; i++) {
          const imgIdx = parseInt(noithatIndices[i]);
          if (!isNaN(imgIdx) && imgIdx >= 1 && imgIdx <= 25) {
            const imgUrl = matchedRow[window.getPoolInteriorColIdx(imgIdx)];
            if (imgUrl) finalImages.push(imgUrl);
          }
        }
        
        while (finalImages.length < 15) finalImages.push("");
        
        // Xử lý Cú pháp (Lấy từ Nội dung chính thô)
        const noiDungChinh = matchedRow[9] || "";
        let cuPhap = noiDungChinh;
        const matchCuPhap = noiDungChinh.match(/^(.*?Quận\s+[a-z0-9àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ\s]+?)\s+[\d\.]+(?:-[\d\.]+)?\s*tỷ/i);
        if (matchCuPhap) {
          cuPhap = matchCuPhap[1].trim();
        }
        
        // Xử lý Quận
        const formatQuan = (q) => {
          if (!q) return "";
          const qLower = q.toLowerCase();
          if (qLower.includes("quận 3")) return "3";
          if (qLower.includes("quận 10")) return "10";
          if (qLower.includes("phú nhuận")) return "PN";
          if (qLower.includes("tân bình")) return "TB";
          return q;
        };
        
        // Xử lý Giá
        const formatGia = (g) => {
          if (!g) return "";
          const val = parseFloat(g.toString().replace(/,/g, ''));
          if (isNaN(val)) return g;
          if (val > 100) return val / 1000;
          return val;
        };
        
        const loaiHinh = (matchedRow[6] || "").toString().includes(".") ? "Hẻm" : "Mặt tiền";
        
        // Xây dựng publicRowData 46 cột cho Sheet Source
        const publicRowData = [
          `=IMAGE(AM${targetRowNumber})`, // 0: Hinh_mat_tien (Cột A)
          cuPhap,                        // 1: Cu_phap (Cột B)
          "",                            // 2: Note (Cột C)
          matchedRow[55],                // 3: id (Cột D)
          matchedRow[56],                // 4: tieu_de (Cột E)
          matchedRow[13],                // 5: dien_tich (Cột F)
          matchedRow[15],                // 6: so_tang (Cột G)
          matchedRow[16],                // 7: mat_tien (Cột H)
          formatGia(matchedRow[11] || matchedRow[58]),     // 8: gia (Cột I)
          formatQuan(matchedRow[3]),     // 9: quan (Cột J)
          matchedRow[4],                 // 10: phuong (Cột K)
          loaiHinh,                      // 11: loai_hinh (Cột L)
          matchedRow[17],                // 12: huong_nha (Cột M)
          matchedRow[59],                // 13: duong_truoc_nha (Cột N)
          matchedRow[60],                // 14: do_rong_hem (Cột O)
          matchedRow[61],                // 15: tinh_trang_nha (Cột P)
          matchedRow[67],                // 16: danh_gia (Cột Q)
          matchedRow[68],                // 17: ngu_tang_tret (Cột R)
          matchedRow[69],                // 18: chdv (Cột S)
          matchedRow[57],                // 19: mo_ta (Cột T)
          finalImages[0],                // 20: anh_1 (Cột U)
          finalImages[1],                // 21: anh_2 (Cột V)
          finalImages[2],                // 22: anh_3 (Cột W)
          finalImages[3],                // 23: anh_4 (Cột X)
          finalImages[4],                // 24: anh_5 (Cột Y)
          finalImages[5],                // 25: anh_6 (Cột Z)
          finalImages[6],                // 26: anh_7 (Cột AA)
          finalImages[7],                // 27: anh_8 (Cột AB)
          finalImages[8],                // 28: anh_9 (Cột AC)
          finalImages[9],                // 29: anh_10 (Cột AD)
          new Date().toISOString(),      // 30: Last updated (Cột AE)
          (window.activeCurationListing && window.activeCurationListing.phuong_cu) || matchedRow[66] || "", // 31: phuong_cu (Cột AF)
          matchedRow[64],                // 32: so_pn (Cột AG)
          matchedRow[65],                // 33: so_wc (Cột AH)
          matchedRow[5],                 // 34: ten_duong (Cột AI)
          "",                            // 35: gio_dang (Cột AJ)
          "",                            // 36: trang_thai (Cột AK)
          sysIdMatched,                  // 37: System ID (Cột AL)
          matchedRow[29],                // 38: Hình Mặt Tiền (Cột AM)
          "",                            // 39: Tiêu đề BDS (Cột AN)
          false,                         // 40: Đăng BDS (Cột AO)
          finalImages[10] || "",         // 41: anh_11 (Cột AP)
          finalImages[11] || "",         // 42: anh_12 (Cột AQ)
          finalImages[12] || "",         // 43: anh_13 (Cột AR)
          finalImages[13] || "",         // 44: anh_14 (Cột AS)
          finalImages[14] || ""          // 45: anh_15 (Cột AT)
        ];
        
        // Step 4: Ghi đè/Thêm mới vào Sheet Source
        const writeUrl = `https://sheets.googleapis.com/v4/spreadsheets/${SOURCE_SHEET_ID}/values/Source!A${targetRowNumber}:AT${targetRowNumber}?valueInputOption=USER_ENTERED`;
        const writeRes = await fetch(writeUrl, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ values: [publicRowData] })
        });
        
        if (!writeRes.ok) {
          let detail = "";
          try {
            const errJson = await writeRes.json();
            detail = ": " + (errJson.error?.message || JSON.stringify(errJson));
          } catch (e) {}
          throw new Error(`Không thể ghi dữ liệu sang Sheet Source (Mã: ${writeRes.status}${detail}).`);
        }
        
        // Cập nhật lại trường Last Sync của dòng đó bên Sheet Pool
        try {
          const poolRowNumber = rows.indexOf(matchedRow) + 2;
          const syncDateStr = new Date().toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" });
          await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!CA${poolRowNumber}:CA${poolRowNumber}?valueInputOption=USER_ENTERED`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ values: [[syncDateStr]] })
          });
        } catch (e) {
          console.warn("Không thể ghi nhận Last Sync vào Pool:", e);
        }
        
        alert(`🎉 Đã đồng bộ lên sóng thành công căn nhà #${matchedRow[55]} (${matchedRow[56]})!`);
        
        // Reset ô tìm kiếm Pool trong Bộ lọc
        const pullInput = document.getElementById('poolSearchToolInput');
        if (pullInput) pullInput.value = '';
        const pullResults = document.getElementById('poolSearchToolResults');
        if (pullResults) pullResults.innerHTML = '';

        // Tải lại dữ liệu web
        secureLoadAttempted = false;
        isSecureLoaded = false;
        isDataLoaded = false;
        loadData();
        
      } catch (err) {
        alert(`❌ Lỗi đồng bộ: ${err.message}`);
        console.error(err);
      } finally {
        if (btnElement) {
          btnElement.disabled = false;
          btnElement.innerHTML = oldText;
        }
      }
    }
  // === toggleAdminAccordion ===
    window.toggleAdminAccordion = function(header) {
      const item = header.closest('.accordion-item');
      const arrow = header.querySelector('.arrow');
      const isExpanded = item.classList.contains('expanded');
      
      if (isExpanded) {
        item.classList.remove('expanded');
        if (arrow) arrow.textContent = '▶';
      } else {
        item.classList.add('expanded');
        if (arrow) arrow.textContent = '▼';
      }
    };
  // === getPublicImagesFromForm ===
    window.getPublicImagesFromForm = function(p, customPoolRowData) {
      if (!p) return [];
      const poolRowData = customPoolRowData || p.pool_row_data;
      const customCoverUrl = (document.getElementById('editCoverImgUrl')?.value || '').trim();
      const publicCoverUrl = (document.getElementById('editPublicCoverUrl')?.value || '').trim();
      const publicIntStr = (document.getElementById('editPublicInteriorIndices')?.value || '').trim();
      const publicAlleyStr = (document.getElementById('editPublicAlleyIndices')?.value || '').trim();

      const targetMatTien = customCoverUrl || p.img_mat_tien || (poolRowData ? poolRowData[29] : '') || '';
      const normMatTien = normalizeImgUrl(targetMatTien);
      const isFacadeUrl = (url) => {
        if (!url) return false;
        const norm = normalizeImgUrl(url);
        return norm !== '' && norm === normMatTien;
      };

      if (poolRowData) {
        const noithatIndices = publicIntStr.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n) && n >= 1 && n <= 25);
        const hemIndices = publicAlleyStr.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n) && n >= 1 && n <= 10);

        const sodo1Url = (document.getElementById('editSodo1Url')?.value || (poolRowData ? poolRowData[window.getPoolSodoColIdx(1)] : p.raw_sodo1) || '').trim();
        const sodo2Url = (document.getElementById('editSodo2Url')?.value || (poolRowData ? poolRowData[window.getPoolSodoColIdx(2)] : p.raw_sodo2) || '').trim();
        const sodo3Url = (document.getElementById('editSodo3Url')?.value || (poolRowData ? poolRowData[window.getPoolSodoColIdx(3)] : p.raw_sodo3) || '').trim();
        const sodo4Url = (document.getElementById('editSodo4Url')?.value || (poolRowData ? poolRowData[window.getPoolSodoColIdx(4)] : p.raw_sodo4) || '').trim();
        const sodo5Url = (document.getElementById('editSodo5Url')?.value || (poolRowData ? poolRowData[window.getPoolSodoColIdx(5)] : p.raw_sodo5) || '').trim();
        const normSodos = [sodo1Url, sodo2Url, sodo3Url, sodo4Url, sodo5Url].map(url => normalizeImgUrl(url));
        const isSodoUrl = (url) => {
          if (!url) return false;
          const norm = normalizeImgUrl(url);
          return norm !== '' && normSodos.includes(norm);
        };

        const finalImages = [];
        let publicCover = publicCoverUrl;
        if (publicCover && ((window.isListingSodoUrl && window.isListingSodoUrl(publicCover, p)) || isFacadeUrl(publicCover))) {
          publicCover = '';
        }
        if (!publicCover) {
          const candidates = [];
          const interior1Idx = window.getPoolInteriorColIdx(1);
          if (poolRowData[interior1Idx] && (!window.isListingSodoUrl || !window.isListingSodoUrl(poolRowData[interior1Idx], p)) && !isFacadeUrl(poolRowData[interior1Idx])) {
            candidates.push(poolRowData[interior1Idx]);
          }
          // poolRowData[29] (raw facade) is completely excluded!
          for (let i = 0; i < noithatIndices.length; i++) {
            const url = poolRowData[window.getPoolInteriorColIdx(noithatIndices[i])];
            if (url && (!window.isListingSodoUrl || !window.isListingSodoUrl(url, p)) && !isFacadeUrl(url)) {
              candidates.push(url);
              break;
            }
          }
          publicCover = candidates[0] || '';
        }

        if (publicCover && (!window.isListingSodoUrl || !window.isListingSodoUrl(publicCover, p)) && !isFacadeUrl(publicCover)) {
          finalImages.push(publicCover);
        }
        
        const maxHem = 2;
        let addedHem = 0;
        for (let i = 0; i < hemIndices.length && addedHem < maxHem; i++) {
          const hemIdx = hemIndices[i];
          const hemUrl = poolRowData[window.getPoolAlleyColIdx(hemIdx)];
          if (hemUrl && (!window.isListingSodoUrl || !window.isListingSodoUrl(hemUrl, p)) && !isFacadeUrl(hemUrl)) {
            finalImages.push(hemUrl);
            addedHem++;
          }
        }
        
        for (let i = 0; i < noithatIndices.length; i++) {
          const imgIdx = noithatIndices[i];
          const imgUrl = poolRowData[window.getPoolInteriorColIdx(imgIdx)];
          if (imgUrl && imgUrl !== publicCover && (!window.isListingSodoUrl || !window.isListingSodoUrl(imgUrl, p)) && !isFacadeUrl(imgUrl) && finalImages.length < 15) {
            finalImages.push(imgUrl);
          }
        }
        return finalImages.filter(Boolean);
      } else {
        const finalImages = [];
        const publicCover = publicCoverUrl || (p.imgs && p.imgs[0]);
        if (publicCover && (!window.isListingSodoUrl || !window.isListingSodoUrl(publicCover, p)) && !isFacadeUrl(publicCover)) {
          finalImages.push(publicCover);
        }
        
        if (p.imgs) {
          p.imgs.forEach(url => {
            if (url && url !== publicCover && !finalImages.includes(url) && (!window.isListingSodoUrl || !window.isListingSodoUrl(url, p)) && !isFacadeUrl(url)) {
              finalImages.push(url);
            }
          });
        }
        return finalImages.slice(0, 15).filter(Boolean);
      }
    };
  // === openZoomOverlay ===
    window.openZoomOverlay = function(url) {
      let overlay = document.getElementById('zoomOverlay');
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'zoomOverlay';
        overlay.style.cssText = `
          position: fixed;
          top: 0; left: 0; right: 0; bottom: 0;
          background: rgba(0,0,0,0.95);
          z-index: 100000;
          display: flex;
          align-items: center;
          justify-content: center;
          opacity: 0;
          transition: opacity 0.3s ease;
          pointer-events: none;
        `;
        overlay.innerHTML = `
          <div style="position: absolute; top: 16px; right: 16px; width: 40px; height: 40px; border-radius: 50%; background: rgba(255,255,255,0.1); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; cursor: pointer; z-index: 100001;" onclick="closeZoomOverlay()">✕</div>
          <img src="" style="max-width: 95%; max-height: 90%; object-fit: contain; transition: transform 0.15s ease-out; transform-origin: center center;" id="zoomImg">
        `;
        document.body.appendChild(overlay);

        const img = overlay.querySelector('#zoomImg');
        let scale = 1;
        let startDist = 0;
        let lastScale = 1;
        let isDragging = false;
        let startX = 0, startY = 0;
        let posX = 0, posY = 0;

        img.ontouchstart = (e) => {
          if (e.touches.length === 2) {
            startDist = Math.hypot(
              e.touches[0].clientX - e.touches[1].clientX,
              e.touches[0].clientY - e.touches[1].clientY
            );
          } else if (e.touches.length === 1) {
            isDragging = true;
            startX = e.touches[0].clientX - posX;
            startY = e.touches[0].clientY - posY;
          }
        };

        img.ontouchmove = (e) => {
          if (e.touches.length === 2 && startDist > 0) {
            const dist = Math.hypot(
              e.touches[0].clientX - e.touches[1].clientX,
              e.touches[0].clientY - e.touches[1].clientY
            );
            scale = Math.max(1, Math.min(4, lastScale * (dist / startDist)));
            img.style.transform = `translate(${posX}px, ${posY}px) scale(${scale})`;
          } else if (e.touches.length === 1 && isDragging && scale > 1) {
            posX = e.touches[0].clientX - startX;
            posY = e.touches[0].clientY - startY;
            img.style.transform = `translate(${posX}px, ${posY}px) scale(${scale})`;
          }
        };

        img.ontouchend = (e) => {
          lastScale = scale;
          isDragging = false;
          if (scale <= 1.05) {
            posX = 0; posY = 0; scale = 1; lastScale = 1;
            img.style.transform = 'translate(0px, 0px) scale(1)';
          }
        };

        overlay.onclick = (e) => {
          if (e.target === overlay) closeZoomOverlay();
        };
      }

      const img = overlay.querySelector('#zoomImg');
      img.src = url;
      img.style.transform = 'translate(0px, 0px) scale(1)';
      
      overlay.style.pointerEvents = 'auto';
      overlay.style.opacity = '1';
      
      window.closeZoomOverlay = function() {
        overlay.style.opacity = '0';
        overlay.style.pointerEvents = 'none';
      };
    };
  // === checkMoTaCollapse ===
    window.checkMoTaCollapse = function() {
      const box = document.getElementById('adminMotaGocBox');
      const btn = document.getElementById('btnExpandMotaGoc');
      if (!box || !btn) return;
      
      box.classList.remove('expanded');
      btn.textContent = 'Xem thêm ▼';
      
      const scrollHeight = box.scrollHeight;
      if (scrollHeight > 165) {
        btn.style.display = 'block';
      } else {
        btn.style.display = 'none';
      }
    };
  // === toggleMotaGocCollapse ===
    window.toggleMotaGocCollapse = function() {
      const box = document.getElementById('adminMotaGocBox');
      const btn = document.getElementById('btnExpandMotaGoc');
      if (!box || !btn) return;
      
      const isExpanded = box.classList.contains('expanded');
      if (isExpanded) {
        box.classList.remove('expanded');
        btn.textContent = 'Xem thêm ▼';
        document.getElementById('sbody').scrollTop -= 100;
      } else {
        box.classList.add('expanded');
        btn.textContent = 'Thu gọn ▲';
      }
    };
  // === saveSourceChanges ===
    window.saveSourceChanges = async function(id) {
      const p = DATA.find(x => String(x.id) === String(id));
      if (!p) {
        showToast("Không tìm thấy thông tin căn nhà!", "error");
        return;
      }

      let token;
      try {
        token = await ensureValidGoogleToken();
      } catch (err) {
        showToast("Không thể xác thực Google. Lưu thất bại: " + err.message, "error");
        return;
      }

      const saveBtn = document.getElementById('saveSourceBtn') || document.getElementById('saveBtn');
      if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '⌛';
      }

      try {
        const note = document.getElementById('editNote').value.trim();
        const tieuDeBds = document.getElementById('editTieuDeBds').value.trim();
        const moTaBds = document.getElementById('editMoTaBds').value.trim();
        const huong = document.getElementById('editHuong').value;
        const duong = document.getElementById('editDuong').value;
        const danhGia = document.getElementById('editDanhGia').value;
        const tinhTrang = document.getElementById('editTinhTrang').value;
        const editDuongTruocNhaEl = document.getElementById('editDuongTruocNha');
        const rongHem = editDuongTruocNhaEl ? editDuongTruocNhaEl.value.trim() : (p.raw_duong_truoc_nha || p.duong_truoc_nha || '');
        const soPn = document.getElementById('editSoPn').value.trim();
        const soWc = document.getElementById('editSoWc').value.trim();
        const nguTret = document.getElementById('editNguTret').checked ? 'Có' : 'Không';
        const chdv = document.getElementById('editChdv').checked ? 'Có' : 'Không';

        // Đọc dữ liệu hình ảnh được chọn từ form biên tập hình ảnh trực quan
        const customCoverUrl = document.getElementById('editCoverImgUrl').value.trim();
        const publicCoverUrl = document.getElementById('editPublicCoverUrl').value.trim();
        const publicIntStr = document.getElementById('editPublicInteriorIndices').value.trim();
        const publicAlleyStr = document.getElementById('editPublicAlleyIndices').value.trim();
        const sodo1Url = document.getElementById('editSodo1Url').value.trim();
        const sodo2Url = document.getElementById('editSodo2Url').value.trim();
        const sodo3Url = document.getElementById('editSodo3Url').value.trim();
        const sodo4Url = document.getElementById('editSodo4Url').value.trim();
        const sodo5Url = document.getElementById('editSodo5Url').value.trim();

        const normSodos = [sodo1Url, sodo2Url, sodo3Url, sodo4Url, sodo5Url].map(url => normalizeImgUrl(url));
        
        const isSodoUrl = (url) => {
          if (!url) return false;
          const norm = normalizeImgUrl(url);
          if (norm === '') return false;
          return normSodos.includes(norm);
        };

        const normMatTien = normalizeImgUrl(customCoverUrl || p.img_mat_tien || (p.pool_row_data ? p.pool_row_data[29] : ''));
        const isFacadeUrl = (url) => {
          if (!url) return false;
          const norm = normalizeImgUrl(url);
          return norm !== '' && norm === normMatTien;
        };

        // Chỉ cập nhật lại mảng ảnh và cover nếu form có nạp hình ảnh
        const finalImages = p.pool_row_data ? window.getPublicImagesFromForm(p) : [];
        if (p.pool_row_data) {
          while (finalImages.length < 15) finalImages.push("");
        }

        const cleanPublicImages = [];
        if (p.pool_row_data && p.original_row_data) {
          // Pad original_row_data to 46 columns in legacy mode
          while (p.original_row_data.length < 46) p.original_row_data.push("");

          for (let i = 20; i <= 29; i++) {
            const url = p.original_row_data[i];
            if (url && !isSodoUrl(url) && !isFacadeUrl(url) && !cleanPublicImages.includes(url)) {
              cleanPublicImages.push(url);
            }
          }
          for (let i = 41; i <= 45; i++) {
            const url = p.original_row_data[i];
            if (url && !isSodoUrl(url) && !isFacadeUrl(url) && !cleanPublicImages.includes(url)) {
              cleanPublicImages.push(url);
            }
          }
          
          if (publicCoverUrl && !isSodoUrl(publicCoverUrl) && !isFacadeUrl(publicCoverUrl)) {
            if (!cleanPublicImages.includes(publicCoverUrl)) {
              cleanPublicImages.unshift(publicCoverUrl);
            } else {
              const idx = cleanPublicImages.indexOf(publicCoverUrl);
              if (idx !== -1) cleanPublicImages.splice(idx, 1);
              cleanPublicImages.unshift(publicCoverUrl);
            }
          }

          while (cleanPublicImages.length < 15) {
            cleanPublicImages.push("");
          }
        }

        const setVal = (names, defaultIdx, val) => {
          if (p.original_row_data) {
            const headers = window.LegoState?.sourceHeaders || [];
            let mapped = false;
            for (const name of names) {
              const idx = headers.indexOf(name);
              if (idx >= 0) {
                while (p.original_row_data.length <= idx) p.original_row_data.push("");
                p.original_row_data[idx] = val;
                mapped = true;
                break;
              }
            }
            if (!mapped && defaultIdx >= 0) {
              while (p.original_row_data.length <= defaultIdx) p.original_row_data.push("");
              p.original_row_data[defaultIdx] = val;
            }
          }
        };

        if (p.original_row_data) {
          const headers = window.LegoState?.sourceHeaders || [];
          if (headers.indexOf("images_metadata_json") >= 0) {
            const metaImages = (cleanPublicImages.length ? cleanPublicImages : finalImages).filter(Boolean).map(url => {
              return { url: url, role: "interior" };
            });
            setVal(["images_metadata_json"], -1, JSON.stringify(metaImages));
          } else {
            // Pool1 legacy flat columns index
            const imgsToUse = cleanPublicImages.length ? cleanPublicImages : finalImages;
            for (let i = 0; i < 10; i++) {
              p.original_row_data[20 + i] = imgsToUse[i] || "";
            }
            for (let i = 10; i < 15; i++) {
              p.original_row_data[31 + i] = imgsToUse[i] || "";
            }
          }
          p.imgs = (cleanPublicImages.length ? cleanPublicImages : finalImages).filter(Boolean);
        }

        setVal(["Note_Noi_Bo", "Note"], 2, note);
        setVal(["Huong", "huong_nha"], 12, huong);
        setVal(["Criteria_Duong_truoc_nha", "duong_truoc_nha"], 13, duong);
        setVal(["Custom_Rong_Hem", "do_rong_hem"], 14, rongHem || '-');
        setVal(["Trang_Thai_Giao_Dich", "Trang_Thai_KN", "tinh_trang_nha"], 15, tinhTrang);
        setVal(["danh_gia"], 16, danhGia);
        setVal(["Ngu_Tret", "ngu_tang_tret"], 17, nguTret);
        setVal(["CHDV", "chdv"], 18, chdv);
        setVal(["Mo_ta_Public", "mo_ta"], 19, moTaBds);
        setVal(["Last updated"], 30, new Date().toISOString());
        setVal(["bedrooms", "so_pn"], 32, soPn || '-');
        setVal(["restrooms", "so_wc"], 33, soWc || '-');
        setVal(["Tieu_De_Public", "tieu_de"], 4, tieuDeBds);
        setVal(["Tiêu đề BDS"], 39, "");
        setVal(["Hình Mặt Tiền", "Hinh_mat_tien"], 38, customCoverUrl);

        p.img_mat_tien = customCoverUrl;
        p.t = tieuDeBds;
        p.note = note;
        p.huong = huong;
        p.duong_truoc_nha = duong;
        p.rong_hem = rongHem || '-';
        p.tinh_trang = tinhTrang;
        p.danh_gia = danhGia;
        p.ngu_tang_tret = nguTret;
        p.chdv = chdv;
        p.so_pn = soPn || '-';
        p.m = moTaBds;

        const SOURCE_SHEET_ID = window.LegoState?.config?.source_sheet_id || '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE';
        const sourceTab = (window.LegoState?.config?.active_pool_system === 'Pool2') ? 'Custom' : 'Source';
        
        const getColLetter = (n) => {
          let col = "";
          while (n > 0) {
            let rem = (n - 1) % 26;
            col = String.fromCharCode(65 + rem) + col;
            n = Math.floor((n - rem) / 26);
          }
          return col || "AT";
        };
        const headersLength = window.LegoState?.sourceHeaders?.length || 46;
        const colLetter = getColLetter(headersLength);

        const writeUrl = `https://sheets.googleapis.com/v4/spreadsheets/${SOURCE_SHEET_ID}/values/${sourceTab}!A${p.source_row_index}:${colLetter}${p.source_row_index}?valueInputOption=USER_ENTERED`;

        const writeRes = await fetch(writeUrl, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ values: [p.original_row_data] })
        });

        if (!writeRes.ok) {
          let detail = "";
          try {
            const errJson = await writeRes.json();
            detail = ": " + (errJson.error?.message || JSON.stringify(errJson));
          } catch (e) {}
          throw new Error(`Google Sheets API returned status ${writeRes.status}${detail}`);
        }

        // Cập nhật lại các trường ảnh đã biên tập sang tab Pool (nếu có smart match)
        // Cập nhật lại các trường ảnh đã biên tập sang tab Pool (nếu có smart match)
        if (p.pool_row_index && p.pool_row_data && window.LegoState?.config?.active_pool_system !== 'Pool2') {
          const POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw';
          
          // 1. Đồng bộ các ảnh Sổ thửa đất (cột AB:AC)
          try {
            await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!AB${p.pool_row_index}:AC${p.pool_row_index}?valueInputOption=USER_ENTERED`, {
              method: 'PUT',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ values: [[sodo1Url, sodo2Url]] })
            });
            p.pool_row_data[27] = sodo1Url;
            p.pool_row_data[28] = sodo2Url;
            p.raw_sodo1 = sodo1Url;
            p.raw_sodo2 = sodo2Url;
          } catch (e) {
            console.warn("Không thể đồng bộ thay đổi Sổ sang Pool thô:", e);
          }

          // 1b. Đồng bộ Hình Mặt Tiền (Cột AD) và Ảnh Bìa / Ảnh 1 (Cột AO) sang Pool thô (US-046.6)
          try {
            await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!AD${p.pool_row_index}:AD${p.pool_row_index}?valueInputOption=USER_ENTERED`, {
              method: 'PUT',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ values: [[customCoverUrl]] })
            });
            p.pool_row_data[29] = customCoverUrl;
            p.img_mat_tien = customCoverUrl;
          } catch (e) {
            console.warn("Không thể đồng bộ Hình Mặt Tiền sang Pool:", e);
          }



          // 1a. Đồng bộ Sổ 3-5 (CC:CE)
          try {
            const sodo3Url = document.getElementById('editSodo3Url').value.trim();
            const sodo4Url = document.getElementById('editSodo4Url').value.trim();
            const sodo5Url = document.getElementById('editSodo5Url').value.trim();
            await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!CC${p.pool_row_index}:CE${p.pool_row_index}?valueInputOption=USER_ENTERED`, {
              method: 'PUT',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ values: [[sodo3Url, sodo4Url, sodo5Url]] })
            });
            p.pool_row_data[80] = sodo3Url;
            p.pool_row_data[81] = sodo4Url;
            p.pool_row_data[82] = sodo5Url;
            p.raw_sodo3 = sodo3Url;
            p.raw_sodo4 = sodo4Url;
            p.raw_sodo5 = sodo5Url;
          } catch (e) {
            console.warn("Không thể đồng bộ thay đổi Sổ 3-5 sang Pool thô:", e);
          }

          // 1b. Đồng bộ Ảnh Nội Thất 1-15 sang Pool (cột AO:BC)
          try {
            const int1_15 = [];
            for (let c = 40; c <= 54; c++) {
              int1_15.push(p.pool_row_data[c] || "");
            }
            await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!AO${p.pool_row_index}:BC${p.pool_row_index}?valueInputOption=USER_ENTERED`, {
              method: 'PUT',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ values: [int1_15] })
            });
          } catch (e) {
            console.warn("Không thể đồng bộ Ảnh Nội Thất 1-15 sang Pool:", e);
          }

          // 1c. Đồng bộ Ảnh Nội Thất 16-25 sang Pool (cột CF:CO)
          try {
            const int16_25 = [];
            for (let c = 83; c <= 92; c++) {
              int16_25.push(p.pool_row_data[c] || "");
            }
            await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!CF${p.pool_row_index}:CO${p.pool_row_index}?valueInputOption=USER_ENTERED`, {
              method: 'PUT',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ values: [int16_25] })
            });
          } catch (e) {
            console.warn("Không thể đồng bộ Ảnh Nội Thất 16-25 sang Pool:", e);
          }

          // 2. Đồng bộ chỉ số ảnh public (cột BK:BL)
          try {
            await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!BK${p.pool_row_index}:BL${p.pool_row_index}?valueInputOption=USER_ENTERED`, {
              method: 'PUT',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ values: [[publicIntStr, publicAlleyStr]] })
            });
            
            // Cập nhật lại biến client-side để đồng bộ
            p.pool_row_data[62] = publicIntStr;
            p.pool_row_data[63] = publicAlleyStr;
          } catch (e) {
            console.warn("Không thể đồng bộ thay đổi hình ảnh sang Pool thô:", e);
          }
        }

        showToast("Đã lưu thay đổi lên Google Sheets thành công!", "success");
        
        // Re-render list cards in the background to reflect changes in-place
        if (typeof render === 'function') {
          render();
        }

        // Focus and expand the Customer Preview section in-place without page reload (US-046.4)
        const accPreview = document.getElementById('accPreview');
        if (accPreview) {
          accPreview.classList.add('expanded');
          const content = accPreview.querySelector('.accordion-content');
          if (content) content.style.maxHeight = content.scrollHeight + 'px';
          const arrow = accPreview.querySelector('.arrow');
          if (arrow) arrow.style.transform = 'rotate(180deg)';
          
          setTimeout(() => {
            accPreview.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }, 300);
        }
      } catch (err) {
        console.error("Lỗi lưu dữ liệu:", err);
        showToast(`Lỗi lưu thay đổi: ${err.message}`, "error");
      } finally {
        if (saveBtn) {
          saveBtn.disabled = false;
          saveBtn.innerHTML = '💾';
        }
      }
    };
  // === saveNewListingFromPool ===
    window.saveNewListingFromPool = async function(systemId, btnElement) {
      let token;
      try {
        token = await ensureValidGoogleToken();
      } catch (err) {
        showToast("Không thể xác thực Google. Lưu thất bại: " + err.message, "error");
        return;
      }
      
      let oldText = "";
      if (btnElement) {
        oldText = btnElement.innerHTML;
        btnElement.disabled = true;
        btnElement.innerHTML = '⌛';
      }
      
      const POOL_SHEET_ID = window.LegoState?.config?.pool_sheet_id || '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw';
      const SOURCE_SHEET_ID = window.LegoState?.config?.source_sheet_id || '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE';
      const poolTab = (window.LegoState?.config?.active_pool_system === 'Pool2') ? 'Listings' : 'Pool';
      const sourceTab = (window.LegoState?.config?.active_pool_system === 'Pool2') ? 'Custom' : 'Source';
      
      try {
        // Step 1: Đọc Sheet Pool để lấy dòng gốc (đọc từ A1 để lấy headers)
        const poolUrl = `https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/${poolTab}!A1:ZZ`;
        const poolRes = await fetch(poolUrl, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!poolRes.ok) {
          throw new Error(`Không thể kết nối Sheet Pool (Mã: ${poolRes.status}).`);
        }
        
        const poolData = await poolRes.json();
        const poolRows = poolData.values || [];
        
        const knownHeaderKeywords = ["System_ID", "System ID", "Ma_Khang_Ngo", "Ma_Khang_Ngo (ID)", "Ma Khang Ngô", "Noi_dung_chinh", "Nội dung chính", "Mo_ta_Public", "Mô tả Public", "images_metadata_json", "id", "tieu_de"];
        const isHeader = (row) => {
          if (!row || row.length === 0) return false;
          return row.some(cell => {
            const val = String(cell || '').trim();
            return knownHeaderKeywords.includes(val);
          });
        };

        const isPoolHeader = isHeader(poolRows[0]);
        const poolHeaders = isPoolHeader ? poolRows[0] : [];
        if (window.LegoState && !window.LegoState.poolHeaders) {
          window.LegoState.poolHeaders = poolHeaders;
        }

        const dataRows = isPoolHeader ? poolRows.slice(1) : poolRows;
        const poolHeadersLength = poolHeaders.length > 0 ? poolHeaders.length : 93;
        dataRows.forEach(r => {
          while (r.length < poolHeadersLength) r.push("");
        });
        
        const getPoolVal = (row, names, defaultIdx) => {
          const headers = window.LegoState?.poolHeaders || poolHeaders || [];
          for (const name of names) {
            const idx = headers.indexOf(name);
            if (idx >= 0) return row[idx] !== undefined ? row[idx] : '';
          }
          return defaultIdx >= 0 && row[defaultIdx] !== undefined ? row[defaultIdx] : '';
        };

        const getPoolColIdx = (names, defaultIdx) => {
          const headers = window.LegoState?.poolHeaders || poolHeaders || [];
          for (const name of names) {
            const idx = headers.indexOf(name);
            if (idx >= 0) return idx;
          }
          return defaultIdx;
        };

        const sysIdIdx = getPoolColIdx(["System_ID", "System ID"], 72);
        const matchedRow = dataRows.find(r => String(r[sysIdIdx] || '').trim() === String(systemId).trim());
        if (!matchedRow) {
          throw new Error("Không tìm thấy căn nhà này trong kho Pool hoặc không khớp System ID.");
        }

        if (window.LegoState?.config?.active_pool_system !== 'Pool2') {
          const p = window.activeCurationListing;
          if (p && p.pool_row_data) {
            matchedRow[27] = p.pool_row_data[27] || "";
            matchedRow[28] = p.pool_row_data[28] || "";
            matchedRow[80] = p.pool_row_data[80] || "";
            matchedRow[81] = p.pool_row_data[81] || "";
            matchedRow[82] = p.pool_row_data[82] || "";
            for (let c = 30; c <= 39; c++) matchedRow[c] = p.pool_row_data[c] || "";
            for (let c = 40; c <= 54; c++) matchedRow[c] = p.pool_row_data[c] || "";
            for (let c = 83; c <= 92; c++) matchedRow[c] = p.pool_row_data[c] || "";
          }
        }

        // Đọc dữ liệu từ form trong modal
        const note = document.getElementById('editNote').value.trim();
        const maKhangNgo = document.getElementById('editMaKhangNgo').value.trim();
        const tieuDeBds = document.getElementById('editTieuDeBds').value.trim();
        const moTaBds = document.getElementById('editMoTaBds').value.trim();
        const huong = document.getElementById('editHuong').value;
        const duong = document.getElementById('editDuong').value;
        const danhGia = document.getElementById('editDanhGia').value;
        const tinhTrang = document.getElementById('editTinhTrang').value;
        const editDuongTruocNhaEl = document.getElementById('editDuongTruocNha');
        const rongHem = editDuongTruocNhaEl ? editDuongTruocNhaEl.value.trim() : '';
        const soPn = document.getElementById('editSoPn').value.trim();
        const soWc = document.getElementById('editSoWc').value.trim();
        const nguTret = document.getElementById('editNguTret').checked ? 'Có' : 'Không';
        const chdv = document.getElementById('editChdv').checked ? 'Có' : 'Không';

        if (!maKhangNgo) {
          throw new Error("Vui lòng điền Mã Khang Ngô!");
        }
        
        // Step 2: Đọc dữ liệu Sheet Source để tránh trùng lặp và xác định vị trí ghi
        const sourceUrl = `https://sheets.googleapis.com/v4/spreadsheets/${SOURCE_SHEET_ID}/values/${sourceTab}!A1:ZZ`;
        const sourceRes = await fetch(sourceUrl, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!sourceRes.ok) {
          throw new Error(`Không thể kết nối Sheet Source (Mã: ${sourceRes.status}).`);
        }
        
        const sourceData = await sourceRes.json();
        const sourceRows = sourceData.values || [];
        const isSourceHeader = isHeader(sourceRows[0]);
        const sourceHeaders = isSourceHeader ? sourceRows[0] : [];
        
        if (window.LegoState && !window.LegoState.sourceHeaders) {
          window.LegoState.sourceHeaders = sourceHeaders;
        }
        
        const sysIdMatched = getPoolVal(matchedRow, ["System_ID", "System ID"], 72);
        if (!sysIdMatched) {
          throw new Error("Dữ liệu căn nhà trong Pool thiếu System ID.");
        }
        
        const sourceSysIdIdx = sourceHeaders.indexOf("System_ID") >= 0 
          ? sourceHeaders.indexOf("System_ID") 
          : (sourceHeaders.indexOf("System ID") >= 0 ? sourceHeaders.indexOf("System ID") : 37);

        let existRowIdx = -1;
        const startIdx = isSourceHeader ? 1 : 0;
        for (let i = startIdx; i < sourceRows.length; i++) {
          if (String(sourceRows[i][sourceSysIdIdx] || '').trim() === String(sysIdMatched).trim()) {
            existRowIdx = i;
            break;
          }
        }
        const targetRowNumber = existRowIdx !== -1 
          ? (isSourceHeader ? existRowIdx + 1 : existRowIdx + 2) 
          : (isSourceHeader ? sourceRows.length + 1 : sourceRows.length + 2);
        
        // Map 15 ảnh nội thất sạch và ảnh hẻm từ biên tập viên hình ảnh trực quan
        const customCoverUrl = document.getElementById('editCoverImgUrl').value.trim();
        const publicCoverUrl = document.getElementById('editPublicCoverUrl').value.trim();
        const publicIntStr = document.getElementById('editPublicInteriorIndices').value.trim();
        const publicAlleyStr = document.getElementById('editPublicAlleyIndices').value.trim();
        const sodo1Url = document.getElementById('editSodo1Url').value.trim();
        const sodo2Url = document.getElementById('editSodo2Url').value.trim();
        const sodo3Url = document.getElementById('editSodo3Url').value.trim();
        const sodo4Url = document.getElementById('editSodo4Url').value.trim();
        const sodo5Url = document.getElementById('editSodo5Url').value.trim();

        if (publicIntStr === "") {
          alert("⚠️ Vui lòng tích chọn ít nhất 1 ảnh nội thất công khai làm Hình Public!");
          if (btnElement) {
            btnElement.disabled = false;
            btnElement.innerHTML = oldText;
          }
          return;
        }

        const p = window.activeCurationListing || {};
        const finalImages = (window.LegoState?.config?.active_pool_system === 'Pool2')
          ? window.getPublicImagesFromForm(p)
          : window.getPublicImagesFromForm(p, matchedRow);
        while (finalImages.length < 15) finalImages.push("");
        
        // Xử lý Cú pháp
        const noiDungChinh = getPoolVal(matchedRow, ["Noi_dung_chinh", "Nội dung chính"], 9) || "";
        let cuPhap = noiDungChinh;
        const matchCuPhap = noiDungChinh.match(/^(.*?Quận\s+[a-z0-9àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ\s]+?)\s+[\d\.]+(?:-[\d\.]+)?\s*tỷ/i);
        if (matchCuPhap) {
          cuPhap = matchCuPhap[1].trim();
        }
        
        // Xử lý Quận
        const formatQuan = (q) => {
          if (!q) return "";
          const qLower = q.toLowerCase();
          if (qLower.includes("quận 3")) return "3";
          if (qLower.includes("quận 10")) return "10";
          if (qLower.includes("phú nhuận")) return "PN";
          if (qLower.includes("tân bình")) return "TB";
          return q;
        };
        
        // Xử lý Giá
        const formatGia = (g) => {
          if (!g) return "";
          const val = parseFloat(g.toString().replace(/,/g, ''));
          if (isNaN(val)) return g;
          if (val > 100) return val / 1000;
          return val;
        };
        
        const poolSoNhaIdx = getPoolColIdx(["Ngõ/Số nhà", "Ngo_So_nha", "So_Nha"], 6);
        const rawSoNha = matchedRow[poolSoNhaIdx] || '';
        const loaiHinh = rawSoNha.toString().includes(".") ? "Hẻm" : "Mặt tiền";
        
        const normSodos = [sodo1Url, sodo2Url, sodo3Url, sodo4Url, sodo5Url].map(url => normalizeImgUrl(url));
        const poolCoverIdx = getPoolColIdx(["cover_image", "Hinh_mat_tien", "Hình Mặt Tiền"], 29);
        let finalCoverUrl = customCoverUrl || matchedRow[poolCoverIdx] || '';
        if (finalCoverUrl && normSodos.includes(normalizeImgUrl(finalCoverUrl))) {
          finalCoverUrl = '';
        }

        // Xây dựng publicRowData động cho Sheet Source / Custom
        const headers = sourceHeaders;
        const publicRowData = [];
        const rowLength = headers.length > 0 ? headers.length : 46;
        for (let i = 0; i < rowLength; i++) {
          publicRowData.push("");
        }

        const getColLetter = (n) => {
          let col = "";
          while (n > 0) {
            let rem = (n - 1) % 26;
            col = String.fromCharCode(65 + rem) + col;
            n = Math.floor((n - rem) / 26);
          }
          return col || "AT";
        };

        const coverHeaders = ["Hình Mặt Tiền", "Hinh_mat_tien"];
        let coverColIdx = -1;
        for (const name of coverHeaders) {
          const idx = headers.indexOf(name);
          if (idx >= 0) {
            coverColIdx = idx;
            break;
          }
        }
        if (coverColIdx === -1) coverColIdx = 38;
        const coverColLetter = getColLetter(coverColIdx + 1);
        const imageFormula = `=IMAGE(${coverColLetter}${targetRowNumber})`;

        const setVal = (names, defaultIdx, val) => {
          let mapped = false;
          for (const name of names) {
            const idx = headers.indexOf(name);
            if (idx >= 0) {
              publicRowData[idx] = val;
              mapped = true;
              break;
            }
          }
          if (!mapped && defaultIdx >= 0) {
            publicRowData[defaultIdx] = val;
          }
        };

        setVal(["Hinh_mat_tien"], 0, imageFormula);
        setVal(["Cu_phap", "Cu phap"], 1, cuPhap);
        setVal(["Note_Noi_Bo", "Note", "Ghi chú"], 2, note);
        setVal(["Ma_Khang_Ngo", "id", "Ma_Khang_Ngo (ID)"], 3, maKhangNgo);
        setVal(["Tieu_De_Public", "tieu_de"], 4, tieuDeBds || getPoolVal(matchedRow, ["Tieu_De_Public", "Tiêu đề Public", "tieu_de"], 56));
        setVal(["DT_Thuc_te", "dien_tich", "DT Thực tế"], 5, getPoolVal(matchedRow, ["DT_Thuc_te", "DT Thực tế", "dien_tich"], 13));
        setVal(["So_Tang", "so_tang", "Số Tầng"], 6, getPoolVal(matchedRow, ["So_Tang", "Số Tầng", "so_tang"], 15));
        setVal(["Mat_Tien", "mat_tien", "Mặt Tiền"], 7, getPoolVal(matchedRow, ["Mat_Tien", "Mặt Tiền", "mat_tien"], 16));
        setVal(["Gia_Public", "gia", "Giá Public"], 8, formatGia(getPoolVal(matchedRow, ["Gia_chao", "Giá chào", "Gia_Public", "Giá Public"], 11)));
        setVal(["Quan", "quan", "Quận"], 9, formatQuan(getPoolVal(matchedRow, ["Quan", "quan", "Quận"], 3)));
        setVal(["Phuong", "phuong", "Phường"], 10, getPoolVal(matchedRow, ["Phuong", "phuong", "Phường"], 4));
        setVal(["loai_hinh", "Loại Hợp đồng"], 11, loaiHinh);
        setVal(["Huong", "huong_nha"], 12, huong);
        setVal(["Criteria_Duong_truoc_nha", "duong_truoc_nha", "Phân loại Hẻm"], 13, duong);
        setVal(["Custom_Rong_Hem", "do_rong_hem", "Đường trước nhà (m)"], 14, rongHem || '-');
        setVal(["Trang_Thai_Giao_Dich", "Trang_Thai_KN", "tinh_trang_nha", "Trạng thái"], 15, tinhTrang);
        setVal(["danh_gia", "Đánh giá (Admin)"], 16, danhGia);
        setVal(["Ngu_Tret", "ngu_tang_tret", "Ngủ trệt (Admin)"], 17, nguTret);
        setVal(["CHDV", "chdv", "CHDV (Admin)"], 18, chdv);
        setVal(["Mo_ta_Public", "mo_ta", "Mô tả Public"], 19, moTaBds);
        setVal(["Last updated"], 30, new Date().toISOString());
        setVal(["phuong_cu", "Phường cũ"], 31, (p && p.phuong_cu) || getPoolVal(matchedRow, ["phuong_cu", "Phường cũ"], 66) || "");
        setVal(["bedrooms", "so_pn", "Số phòng ngủ"], 32, soPn || '-');
        setVal(["restrooms", "so_wc", "Số nhà vệ sinh"], 33, soWc || '-');
        setVal(["Ten_Duong", "ten_duong", "Đường"], 34, getPoolVal(matchedRow, ["streetName", "Đường", "Ten_Duong"], 5));
        setVal(["gio_dang"], 35, "");
        setVal(["trang_thai"], 36, "");
        setVal(["System_ID", "System ID"], 37, sysIdMatched);
        setVal(["Hình Mặt Tiền", "Hinh_mat_tien"], 38, finalCoverUrl);
        setVal(["Tiêu đề BDS"], 39, "");
        setVal(["Đăng BDS"], 40, false);

        if (headers.indexOf("images_metadata_json") >= 0) {
          const metaImages = finalImages.filter(Boolean).map(url => {
            return { url: url, role: "interior" };
          });
          setVal(["images_metadata_json"], -1, JSON.stringify(metaImages));
        } else {
          // Pool1 legacy flat columns index
          for (let i = 0; i < 10; i++) {
            publicRowData[20 + i] = finalImages[i] || "";
          }
          for (let i = 10; i < 15; i++) {
            publicRowData[41 + (i - 10)] = finalImages[i] || "";
          }
        }
        
        // Step 4: Ghi đè/Thêm mới vào Sheet Source / Custom
        const headersLength = headers.length || 46;
        const colLetter = getColLetter(headersLength);
        const writeUrl = `https://sheets.googleapis.com/v4/spreadsheets/${SOURCE_SHEET_ID}/values/${sourceTab}!A${targetRowNumber}:${colLetter}${targetRowNumber}?valueInputOption=USER_ENTERED`;
        const writeRes = await fetch(writeUrl, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ values: [publicRowData] })
        });
        
        if (!writeRes.ok) {
          let detail = "";
          try {
            const errJson = await writeRes.json();
            detail = ": " + (errJson.error?.message || JSON.stringify(errJson));
          } catch (e) {}
          throw new Error(`Không thể ghi dữ liệu sang Sheet Source (Mã: ${writeRes.status}${detail}).`);
        }
        
        // Cập nhật lại các trường ảnh đã biên tập và trường Last Sync của dòng đó bên Sheet Pool
        if (window.LegoState?.config?.active_pool_system !== 'Pool2') {
          try {
            const poolRowNumber = poolRows.indexOf(matchedRow) + 1;
            const syncDateStr = new Date().toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" });
            
            // 0. Cập nhật Sổ 1 & 2 (AB:AC)
            try {
              await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!AB${poolRowNumber}:AC${poolRowNumber}?valueInputOption=USER_ENTERED`, {
                method: 'PUT',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ values: [[sodo1Url, sodo2Url]] })
              });
            } catch (e) {
              console.warn("Không thể đồng bộ thay đổi Sổ sang Pool thô:", e);
            }

            // 0b. Cập nhật Hình Mặt Tiền (Cột AD) và Ảnh Bìa / Ảnh 1 (Cột AO) sang Pool thô (US-046.6)
            try {
              await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!AD${poolRowNumber}:AD${poolRowNumber}?valueInputOption=USER_ENTERED`, {
                method: 'PUT',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ values: [[customCoverUrl]] })
              });
            } catch (e) {
              console.warn("Không thể đồng bộ Hình Mặt Tiền sang Pool:", e);
            }

            // 0c. Cập nhật Sổ 3-5 (CC:CE)
            try {
              await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!CC${poolRowNumber}:CE${poolRowNumber}?valueInputOption=USER_ENTERED`, {
                method: 'PUT',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ values: [[sodo3Url, sodo4Url, sodo5Url]] })
              });
            } catch (e) {
              console.warn("Không thể đồng bộ Sổ 3-5 sang Pool:", e);
            }

            // 1b. Cập nhật Ảnh Nội Thất 1-15 (AO:BC) và 16-25 (CC:CL) sang Pool thô
            try {
              const int1_15 = [];
              for (let c = 40; c <= 54; c++) {
                int1_15.push(matchedRow[c] || "");
              }
              await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!AO${poolRowNumber}:BC${poolRowNumber}?valueInputOption=USER_ENTERED`, {
                method: 'PUT',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ values: [int1_15] })
              });
            } catch (e) {
              console.warn("Không thể đồng bộ Ảnh Nội Thất 1-15 sang Pool:", e);
            }

            try {
              const int16_25 = [];
              for (let c = 83; c <= 92; c++) {
                int16_25.push(matchedRow[c] || "");
              }
              await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!CF${poolRowNumber}:CO${poolRowNumber}?valueInputOption=USER_ENTERED`, {
                method: 'PUT',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ values: [int16_25] })
              });
            } catch (e) {
              console.warn("Không thể đồng bộ Ảnh Nội Thất 16-25 sang Pool:", e);
            }

            // 1. Cập nhật anhDuocChon (BK) và anhHemDuocChon (BL)
            await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!BK${poolRowNumber}:BL${poolRowNumber}?valueInputOption=USER_ENTERED`, {
              method: 'PUT',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ values: [[publicIntStr, publicAlleyStr]] })
            });
            
            // 2. Cập nhật Last Sync (CA)
            await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!CA${poolRowNumber}:CA${poolRowNumber}?valueInputOption=USER_ENTERED`, {
              method: 'PUT',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ values: [[syncDateStr]] })
            });
          } catch (e) {
            console.warn("Không thể ghi nhận thay đổi hình ảnh hoặc Last Sync vào Pool:", e);
          }
        }
        
        showToast(`🎉 Đã đồng bộ lên sóng thành công căn nhà #${maKhangNgo}! Đang tải lại trang...`);
        
        // Reset các ô tìm kiếm Pool
        const pullInput = document.getElementById('poolSearchToolInput');
        if (pullInput) pullInput.value = '';
        const pullResults = document.getElementById('poolSearchToolResults');
        if (pullResults) pullResults.innerHTML = '';

        localStorage.setItem('auto_preview_listing_id', maKhangNgo);
        localStorage.setItem('auto_share_zalo_listing_id', maKhangNgo);
        setTimeout(() => {
          window.location.reload();
        }, 1200);
        
      } catch (err) {
        showToast(`❌ Lỗi đồng bộ: ${err.message}`, "error");
        console.error(err);
      } finally {
        if (btnElement) {
          btnElement.disabled = false;
          btnElement.innerHTML = oldText;
        }
      }
    };

  // Register remaining aliases on window for backward compatibility
  window.compressImageClientSide = compressImageClientSide;
  window.uploadFileToR2 = uploadFileToR2;
  window.executePullFromPool = executePullFromPool;
  window.renderImageEditorWidget = renderImageEditorWidget;
  window.isListingSodoUrl = isListingSodoUrl;
  window.slideImageEditorCarousel = slideImageEditorCarousel;
  window.gotoImageEditorSlide = gotoImageEditorSlide;
  window.handleCarouselTouchStart = handleCarouselTouchStart;
  window.handleCarouselTouchMove = handleCarouselTouchMove;
  window.handleCarouselTouchEnd = handleCarouselTouchEnd;
  window.handleCarouselSwipe = handleCarouselSwipe;
  window.removeImageFromPublicLists = removeImageFromPublicLists;
  window.removeImageFromSodo = removeImageFromSodo;
  window.activeImageToggleFacade = activeImageToggleFacade;
  window.activeImageToggleCover = activeImageToggleCover;
  window.activeImageToggleSodo = activeImageToggleSodo;
  window.activeImageTogglePublic = activeImageTogglePublic;
  window.activeImageMoveOrder = activeImageMoveOrder;
  window.reRenderCurationEditorInPlace = reRenderCurationEditorInPlace;
  window.refreshImageEditorUI = refreshImageEditorUI;
  window.handleLocalImageUpload = handleLocalImageUpload;
  window.uncheckAllCurationImages = uncheckAllCurationImages;
  window.openPoolS = openPoolS;
  window.onPoolSearchToolKeyup = onPoolSearchToolKeyup;
  window.pullListingFromPoolRow = pullListingFromPoolRow;
  window.toggleAdminAccordion = toggleAdminAccordion;
  window.getPublicImagesFromForm = getPublicImagesFromForm;
  window.openZoomOverlay = openZoomOverlay;
  window.checkMoTaCollapse = checkMoTaCollapse;
  window.toggleMotaGocCollapse = toggleMotaGocCollapse;
  window.saveSourceChanges = saveSourceChanges;
  window.saveNewListingFromPool = saveNewListingFromPool;

  console.log("LegoDetailAdmin module initialized.");
})();
