    function render() {
      if (hasErrorState) return;
      const list = document.getElementById('list');
      list.innerHTML = '';
      
      // Sửa lỗi: Render dựa trên danh sách đã lọc (getFiltered()) thay vì danh sách thô (sourceArr)
      // Điều này khắc phục triệt độ việc tìm kiếm BĐS vượt quá 200 căn trong Kho Pool không hiển thị
      const filteredArr = getFiltered();
      const arr = filteredArr.slice().sort((a, b) => {
        if (currentSortType === 'newest') {
          let ta, tb;
          if (isAdmin && activeMode === 'pool' && showOnAirOnly) {
            const ma = DATA.find(x => 
              (x.system_id && a.system_id && String(x.system_id).trim() === String(a.system_id).trim()) ||
              (x.id && a.id && String(x.id).trim() === String(a.id).trim())
            );
            const mb = DATA.find(x => 
              (x.system_id && b.system_id && String(x.system_id).trim() === String(b.system_id).trim()) ||
              (x.id && b.id && String(x.id).trim() === String(b.id).trim())
            );
            ta = ma ? parseInt(ma.temp_id, 10) || 0 : 0;
            tb = mb ? parseInt(mb.temp_id, 10) || 0 : 0;
          } else {
            ta = parseInt(a.temp_id, 10) || 0;
            tb = parseInt(b.temp_id, 10) || 0;
          }
          return currentSortDir === 'asc' ? ta - tb : tb - ta;
        } else {
          const ga = parseFloat(a.gia) || 0, gb = parseFloat(b.gia) || 0;
          return currentSortDir === 'asc' ? ga - gb : gb - ga;
        }
      });

      if (!arr.length) {
        if (isAdmin && activeMode === 'pool') {
          list.insertAdjacentHTML('beforeend', '<div style="text-align:center;padding:60px 20px;color:var(--sub);font-weight:500;">Không có bất động sản nào trong Kho Pool khớp với bộ lọc hiện tại.</div>');
        } else {
          list.insertAdjacentHTML('beforeend', '<div style="text-align:center;padding:60px 20px;color:var(--sub);font-weight:500;">Vui lòng liên hệ Khang Ngô Nhà Phố để được cung cấp thông tin.</div>');
        }
        return;
      }

      const isPool = (isAdmin && activeMode === 'pool');
      const maxRender = isPool ? 200 : arr.length;
      const itemsToRender = arr.slice(0, maxRender);

      const frag = document.createDocumentFragment();
      itemsToRender.forEach((p) => {
        let cardEl;
        if (isAdmin) {
          const curatedListing = DATA.find(x => 
            (x.system_id && p.system_id && String(x.system_id).trim() === String(p.system_id).trim()) ||
            (x.id && p.id && String(x.id).trim() === String(p.id).trim())
          );
          cardEl = LegoRenderAdmin.createCard(p, curatedListing, { favs, SELECTED_IDS, activeCollectionName: window.activeCollectionName });
        } else {
          cardEl = LegoRenderClient.createCard(p, { favs, activeCollectionName: window.activeCollectionName });
        }
        frag.appendChild(cardEl);
      });
      list.appendChild(frag);

      if (isPool && arr.length > maxRender) {
        list.insertAdjacentHTML('beforeend', `
          <div style="grid-column: 1 / -1; text-align: center; padding: 24px; color: rgba(255,255,255,0.45); font-size: 13px; font-weight: 500; border-top: 1px solid rgba(255,255,255,0.08); margin-top: 15px; line-height: 1.5;">
            📦 Đang hiển thị <b>200</b> trên tổng số <b>${arr.length}</b> căn trong Kho Pool.<br>
            <span style="font-size:12px; color: var(--gold); font-weight: 600;">Vui lòng chọn Quận/Phường hoặc điền Khoảng Giá/Diện Tích để thu hẹp tìm kiếm!</span>
          </div>
        `);
      }

      applyFilter();
    }
    window.render = render;



    window.executePoolFallbackSearch = function(query) {
      const resultsContainer = document.getElementById('poolFallbackResults');
      if (!resultsContainer) return;
      resultsContainer.innerHTML = '';
      
      const matched = searchPoolRows(query);
      if (matched.length === 0) {
        resultsContainer.innerHTML = '<div style="font-size: 13px; color: rgba(255,255,255,0.5); text-align: center; padding: 10px;">❌ Vẫn không tìm thấy căn nào trong Pool thô khớp từ khóa này.</div>';
        return;
      }
      
      resultsContainer.innerHTML = `<div style="font-size: 11.5px; font-weight: 800; color: var(--gold); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">📦 TÌM THẤY ${matched.length} CĂN TRONG POOL THÔ:</div>`;
      
      matched.slice(0, 15).forEach(row => {
        const isAlready = isPoolRowOnAir(row);
        const systemId = row[72] || row[71] || '';
        const id = row[55] || systemId || '';
        const soNha = row[6] || '';
        const duong = row[5] || '';
        const gia = row[11] || row[58] || '';
        const dt = row[14] || '';
        const dauChu = row[75] || '';
        const sdt = row[74] || '';
        const ndChinh = row[9] || '';

        const div = document.createElement('div');
        div.style.cssText = 'padding: 12px; background: rgba(255,255,255,0.04); border-radius: 12px; border: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; gap: 12px; cursor: pointer; transition: background 0.2s;';
        
        div.onmouseenter = () => div.style.background = 'rgba(255,255,255,0.08)';
        div.onmouseleave = () => div.style.background = 'rgba(255,255,255,0.04)';
        
        if (isAlready) {
          // If already on air, click card to open standard detail view (openS)
          div.onclick = () => openS(id);
        } else {
          // If not yet on air, click card to open raw curation detail view (openPoolS)
          div.onclick = () => openPoolS(systemId);
        }
        
        div.innerHTML = `
          <div style="flex: 1; min-width: 0;">
            <div style="font-size: 13px; font-weight: 700; color: #fff; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              🏠 ${soNha} ${duong}
            </div>
            <div style="font-size: 11px; color: rgba(255,255,255,0.65); margin-top: 4px; line-height: 1.4;">
              💰 Giá chào: <b style="color:var(--gold);">${gia} tỷ</b> - 📐 Diện tích: <b>${dt} m²</b><br>
              👤 Đầu chủ: <b>${dauChu}</b> (${sdt})<br>
              📝 Nội dung: <span style="font-style: italic; color: rgba(255,255,255,0.55);">${ndChinh.substring(0, 75)}...</span>
            </div>
          </div>
          <div style="flex-shrink: 0;">
            ${isAlready ? `
              <span style="font-size: 10.5px; font-weight: 700; color: #2ecc71; background: rgba(46, 204, 113, 0.15); padding: 5px 10px; border-radius: 6px; white-space: nowrap;">✅ Đã lên sóng</span>
            ` : `
              <button onclick="pullListingFromPoolRow(event, '${systemId}', '${id}', '${soNha.replace(/'/g, "\\'")}', '${duong.replace(/'/g, "\\'")}')" 
                style="background: #27ae60; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 11.5px; font-weight: 700; cursor: pointer; white-space: nowrap; font-family: inherit;">
                ⚡ Lên sóng
              </button>
            `}
          </div>
        `;
        resultsContainer.appendChild(div);
      });
    };





    // Note: Lightbox & Gallery logic moved to static/js/lego_detail_client.js


    function openS(id, tempP = null, autoExpandPreview = false) {
      const p = tempP || DATA.find(x => String(x.id) === String(id));
      if (!p) return;
      window.activeCurationListing = p;

      const targetMatTien = p.img_mat_tien || (p.pool_row_data ? p.pool_row_data[29] : '') || '';
      const normMatTien = normalizeImgUrl(targetMatTien);
      const isFacadeUrl = (url) => {
        if (!url) return false;
        const norm = normalizeImgUrl(url);
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

      // Tracking: Xem chi tiết căn nhà
      if (p.id) {
        trackAction("Xem chi tiết", `#${p.id} - ${p.t}`);
      }

      const mID = document.getElementById('mID');
      const cleanTitle = cutTitleToDistrict(p.t);
      const cleanAddressTitle = `${p.raw_so_nha || ''} ${p.raw_ten_duong || ''}`.trim() || cleanTitle;
      document.getElementById('mT').textContent = cleanAddressTitle;

      const floatActions = document.getElementById('adminDetailFloatActions');
