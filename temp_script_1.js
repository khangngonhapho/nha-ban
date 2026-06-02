
    // ============================================================
    // [Latest Update / User Story]
    // - US-029: Sắp xếp theo Sản phẩm mới thêm mặc định trên danh sách, thêm nút xếp thời gian ⏱️ kế bên xếp giá 💰 trên thanh điều khiển của Admin (Cập nhật ngày 2026-05-25)
    // - US-028: Đồng bộ cơ chế nén Bitmask gửi khách nhiều căn (?b=...) siêu ngắn cho cả hai luồng Admin, giữ URL cực ngắn tránh bị Zalo/Messenger cắt ngắn (Cập nhật ngày 2026-05-25)
    // ============================================================
    //  ⚙️  KIỂM TRA QUYỀN TRUY CẬP & GIAI ĐOẠN 1 TRACKING
    // ============================================================
    const ADMIN_PASSWORD = 'trang';
    const urlParams = new URLSearchParams(window.location.search);
    const isAdmin = urlParams.get('pwd') === ADMIN_PASSWORD;
    const shareToken = urlParams.get('s');

    // Giai đoạn 1: Giải mã tên khách hàng
    let displayCustomerName = "";
    let trackingCustomerName = "";
    const customerToken = urlParams.get('c');
    if (customerToken) {
      try {
        let safeToken = customerToken.replace(/ /g, '+');
        // Khôi phục padding = cho Base64URL nếu bị thiếu
        while (safeToken.length % 4) {
          safeToken += '=';
        }
        const decoded = decodeURIComponent(escape(window.atob(safeToken)));
        const parts = decoded.split("|").map(p => p.trim());
        displayCustomerName = parts[0];
        trackingCustomerName = `${parts[0]}${parts[1] ? ' - ' + parts[1] : ''}`;

        // GIẢI MÃ & CẬP NHẬT TIÊU ĐỀ TRANG TÙY CHỈNH (US-033)
        const customPageTitle = parts[2] || "";
        if (customPageTitle) {
          document.title = customPageTitle;
        } else {
          document.title = "Giỏ hàng độc quyền - Khang Ngô Nhà Phố";
        }
      } catch (e) {
        displayCustomerName = "Khách Hàng";
        trackingCustomerName = "Khách Hàng";
        document.title = "Giỏ hàng độc quyền - Khang Ngô Nhà Phố";
      }
    } else {
      document.title = "Khang Ngô Nhà Phố";
    }

    // Giai đoạn 1: Hàm Tracking gửi data về Google Apps Script
    // Đã cấu hình Tracking API thực tế
    const TRACKING_URL = 'https://script.google.com/macros/s/AKfycbxsFXAQiX11LaSAslvefiv7ncWcHVgeyyd8Gi2pgRAneHhyZpE0AZKjP4rRrHD15oNN1g/exec';

    function trackAction(action, details = "") {
      if (isAdmin || !trackingCustomerName) return; // Không track Admin
      try {
        fetch(TRACKING_URL, {
          method: 'POST',
          mode: 'no-cors',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            customer: trackingCustomerName,
            action: action,
            details: details
          })
        }).catch(e => { });
      } catch (error) { }
    }

    if (displayCustomerName) {
      const banner = document.getElementById('welcomeBanner');
      if (banner) {
        banner.innerHTML = `👋 Xin chào <b>${displayCustomerName}</b>, đây là danh sách nhà Khang Ngô chọn riêng cho anh/chị!`;
        banner.style.display = 'block';
      }
    }

    if (isAdmin) document.body.classList.add('is-admin');

    // Logic chia sẻ: giải mã danh sách ID từ URL
    let sharedIds = null;
    const shareBitmask = urlParams.get('b'); // Format cũ: bitmask
    if (shareToken) {
      try {
        if (shareToken.includes(',') || !shareToken.includes('[')) {
          // Token có thể chứa list mã tạm (VD: 1,5,12) hoặc list Mã căn cũ (VD: q3-10,pn-05)
          sharedIds = shareToken.split(',').map(s => s.trim()).filter(Boolean);
        } else {
          const decoded = atob(shareToken);
          const parsed = JSON.parse(decoded);
          if (Array.isArray(parsed)) sharedIds = parsed;
        }
      } catch (e) {
        sharedIds = shareToken.split(',').map(s => s.trim()).filter(Boolean);
      }
    }
    // Hàm giải mã bitmask (gọi sau khi load data)
    const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
    function decodeBitmask(encoded, allIds) {
      let bits = '';
      for (const ch of encoded) {
        const val = B64.indexOf(ch);
        if (val < 0) continue;
        bits += val.toString(2).padStart(6, '0');
      }
      return allIds.filter((id, i) => bits[i] === '1');
    }

    //  ⚙️  CẤU HÌNH 
    const SHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0';
    const SDT = '0979841573';
    // ============================================================

    // Cập nhật số điện thoại tự động
    document.querySelectorAll('[href*="0979841573"]').forEach(el => {
      el.href = el.href.replace(/0979841573/g, SDT);
    });

    let DATA = [];
    const selDistricts = new Set();
    const selWards = new Set();
    const selDuongs = new Set();
    const selHuong = new Set();
    const selGia = new Set();
    const selDanhGia = new Set();
    let filterOpen = false;
    let currentSortType = 'newest'; // 'newest' or 'price'
    let currentSortDir = 'desc'; // 'desc' = high/newest first, 'asc' = low/oldest first
    let showFavOnly = false;
    let favs = new Set(JSON.parse(localStorage.getItem('favs') || '[]'));
    let collections = JSON.parse(localStorage.getItem('adminCollections') || '{}');
    let activeCollectionName = null; // null | 'favorites' | '[Tên BST tự tạo]'

    // ── Multi-select helper ──
    function tSel(set, val) {
      if (val === 'all') { set.clear(); return; }
      if (set.has(val)) set.delete(val); else set.add(val);
    }
    function syncTabUI(containerId, set) {
      document.querySelectorAll('#' + containerId + ' .tab').forEach(btn => {
        const v = btn.getAttribute('data-val');
        btn.classList.toggle('on', v === 'all' ? set.size === 0 : set.has(v));
      });
    }
    function applyGia(arr) {
      if (!selGia.size) return arr;
      return arr.filter(p => {
        const g = parseFloat(p.gia) || 0;
        return [...selGia].some(r => {
          if (r === 'lt7') return g < 7;
          if (r === '7-10') return g >= 7 && g <= 10;
          if (r === '10-15') return g > 10 && g <= 15;
          if (r === '15-20') return g > 15 && g <= 20;
          if (r === 'gt20') return g > 20;
          return false;
        });
      });
    }
    function toggleSearchClearBtn() {
      const sInput = document.getElementById('searchInput');
      const clearBtn = document.getElementById('searchClear');
      if (sInput && clearBtn) {
        clearBtn.style.display = sInput.value.trim() ? 'flex' : 'none';
      }
    }
    function clearSearchInput() {
      const sInput = document.getElementById('searchInput');
      if (sInput) {
        sInput.value = '';
        onSearchInput();
      }
    }
    function onSearchInput() {
      toggleSearchClearBtn();
      updateStats();
      applyFilter();
      saveState();
    }

    function toggleSearchBar() {
      const bar = document.getElementById('searchBar');
      const btn = document.getElementById('searchToggleBtn');
      const input = document.getElementById('searchInput');
      if (!bar || !btn || !input) return;
      const isOpen = bar.classList.toggle('open');
      btn.classList.toggle('active', isOpen);
      if (isOpen) {
        setTimeout(() => input.focus(), 150);
      } else {
        input.value = '';
        onSearchInput();
      }
    }

    function getFiltered() {
      let a = DATA;
      const sv = (document.getElementById('searchInput')?.value || '').trim().toLowerCase();
      if (sv) {
        a = a.filter(p => {
          const idMatch = String(p.id).toLowerCase().includes(sv);
          const tMatch = p.t.toLowerCase().includes(sv);
          const dMatch = p.duong_truoc_nha.toLowerCase().includes(sv);
          const pMatch = p.phuong.toLowerCase().includes(sv);
          const qMatch = p.q.toLowerCase().includes(sv) ||
            p.ql.toLowerCase().includes(sv) ||
            (sv === 'phú nhuận' && p.q === 'pn') ||
            (sv === 'tân bình' && p.q === 'tb') ||
            (sv === 'bình thạnh' && p.q === 'bt') ||
            (sv === 'gò vấp' && p.q === 'gv') ||
            (sv === 'quận 3' && p.q === 'q3') ||
            (sv === 'quận 10' && p.q === 'q10');
          return idMatch || tMatch || dMatch || pMatch || qMatch;
        });
      }

      // LỌC THEO BỘ LỌC ADMIN NÂNG CAO
      const asv = (document.getElementById('adminSearchInput')?.value || '').trim().toLowerCase();
      if (isAdmin && asv) {
        a = a.filter(p => {
          const dauChuMatch = (p.raw_ten_dau_chu || '').toLowerCase().includes(asv);
          const ndMatch = (p.raw_noi_dung_chinh || '').toLowerCase().includes(asv);
          const mtMatch = (p.raw_mo_ta_chi_tiet || '').toLowerCase().includes(asv);
          const noteMatch = (p.note || '').toLowerCase().includes(asv);
          const cpMatch = (p.cu_phap || '').toLowerCase().includes(asv);
          const soNhaMatch = (p.raw_so_nha || '').toLowerCase().includes(asv);
          const duongMatch = (p.raw_ten_duong || '').toLowerCase().includes(asv);
          return dauChuMatch || ndMatch || mtMatch || noteMatch || cpMatch || soNhaMatch || duongMatch;
        });
      }

      if (showFavOnly) a = a.filter(p => favs.has(String(p.id)));
      if (selDistricts.size) a = a.filter(p => selDistricts.has(p.q));
      if (selWards.size) a = a.filter(p => selWards.has(p.phuong));
      if (selDuongs.size) a = a.filter(p => selDuongs.has(p.duong_truoc_nha));
      if (selHuong.size) a = a.filter(p => selHuong.has(p.huong));
      a = applyGia(a);
      if (selDanhGia.size) a = a.filter(p => selDanhGia.has(p.danh_gia));

      // LỌC THEO BỘ SƯU TẬP HOẶC DANH SÁCH YÊU THÍCH CỦA ADMIN
      if (activeCollectionName) {
        if (activeCollectionName === 'favorites') {
          a = a.filter(p => favs.has(String(p.id)));
        } else if (collections[activeCollectionName]) {
          const colIds = new Set(collections[activeCollectionName]);
          a = a.filter(p => colIds.has(String(p.id)));
        }
      }
      return a;
    }
    const SELECTED_IDS = new Set();

    // Lấy giá trị ô từ Google Sheets JSON (xử lý null do lỗi mixed type của gviz)
    function cv(cell) { return cell ? (cell.v ?? cell.f ?? '') : ''; }

    // Tự động convert link Google Drive → ảnh có thể nhúng với kích thước tùy chỉnh
    function fixImgUrl(url, sz = 'w800') {
      if (!url) return '';
      if (url.includes('thumbnail') || url.includes('uc?export')) {
        // Nếu là link thumbnail cũ, cập nhật lại kích thước
        return url.replace(/sz=w\d+/, `sz=${sz}`);
      }
      const m1 = url.match(/drive\.google\.com\/file\/d\/([^/?\s]+)/);
      if (m1) return `https://drive.google.com/thumbnail?id=${m1[1]}&sz=${sz}`;
      const m2 = url.match(/[?&]id=([^&\s]+)/);
      if (m2) return `https://drive.google.com/thumbnail?id=${m2[1]}&sz=${sz}`;
      return url;
    }

    // Dùng JSONP thay fetch để tránh lỗi CORS khi mở file:// cục bộ
    async function loadData() {
      // Xóa script cũ nếu có
      const old = document.getElementById('_gs');
      if (old) old.remove();
      const oldAdmin = document.getElementById('_gs_admin');
      if (oldAdmin) oldAdmin.remove();

      const token = localStorage.getItem('g_access_token');
      const expiry = localStorage.getItem('g_token_expiry');
      const now = Date.now();
      const isTokenValid = token && expiry && parseInt(expiry, 10) > now;

      if (isAdmin && isTokenValid) {
        console.log("Loading parallel Admin data...");
        const listContainer = document.getElementById('list');
        if (listContainer) {
          listContainer.innerHTML = '<div style="text-align:center; padding: 40px; font-weight: 700; color: var(--red);">🏠 ĐANG NẠP DỮ LIỆU BẢO MẬT ADMIN SONG SONG...</div>';
        }

        const POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw';
        const SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE';

        try {
          const [sourceRes, poolRes] = await Promise.all([
            fetch(`https://sheets.googleapis.com/v4/spreadsheets/${SOURCE_SHEET_ID}/values/Source!A2:AO`, {
              headers: { 'Authorization': `Bearer ${token}` }
            }),
            fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!A2:BZ`, {
              headers: { 'Authorization': `Bearer ${token}` }
            })
          ]);

          if (!sourceRes.ok || !poolRes.ok) {
            throw new Error(`Lỗi tải API Google Sheets (Source: ${sourceRes.status}, Pool: ${poolRes.status})`);
          }

          const sourceDataJson = await sourceRes.json();
          const poolDataJson = await poolRes.json();

          const sourceRows = sourceDataJson.values || [];
          const poolRows = poolDataJson.values || [];

          const fullList = sourceRows
            .map((sr, index) => {
              if (!sr[3] && !sr[4]) return null;
              
              const targetRowNumber = index + 2;
              const dt = parseFloat(sr[5]) || 0;
              const gia = parseFloat(sr[8]) || 0;
              const giabq = (dt > 0 && gia > 0) ? Math.round((gia * 1000) / dt) : 0;
              
              let rawQ = sr[9] || '';
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
              else if (cleanQLower.includes('cần giờ') || cleanQLower === 'cg') cleanQ = 'cg';
              else if (cleanQLower === '1' || cleanQLower === 'q1') cleanQ = '1';
              else if (cleanQLower === '2' || cleanQLower === 'q2') cleanQ = '2';
              else if (cleanQLower === '3' || cleanQLower === 'q3') cleanQ = '3';
              else if (cleanQLower === '4' || cleanQLower === 'q4') cleanQ = '4';
              else if (cleanQLower === '5' || cleanQLower === 'q5') cleanQ = '5';
              else if (cleanQLower === '6' || cleanQLower === 'q6') cleanQ = '6';
              else if (cleanQLower === '7' || cleanQLower === 'q7') cleanQ = '7';
              else if (cleanQLower === '8' || cleanQLower === 'q8') cleanQ = '8';
              else if (cleanQLower === '9' || cleanQLower === 'q9') cleanQ = '9';
              else if (cleanQLower === '10' || cleanQLower === 'q10') cleanQ = '10';
              else if (cleanQLower === '11' || cleanQLower === 'q11') cleanQ = '11';
              else if (cleanQLower === '12' || cleanQLower === 'q12') cleanQ = '12';

              const p = {
                temp_id: index + 1,
                id: sr[3] || '',
                t: sr[4] || '',
                dt: sr[5] || '',
                tang: sr[6] || '',
                mat: sr[7] || '',
                gia: sr[8] || '',
                q: (isNaN(cleanQ) || cleanQ === '') ? cleanQ.toLowerCase() : 'q' + cleanQ,
                ql: cleanQ.toUpperCase(),
                phuong: sr[10] || '-',
                loai_hinh: sr[11] || 'Hẻm',
                huong: sr[12] || '-',
                duong_truoc_nha: sr[13] || '-',
                rong_hem: sr[14] || '-',
                tinh_trang: sr[15] || '-',
                danh_gia: sr[16] || '',
                is_invisible: (sr[15] || '').toLowerCase().includes('ẩn') ||
                              (sr[15] || '').toLowerCase().includes('đã bán') ||
                              (sr[15] || '').toLowerCase().includes('invisible'),
                ngu_tang_tret: sr[17] || '-',
                chdv: sr[18] || '-',
                giabq: giabq > 0 ? `${giabq} tr/m²` : '-',
                m: sr[19] || '',
                imgs: [
                  sr[20], sr[21], sr[22], sr[23], sr[24],
                  sr[25], sr[26], sr[27], sr[28], sr[29]
                ].filter(Boolean),
                system_id: sr[37] || (index + 1).toString(),
                so_pn: sr[32] || '-',
                img_mat_tien: sr[38] || '',
                
                original_row_data: sr,
                source_row_index: targetRowNumber
              };

              const poolRow = poolRows.find(pr => {
                const prSystemId = pr[71] || '';
                const prId = pr[54] || '';
                return (p.system_id && prSystemId === p.system_id) || 
                       (p.id && prId === p.id) ||
                       (p.system_id && prId === p.system_id);
              });

              if (poolRow) {
                p.raw_ten_dau_chu = poolRow[74] || '';
                p.raw_dt_dau_chu = poolRow[73] || '';
                p.raw_link_fb = poolRow[75] || '';
                p.raw_noi_dung_chinh = poolRow[9] || '';
                p.raw_mo_ta_chi_tiet = poolRow[56] || '';
                p.raw_sodo1 = poolRow[27] || '';
                p.raw_sodo2 = poolRow[28] || '';
                p.raw_so_nha = poolRow[6] || '';
                p.raw_ten_duong = poolRow[5] || '';
                p.raw_dt_tren_so = poolRow[13] || '';
                p.raw_gia_chao = poolRow[57] || '';
                p.raw_so_tang = poolRow[15] || '';
                p.raw_mat_tien = poolRow[16] || '';
                p.raw_duong_truoc_nha = poolRow[58] || '';
                p.raw_do_rong_hem = poolRow[59] || '';
                p.raw_so_pn = poolRow[63] || '';
                p.raw_so_wc = poolRow[64] || '';
                p.pool_row_index = poolRows.indexOf(poolRow) + 2;
              } else {
                p.raw_ten_dau_chu = '';
                p.raw_dt_dau_chu = '';
                p.raw_link_fb = '';
                p.raw_noi_dung_chinh = '';
                p.raw_mo_ta_chi_tiet = '';
                p.raw_sodo1 = '';
                p.raw_sodo2 = '';
                p.raw_so_nha = '';
                p.raw_ten_duong = p.ten_duong || '';
                p.raw_dt_tren_so = p.dt || '';
                p.raw_gia_chao = p.gia || '';
                p.raw_so_tang = p.tang || '';
                p.raw_mat_tien = p.mat || '';
                p.raw_duong_truoc_nha = p.duong_truoc_nha || '';
                p.raw_do_rong_hem = p.rong_hem || '';
                p.raw_so_pn = p.so_pn || '';
                p.raw_so_wc = '';
                p.pool_row_index = null;
              }

              return p;
            })
            .filter(Boolean);

          finalizeData(fullList);
        } catch (err) {
          console.error("Error loading secure admin data, falling back to public:", err);
          loadPublicDataFallback();
        }
      } else {
        loadPublicDataFallback();
      }
    }

    function loadPublicDataFallback() {
      window.__gsCallback = function (response) {
        try {
          const rows = response.table.rows;
          const QUAN_FULL = { pn: 'Phú Nhuận', tb: 'Tân Bình', bt: 'Bình Thạnh', gv: 'Gò Vấp' };
          const fullList = rows
            .filter(r => r.c[0] && r.c[0].v)
            .map((r, index) => {
              const dt = parseFloat(cv(r.c[2])) || 0;
              const gia = parseFloat(cv(r.c[5])) || 0;
              const giabq = (dt > 0 && gia > 0) ? Math.round((gia * 1000) / dt) : 0;
              let rawQ = cv(r.c[6]);
              if (!rawQ) {
                const titleLower = String(cv(r.c[1])).toLowerCase();
                const phuongLower = String(cv(r.c[7])).toLowerCase();
                if (titleLower.includes('phú nhuận') || titleLower.includes('pn') || phuongLower.includes('phú nhuận') || phuongLower.includes('pn') || phuongLower.includes('cầu kiệu')) rawQ = 'PN';
                else if (titleLower.includes('tân bình') || titleLower.includes('tb') || phuongLower.includes('tân bình') || phuongLower.includes('tb') || phuongLower.includes('tân sơn nhất') || phuongLower.includes('tân hòa')) rawQ = 'TB';
                else if (titleLower.includes('bình thạnh') || titleLower.includes('bt') || phuongLower.includes('bình thạnh') || phuongLower.includes('bt')) rawQ = 'BT';
                else if (titleLower.includes('gò vấp') || titleLower.includes('gv') || phuongLower.includes('gò vấp') || phuongLower.includes('gv')) rawQ = 'GV';
              }
              let cleanQ = String(rawQ).replace(/^(Quận|Q)\.?\s*/i, '').trim();
              if (cleanQ.endsWith('.0')) {
                cleanQ = cleanQ.substring(0, cleanQ.length - 2);
              }

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
              else if (cleanQLower.includes('cần giờ') || cleanQLower === 'cg') cleanQ = 'cg';
              else if (cleanQLower === '1' || cleanQLower === 'q1') cleanQ = '1';
              else if (cleanQLower === '2' || cleanQLower === 'q2') cleanQ = '2';
              else if (cleanQLower === '3' || cleanQLower === 'q3') cleanQ = '3';
              else if (cleanQLower === '4' || cleanQLower === 'q4') cleanQ = '4';
              else if (cleanQLower === '5' || cleanQLower === 'q5') cleanQ = '5';
              else if (cleanQLower === '6' || cleanQLower === 'q6') cleanQ = '6';
              else if (cleanQLower === '7' || cleanQLower === 'q7') cleanQ = '7';
              else if (cleanQLower === '8' || cleanQLower === 'q8') cleanQ = '8';
              else if (cleanQLower === '9' || cleanQLower === 'q9') cleanQ = '9';
              else if (cleanQLower === '10' || cleanQLower === 'q10') cleanQ = '10';
              else if (cleanQLower === '11' || cleanQLower === 'q11') cleanQ = '11';
              else if (cleanQLower === '12' || cleanQLower === 'q12') cleanQ = '12';
              return {
                temp_id: index + 1,
                id: cv(r.c[0]),
                t: cv(r.c[1]),
                dt: cv(r.c[2]),
                tang: cv(r.c[3]),
                mat: cv(r.c[4]),
                gia: cv(r.c[5]),
                q: (isNaN(cleanQ) || cleanQ === '') ? cleanQ.toLowerCase() : 'q' + cleanQ,
                ql: cleanQ.toUpperCase(),
                phuong: cv(r.c[7]) || '-',
                loai_hinh: cv(r.c[8]) || 'Hẻm',
                huong: cv(r.c[9]) || '-',
                duong_truoc_nha: cv(r.c[10]) || '-',
                rong_hem: cv(r.c[11]) || '-',
                tinh_trang: cv(r.c[12]) || '-',
                danh_gia: cv(r.c[13]) || '',
                is_invisible: (cv(r.c[12]) || '').toLowerCase().includes('ẩn') ||
                  (cv(r.c[12]) || '').toLowerCase().includes('đã bán') ||
                  (cv(r.c[12]) || '').toLowerCase().includes('invisible'),
                ngu_tang_tret: cv(r.c[14]) || '-',
                chdv: cv(r.c[15]) || '-',
                giabq: giabq > 0 ? `${giabq} tr/m²` : '-',
                m: cv(r.c[16]),
                imgs: [
                  cv(r.c[17]), cv(r.c[18]), cv(r.c[19]), cv(r.c[20]), cv(r.c[21]),
                  cv(r.c[22]), cv(r.c[23]), cv(r.c[24]), cv(r.c[25]), cv(r.c[26])
                ].filter(Boolean),
                system_id: cv(r.c[34]) || (index + 1).toString(),
                so_pn: cv(r.c[29]) || '-',
                img_mat_tien: ''
              };
            });

          finalizeData(fullList);
        } catch (e) {
          showError('Lỗi parse dữ liệu: ' + e.message);
        }
      };

      const s = document.createElement('script');
      s.id = '_gs';
      s.src = `https://docs.google.com/spreadsheets/d/${SHEET_ID}/gviz/tq?tqx=out:json;responseHandler:__gsCallback`;
      s.onerror = () => showError('Không kết nối được Google Sheets. Kiểm tra SHEET_ID và quyền truy cập.');
      document.head.appendChild(s);
    }

    function finalizeData(fullList) {
      if (shareBitmask) {
        const allIds = fullList.filter(p => !p.is_invisible).map(p => String(p.id));
        sharedIds = decodeBitmask(shareBitmask, allIds);
      } else if (sharedIds) {
        sharedIds = sharedIds.map(tk => {
          if (tk.startsWith('SYS-')) {
            const house = fullList.find(h => h.system_id === tk);
            return house ? String(house.id) : null;
          }
          if (/^\d+$/.test(tk)) {
            const idx = parseInt(tk, 10) - 1;
            return fullList[idx] ? String(fullList[idx].id) : null;
          }
          return tk;
        }).filter(Boolean);
      }

      if (sharedIds) {
        DATA = fullList.filter(p => sharedIds.map(String).includes(String(p.id)) && !p.is_invisible);
      } else if (!isAdmin) {
        DATA = [];
        showError('Vui lòng liên hệ Khang Ngô Nhà Phố để được cung cấp thông tin.');
      } else {
        DATA = fullList.filter(p => !p.is_invisible);
      }

      if (DATA.length > 0) {
        trackAction("Mở danh sách nhà", `Số lượng hiển thị: ${DATA.length} căn`);
      }

      buildDistrictTabs();
      restoreState();
      updateSortButtonsUI();

      buildWardTabs();
      buildDuongTabs();
      buildHuongTabs();
      updateFilterSummary();
      updateStats();
      render();
      if (isAdmin) {
        autoLoginOrSilentRefresh();
      }
    }

    function showError(msg) {
      const list = document.getElementById('list');
      list.innerHTML = '';
      list.insertAdjacentHTML('beforeend', `
    <div class="err-box">
      <h3>🏠 Thông báo</h3>
      <p style="font-size: 15px; font-weight: 500;">Vui lòng liên hệ <b>Khang Ngô Nhà Phố</b> để được cung cấp thông tin.</p>
    </div>`);
    }

    // ── Local Storage State ──
    function saveState() {
      if (!isAdmin || shareBitmask || shareToken) return;
      const state = {
        districts: [...selDistricts],
        wards: [...selWards],
        duongs: [...selDuongs],
        huongs: [...selHuong],
        gia: [...selGia],
        danhGia: [...selDanhGia],
        selectedIds: [...SELECTED_IDS],
        favOnly: showFavOnly,
        search: document.getElementById('searchInput')?.value || ''
      };
      localStorage.setItem('adminState', JSON.stringify(state));
    }

    function restoreState() {
      if (!isAdmin || shareBitmask || shareToken) return;
      try {
        const saved = localStorage.getItem('adminState');
        if (!saved) return;
        const state = JSON.parse(saved);

        state.districts?.forEach(x => selDistricts.add(x));
        state.wards?.forEach(x => selWards.add(x));
        state.duongs?.forEach(x => selDuongs.add(x));
        state.huongs?.forEach(x => selHuong.add(x));
        state.gia?.forEach(x => selGia.add(x));
        state.danhGia?.forEach(x => selDanhGia.add(x));
        state.selectedIds?.forEach(x => SELECTED_IDS.add(x));

        if (state.favOnly !== undefined) showFavOnly = state.favOnly;

        const sInput = document.getElementById('searchInput');
        if (sInput && state.search) {
          sInput.value = state.search;
          toggleSearchClearBtn();
        }

        syncTabUI('districtTabs', selDistricts);
        syncTabUI('giaTabs', selGia);
        syncTabUI('danhGiaTabs', selDanhGia);

        updateSortButtonsUI();
        updateFavBtnUI();

        const sc = document.getElementById('shareCount');
        if (sc) sc.textContent = SELECTED_IDS.size;
      } catch (e) {
        console.error('Lỗi restore state:', e);
      }
    }

    function updateStats() {
      const arr = getFiltered();
      if (!arr.length) { document.getElementById('totalBadge').textContent = '0 BĐS'; return; }
      const gias = arr.map(p => parseFloat(p.gia)).filter(Boolean);
      const dts = arr.map(p => parseFloat(p.dt)).filter(Boolean);
      const tangs = arr.map(p => parseFloat(p.tang)).filter(Boolean);
      const quans = [...new Set(arr.map(p => p.q).filter(Boolean))].length;
      document.getElementById('sTong').textContent = arr.length;
      document.getElementById('sTang').textContent = tangs.length ? `${Math.min(...tangs)}–${Math.max(...tangs)}` : '-';
      document.getElementById('sGia').textContent = gias.length ? `${Math.min(...gias).toFixed(1)}–${Math.max(...gias).toFixed(1)}` : '-';
      document.getElementById('sDt').textContent = dts.length ? `${Math.min(...dts)}–${Math.max(...dts)}` : '-';
      document.getElementById('sQuan').textContent = quans || '-';
      document.getElementById('totalBadge').textContent = `${arr.length} BĐS`;
    }

    // ── Filter panel toggle ──
    function toggleFilter() {
      filterOpen = !filterOpen;
      document.getElementById('filterPanel').classList.toggle('open', filterOpen);
      const btn = document.getElementById('filterBtn');
      btn.classList.toggle('active', filterOpen);
    }
    function closeFilter() {
      if (!filterOpen) return;
      filterOpen = false;
      document.getElementById('filterPanel').classList.remove('open');
      const btn = document.getElementById('filterBtn');
      const anyActive = !!(selDistricts.size || selWards.size || selDuongs.size || selHuong.size || selGia.size || selDanhGia.size);
      btn.classList.toggle('active', anyActive);
    }

    // ── Build district tabs dynamically ──
    function buildDistrictTabs() {
      const districtsInPool = [...new Set(DATA.map(p => p.q).filter(Boolean))];
      const dNamesFull = {
        q1: 'Quận 1', q2: 'Quận 2', q3: 'Quận 3', q4: 'Quận 4', q5: 'Quận 5', q6: 'Quận 6',
        q7: 'Quận 7', q8: 'Quận 8', q9: 'Quận 9', q10: 'Quận 10', q11: 'Quận 11', q12: 'Quận 12',
        pn: 'Phú Nhuận', tb: 'Tân Bình', bt: 'Bình Thạnh', gv: 'Gò Vấp',
        tp: 'Tân Phú', btan: 'Bình Tân', td: 'Thủ Đức',
        hm: 'Hóc Môn', nb: 'Nhà Bè', bc: 'Bình Chánh', cc: 'Củ Chi', cg: 'Cần Giờ'
      };

      const order = ['q3', 'q10', 'pn', 'tb', 'bt', 'gv', 'q1', 'q2', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q11', 'q12', 'tp', 'btan', 'td', 'hm', 'nb', 'bc', 'cc', 'cg'];
      
      districtsInPool.sort((a, b) => {
        let idxA = order.indexOf(a);
        let idxB = order.indexOf(b);
        if (idxA === -1) idxA = 999;
        if (idxB === -1) idxB = 999;
        return idxA - idxB;
      });

      const container = document.getElementById('districtTabs');
      if (!container) return;

      container.innerHTML = `<button class="tab ${selDistricts.size === 0 ? 'on' : ''}" data-val="all" onclick="tDistrict('all')">Tất cả</button>`
        + districtsInPool.map(d => {
            const name = dNamesFull[d] || d.toUpperCase();
            return `<button class="tab ${selDistricts.has(d) ? 'on' : ''}" data-val="${d}" onclick="tDistrict('${d}')">${name}</button>`;
          }).join('');
    }

    // ── Build ward tabs dynamically ──
    function buildWardTabs() {
      const pool = selDistricts.size ? DATA.filter(p => selDistricts.has(p.q)) : DATA;
      const wards = [...new Set(pool.map(p => p.phuong).filter(w => w && w !== '-'))].sort();
      const wt = document.getElementById('wardTabs');
      const wl = document.getElementById('wardLbl');
      if (!wards.length) { wt.classList.remove('has-wards'); wl.style.display = 'none'; return; }
      wl.style.display = 'block';
      wt.innerHTML = `<button class="tab ${selWards.size === 0 ? 'on' : ''}" data-val="all" onclick="tWard('all')">Tất cả</button>`
        + wards.map(w => `<button class="tab ${selWards.has(w) ? 'on' : ''}" data-val="${w}" onclick="tWard('${w}')">${w}</button>`).join('');
      wt.classList.add('has-wards');
    }

    // ── Build duong tabs dynamically ──
    function buildDuongTabs() {
      let pool = selDistricts.size ? DATA.filter(p => selDistricts.has(p.q)) : DATA;
      if (selWards.size) pool = pool.filter(p => selWards.has(p.phuong));
      const duongs = [...new Set(pool.map(p => p.duong_truoc_nha).filter(d => d && d !== '-'))].sort();
      const dt = document.getElementById('duongTabs');
      const dl = document.getElementById('duongLbl');
      if (!duongs.length) { dt.classList.remove('has-duong'); dl.style.display = 'none'; return; }
      dl.style.display = 'block';
      dt.innerHTML = `<button class="tab ${selDuongs.size === 0 ? 'on' : ''}" data-val="all" onclick="tDuong('all')">Tất cả</button>`
        + duongs.map(d => `<button class="tab ${selDuongs.has(d) ? 'on' : ''}" data-val="${d}" onclick="tDuong('${d}')">${d}</button>`).join('');
      dt.classList.add('has-duong');
    }

    // ── Build huong (direction) tabs dynamically ──
    function buildHuongTabs() {
      let pool = selDistricts.size ? DATA.filter(p => selDistricts.has(p.q)) : DATA;
      if (selWards.size) pool = pool.filter(p => selWards.has(p.phuong));
      const huongs = [...new Set(pool.map(p => p.huong).filter(h => h && h !== '-'))].sort();
      const ht = document.getElementById('huongTabs');
      const hl = document.getElementById('huongLbl');
      if (!huongs.length) { ht.classList.remove('has-huong'); hl.style.display = 'none'; return; }
      hl.style.display = 'block';
      ht.innerHTML = `<button class="tab ${selHuong.size === 0 ? 'on' : ''}" data-val="all" onclick="tHuong('all')">Tất cả</button>`
        + huongs.map(h => `<button class="tab ${selHuong.has(h) ? 'on' : ''}" data-val="${h}" onclick="tHuong('${h}')">${h}</button>`).join('');
      ht.classList.add('has-huong');
    }

    // ── Toggle functions (multi-select) ──
    function tDistrict(val) {
      tSel(selDistricts, val); syncTabUI('districtTabs', selDistricts);
      selWards.clear(); selDuongs.clear(); selHuong.clear();
      buildWardTabs(); buildDuongTabs(); buildHuongTabs();
      updateFilterSummary(); updateStats(); applyFilter();
    }
    function tWard(val) {
      tSel(selWards, val); syncTabUI('wardTabs', selWards);
      selDuongs.clear(); selHuong.clear(); buildDuongTabs(); buildHuongTabs();
      updateFilterSummary(); updateStats(); applyFilter();
    }
    function tDuong(val) {
      tSel(selDuongs, val); syncTabUI('duongTabs', selDuongs);
      updateFilterSummary(); updateStats(); applyFilter();
    }
    function tGia(val) {
      tSel(selGia, val); syncTabUI('giaTabs', selGia);
      updateFilterSummary(); updateStats(); applyFilter();
    }
    function tDanhGia(val) {
      tSel(selDanhGia, val); syncTabUI('danhGiaTabs', selDanhGia);
      updateFilterSummary(); updateStats(); applyFilter();
    }
    function tHuong(val) {
      tSel(selHuong, val); syncTabUI('huongTabs', selHuong);
      updateFilterSummary(); updateStats(); applyFilter();
    }

    function updateFilterSummary() {
      const dNames = {
        q1: 'Q.1', q2: 'Q.2', q3: 'Q.3', q4: 'Q.4', q5: 'Q.5', q6: 'Q.6',
        q7: 'Q.7', q8: 'Q.8', q9: 'Q.9', q10: 'Q.10', q11: 'Q.11', q12: 'Q.12',
        pn: 'P.Nhuận', tb: 'T.Bình', bt: 'B.Thạnh', gv: 'G.Vấp',
        tp: 'T.Phú', btan: 'B.Tân', td: 'T.Đức',
        hm: 'H.Môn', nb: 'N.Bè', bc: 'B.Chánh', cc: 'C.Chi', cg: 'C.Giờ'
      };
      const gNames = { 'lt7': '<7t', '7-10': '7-10t', '10-15': '10-15t', '15-20': '15-20t', 'gt20': '>20t' };
      const parts = [];
      if (selDistricts.size) parts.push([...selDistricts].map(d => dNames[d] || d).join('+'));
      if (selWards.size) parts.push('P.' + [...selWards].join('+'));
      if (selDuongs.size) parts.push([...selDuongs].join('+'));
      if (selHuong.size) parts.push('🧭' + [...selHuong].join('+'));
      if (selGia.size) parts.push([...selGia].map(g => gNames[g] || g).join('+'));
      if (selDanhGia.size) parts.push([...selDanhGia].map(d => d === 'Hàng Ngon' ? '💎' : '⚠️').join(''));
      document.getElementById('filterSummary').textContent = parts.length ? parts.join(' · ') : 'Tất cả';
      const anyActive = !!(selDistricts.size || selWards.size || selDuongs.size || selHuong.size || selGia.size || selDanhGia.size);
      document.getElementById('filterBtn').classList.toggle('active', anyActive || filterOpen);
      document.getElementById('resetBtn').style.display = anyActive ? 'inline-flex' : 'none';

      // Hiển thị dòng thứ 2 (bộ lọc hiện tại) chỉ khi có filter hoạt động
      const bar = document.getElementById('filterBar');
      if (bar) {
        bar.style.display = (isAdmin && anyActive) ? 'flex' : 'none';
      }

      saveState();
    }

    function resetFilters() {
      selDistricts.clear(); selWards.clear(); selDuongs.clear(); selHuong.clear(); selGia.clear(); selDanhGia.clear();
      buildDistrictTabs();
      syncTabUI('districtTabs', selDistricts);
      syncTabUI('giaTabs', selGia);
      syncTabUI('danhGiaTabs', selDanhGia);

      // Xóa ô tìm kiếm
      const sInput = document.getElementById('searchInput');
      if (sInput) sInput.value = '';
      toggleSearchClearBtn();

      // Ward, Duong & Huong tabs cần rebuild vì là dynamic
      buildWardTabs(); buildDuongTabs(); buildHuongTabs();
      updateFilterSummary(); updateStats(); applyFilter();
    }

    function updateSortButtonsUI() {
      const btnNew = document.getElementById('sortNewBtn');
      const btnPrice = document.getElementById('sortPriceBtn');
      if (!btnNew || !btnPrice) return;

      if (currentSortType === 'newest') {
        btnNew.classList.add('active');
        btnNew.textContent = currentSortDir === 'desc' ? '⏱️⬇' : '⏱️⬆';
        btnPrice.classList.remove('active');
        btnPrice.textContent = '💰';
      } else {
        btnPrice.classList.add('active');
        btnPrice.textContent = currentSortDir === 'desc' ? '💰⬇' : '💰⬆';
        btnNew.classList.remove('active');
        btnNew.textContent = '⏱️';
      }
    }

    function toggleSortNew() {
      if (currentSortType === 'newest') {
        currentSortDir = currentSortDir === 'desc' ? 'asc' : 'desc';
      } else {
        currentSortType = 'newest';
        currentSortDir = 'desc';
      }
      updateSortButtonsUI();
      saveState();
      render();
    }

    function toggleSortPrice() {
      if (currentSortType === 'price') {
        currentSortDir = currentSortDir === 'desc' ? 'asc' : 'desc';
      } else {
        currentSortType = 'price';
        currentSortDir = 'desc';
      }
      updateSortButtonsUI();
      saveState();
      render();
    }

    function updateFavBtnUI() {
      const btn = document.getElementById('favFilterBtn');
      const badge = document.getElementById('favCount');
      if (!btn || !badge) return;
      btn.classList.toggle('active', showFavOnly);
      btn.innerHTML = showFavOnly ? '♥' : '♡';
      if (favs.size > 0) {
        badge.textContent = favs.size;
        badge.style.display = 'flex';
      } else {
        badge.style.display = 'none';
      }
    }

    function toggleFavFilter() {
      if (!isAdmin) {
        showFavOnly = !showFavOnly;
        updateFavBtnUI();
        saveState();
        updateStats(); applyFilter();
      } else {
        openColViewModal();
      }
    }

    function render() {
      const list = document.getElementById('list');
      list.innerHTML = '';
      const arr = DATA.slice().sort((a, b) => {
        if (currentSortType === 'newest') {
          const ta = parseInt(a.temp_id, 10) || 0;
          const tb = parseInt(b.temp_id, 10) || 0;
          return currentSortDir === 'asc' ? ta - tb : tb - ta;
        } else {
          const ga = parseFloat(a.gia) || 0, gb = parseFloat(b.gia) || 0;
          return currentSortDir === 'asc' ? ga - gb : gb - ga;
        }
      });

      if (!arr.length) {
        list.insertAdjacentHTML('beforeend', '<div style="text-align:center;padding:60px 20px;color:var(--sub);font-weight:500;">Vui lòng liên hệ Khang Ngô Nhà Phố để được cung cấp thông tin.</div>');
        return;
      }

      const frag = document.createDocumentFragment();
      arr.forEach((p, i) => {
        const imgUrls = p.imgs.filter(u => !u.includes('facebook.com') && !u.includes('fb.watch') && !u.includes('fb.gg'));
        let thumbUrl = (isAdmin && p.img_mat_tien) ? p.img_mat_tien : imgUrls[0];
        const thumb = thumbUrl ? fixImgUrl(thumbUrl, 'w400') : 'https://via.placeholder.com/300x200?text=No+Photo';
        const c = document.createElement('div');
        c.className = 'card';
        c.dataset.pid = String(p.id);
        c.setAttribute('onclick', `openS('${p.id}')`);

        if (isAdmin) {
          c.innerHTML = `
        <div class="crow">
          <div class="ibox">
            <img src="${thumb}" alt="${p.t}" loading="lazy" onload="this.parentElement.classList.add('is-loaded'); this.classList.add('loaded');">
            <div style="position: absolute; bottom: 0; left: 0; right: 0; background: rgba(52, 152, 219, 0.9); color: white; text-align: center; font-size: 11px; font-weight: 700; padding: 4px 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-transform: uppercase;">
              ${p.tinh_trang || 'Bình thường'}
            </div>
            <input type="checkbox" class="card-sel" onclick="event.stopPropagation()" onchange="toggleSelect('${p.id}', this)" ${SELECTED_IDS.has(String(p.id)) ? 'checked' : ''}>
            <button class="heart ${favs.has(String(p.id)) ? 'on' : ''}" onclick="th('${p.id}', this, event)">${favs.has(String(p.id)) ? '♥' : '♡'}</button>
          </div>
          <div class="card-right">
            <div class="info">
              <div class="ititle" style="color: var(--red); font-weight: 850; font-size: 14.5px; line-height: 1.35; margin-bottom: 6px;">
                ${p.raw_so_nha ? p.raw_so_nha + ' ' : ''}${p.raw_ten_duong ? p.raw_ten_duong : p.t} ${p.cu_phap ? '| ' + p.cu_phap : ''}
              </div>
              <div style="font-size: 12px; margin-bottom: 4px; color: #2c3e50; font-weight: 600; display: flex; align-items: center; gap: 4px;">
                <span>📍</span> P.${p.phuong}, Q.${p.ql}
              </div>
              <div style="font-size: 12px; margin-bottom: 4px; color: #2c3e50; font-weight: 600; display: flex; align-items: center; gap: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                <span>👤</span> ${p.raw_ten_dau_chu || 'Chưa rõ đầu chủ'}
              </div>
              <div style="font-size: 12.5px; color: var(--red); font-weight: 700; display: flex; align-items: center; gap: 4px;">
                <span>📞</span> 
                ${p.raw_dt_dau_chu ? `<a href="tel:${p.raw_dt_dau_chu}" onclick="event.stopPropagation();" style="color: var(--red); text-decoration: underline; font-weight: 800;">${p.raw_dt_dau_chu}</a>` : 'Chưa có SĐT'}
              </div>
            </div>
            <div class="cfoot" style="margin-top: 6px;">
              ${activeCollectionName ? `<button class="remove-from-col-btn" onclick="removeFromCol('${p.id}', '${activeCollectionName}', event)">✕ Bỏ</button>` : ''}
              <div style="font-size: 12px; font-weight: 700; color: #2c3e50; display: flex; align-items: center; gap: 6px;">
                <span style="background: rgba(39, 174, 96, 0.15); color: #27ae60; padding: 2px 6px; border-radius: 4px; font-size: 11px;">${p.gia} tỷ</span>
                <span style="background: rgba(52, 152, 219, 0.15); color: #3498db; padding: 2px 6px; border-radius: 4px; font-size: 11px;">#${p.id}</span>
              </div>
            </div>
          </div>
        </div>`;
        } else {
          c.innerHTML = `
        <div class="crow">
          <div class="ibox">
            <img src="${thumb}" alt="${p.t}" loading="lazy" onload="this.parentElement.classList.add('is-loaded'); this.classList.add('loaded');">
            ${isAdmin ? `<input type="checkbox" class="card-sel" onclick="event.stopPropagation()" onchange="toggleSelect('${p.id}', this)" ${SELECTED_IDS.has(String(p.id)) ? 'checked' : ''}>` : ''}
            <button class="heart ${favs.has(String(p.id)) ? 'on' : ''}" onclick="th('${p.id}', this, event)">${favs.has(String(p.id)) ? '♥' : '♡'}</button>
          </div>
          <div class="card-right">
            <div class="info">
              <div class="ititle">${p.t}</div>
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
        }
        frag.appendChild(c);
      });
      list.appendChild(frag);
      applyFilter();
    }

    // Lọc nhanh bằng ẩn/hiện card (không tạo lại DOM)
    function applyFilter() {
      const filteredIds = new Set(getFiltered().map(p => String(p.id)));
      const cards = document.querySelectorAll('#list .card');
      let visibleCount = 0;
      cards.forEach(c => {
        const show = filteredIds.has(c.dataset.pid);
        c.style.display = show ? '' : 'none';
        if (show) visibleCount++;
      });
      // Hiện thông báo nếu không có kết quả
      let noResult = document.getElementById('noResultMsg');
      if (!visibleCount) {
        if (!noResult) {
          const d = document.createElement('div');
          d.id = 'noResultMsg';
          d.style.cssText = 'text-align:center;padding:60px 20px;color:var(--sub);font-weight:500;';
          d.textContent = 'Không tìm thấy căn nào phù hợp.';
          document.getElementById('list').appendChild(d);
        }
      } else if (noResult) {
        noResult.remove();
      }
    }



    function th(id, b, e) {
      if (e) e.stopPropagation();
      const sid = String(id);
      if (favs.has(sid)) {
        favs.delete(sid);
        b.classList.remove('on');
        b.textContent = '♡';
      } else {
        favs.add(sid);
        b.classList.add('on');
        b.textContent = '♥';
      }
      localStorage.setItem('favs', JSON.stringify([...favs]));
      updateFavBtnUI();
      if (showFavOnly) { updateStats(); render(); }
    }

    // ── Lightbox Logic ──
    let lbIdx = 0;
    let currentImgs = [];
    function openLb(i) {
      lbIdx = i;
      document.getElementById('lbOverlay').classList.add('open');
      renderLbMain(); renderLbThumbs();
    }
    function closeLb() {
      document.getElementById('lbOverlay').classList.remove('open');
      document.getElementById('lbMain').innerHTML = ''; // Stop video
    }
    function lbMove(d) {
      lbIdx = (lbIdx + d + currentImgs.length) % currentImgs.length;
      renderLbMain(); updateLbThumbsUI();
    }
    function goToLb(i) {
      lbIdx = i; renderLbMain(); updateLbThumbsUI();
    }
    function renderLbMain() {
      const s = currentImgs[lbIdx];
      const main = document.getElementById('lbMain');
      if (s.includes('facebook.com') || s.includes('fb.watch') || s.includes('fb.gg')) {
        const encoded = encodeURIComponent(s);
        main.innerHTML = `<iframe src="https://www.facebook.com/plugins/video.php?href=${encoded}&show_text=false&autoplay=1" style="width:auto;height:100%;max-width:100%;aspect-ratio:9/16;margin:0 auto;display:block;border:none;overflow:hidden;" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>`;
      } else {
        main.innerHTML = `<img src="${s}" alt="Ảnh phóng to">`;
      }
    }
    function renderLbThumbs() {
      document.getElementById('lbThumbs').innerHTML = currentImgs.map((s, i) => {
        if (s.includes('facebook.com') || s.includes('fb.watch') || s.includes('fb.gg')) {
          return `<div class="lb-thumb-vid ${i === lbIdx ? 'on' : ''}" onclick="goToLb(${i})" id="lbt-${i}">▶</div>`;
        } else {
          const thumbSrc = fixImgUrl(s, 'w200');
          return `<img src="${thumbSrc}" class="lb-thumb ${i === lbIdx ? 'on' : ''}" onclick="goToLb(${i})" id="lbt-${i}">`;
        }
      }).join('');
    }
    function updateLbThumbsUI() {
      document.querySelectorAll('.lb-thumb, .lb-thumb-vid').forEach((el, i) => {
        el.classList.toggle('on', i === lbIdx);
        if (i === lbIdx) el.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      });
    }

    // ── Gallery ──
    let gI = 0, gN = 0, tx = 0;
    function buildG(imgs) {
      gI = 0; gN = imgs.length; currentImgs = imgs;
      const gt = document.getElementById('gt'), gd = document.getElementById('gd');
      gt.innerHTML = ''; gd.innerHTML = '';
      if (!imgs.length) { document.getElementById('gw').style.display = 'none'; return; }
      document.getElementById('gw').style.display = '';
      imgs.forEach((s, i) => {
        const sl = document.createElement('div'); sl.className = 'gslide';
        if (s.includes('facebook.com') || s.includes('fb.watch') || s.includes('fb.gg')) {
          const encoded = encodeURIComponent(s);
          sl.innerHTML = `
        <div onclick="openLb(${i})" style="position:absolute; inset:0; z-index:10; cursor:pointer;"></div>
        <iframe src="https://www.facebook.com/plugins/video.php?href=${encoded}&show_text=false" style="width:auto;height:100%;max-width:100%;aspect-ratio:9/16;margin:0 auto;display:block;border:none;overflow:hidden;" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>`;
        } else {
          sl.innerHTML = `<img src="${s}" alt="Ảnh ${i + 1}" loading="${i === 0 ? 'eager' : 'lazy'}" onclick="openLb(${i})">`;
        }
        gt.appendChild(sl);
        const d = document.createElement('div'); d.className = 'dot' + (i === 0 ? ' on' : '');
        gd.appendChild(d);
      });
      gt.style.transform = 'translateX(0)'; ua();
      const gw = document.getElementById('gw');

      // Xử lý vuốt ảnh mượt mà và chặn lệnh "Back" của iPhone
      gw.ontouchstart = e => {
        tx = e.touches[0].clientX;
        ty = e.touches[0].clientY;
      };

      gw.ontouchmove = e => {
        const dx = tx - e.touches[0].clientX;
        const dy = ty - e.touches[0].clientY;
        // Nếu vuốt ngang nhiều hơn vuốt dọc -> Chặn lệnh của trình duyệt
        if (Math.abs(dx) > Math.abs(dy)) {
          if (e.cancelable) e.preventDefault();
        }
      };

      gw.ontouchend = e => {
        const dx = tx - e.changedTouches[0].clientX;
        if (Math.abs(dx) > 40) gm(dx > 0 ? 1 : -1);
      };
    }
    function gm(d) {
      gI = Math.max(0, Math.min(gN - 1, gI + d));
      document.getElementById('gt').style.transform = `translateX(-${gI * 100}%)`;
      document.querySelectorAll('.dot').forEach((x, i) => x.classList.toggle('on', i === gI));
      ua();
    }
    function ua() {
      document.getElementById('al').style.display = gI === 0 ? 'none' : 'flex';
      document.getElementById('ar').style.display = gI === gN - 1 ? 'none' : 'flex';
    }

    function openS(id) {
      const p = DATA.find(x => String(x.id) === String(id));
      if (!p) return;

      // Tracking: Xem chi tiết căn nhà
      trackAction("Xem chi tiết", `#${p.id} - ${p.t}`);

      document.getElementById('mT').textContent = p.t;
      document.getElementById('mID').textContent = `#${p.id}`;
      
      const sbody = document.getElementById('sbody');
      const scta = document.querySelector('.scta');

      if (isAdmin && p.original_row_data) {
        if (scta) scta.style.display = 'none';
        
        sbody.innerHTML = `
          <div class="admin-accordion">
            <!-- ACCORDION 1: THÔNG TIN THÔ - POOL -->
            <div class="accordion-item expanded" id="accPool">
              <div class="accordion-header active" onclick="toggleAdminAccordion(this)">
                <span>📢 THÔNG TIN THÔ - POOL</span>
                <span class="arrow">▼</span>
              </div>
              <div class="accordion-content" style="display:block;">
                <!-- Carousels -->
                <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px;">
                  <div>
                    <div class="admin-detail-section-title">🏠 HÌNH ẢNH NHÀ (NỘI THẤT SẠCH)</div>
                    <div id="carouselNha" style="position: relative;">
                      <div class="admin-scroll-carousel"></div>
                      <div class="admin-carousel-dots"></div>
                    </div>
                  </div>
                  <div>
                    <div class="admin-detail-section-title">📜 SƠ ĐỒ THỬA ĐẤT (ẢNH SỔ)</div>
                    <div id="carouselSo" style="position: relative;">
                      <div class="admin-scroll-carousel"></div>
                      <div class="admin-carousel-dots"></div>
                    </div>
                  </div>
                </div>

                <!-- Technical Specs Dotted Grid -->
                <div class="admin-raw-header-row">
                  <span class="admin-ma-hang">#${p.id}</span>
                  <span class="admin-status-badge">${p.tinh_trang || 'Bình thường'}</span>
                </div>
                <div class="admin-raw-section">
                  <div class="admin-raw-title">📊 THÔNG SỐ KỸ THUẬT THÔ</div>
                  <div class="admin-raw-grid">
                    <div class="admin-raw-cell">
                      <span class="label">DT trên sổ:</span>
                      <span class="value dotted">${p.raw_dt_tren_so || p.dt || '-'} m²</span>
                    </div>
                    <div class="admin-raw-cell">
                      <span class="label">Giá chào:</span>
                      <span class="value dotted" style="color:var(--red); font-weight:800;">${p.raw_gia_chao || p.gia || '-'} tỷ</span>
                    </div>
                    <div class="admin-raw-cell">
                      <span class="label">Ngang/mặt tiền:</span>
                      <span class="value dotted">${p.raw_mat_tien || p.mat || '-'} m</span>
                    </div>
                    <div class="admin-raw-cell">
                      <span class="label">Chiều dài sâu:</span>
                      <span class="value dotted">${p.dai_nha || '-'} m</span>
                    </div>
                    <div class="admin-raw-cell">
                      <span class="label">Độ rộng hẻm:</span>
                      <span class="value dotted">${p.raw_do_rong_hem || p.rong_hem || '-'} m</span>
                    </div>
                    <div class="admin-raw-cell">
                      <span class="label">Kết cấu:</span>
                      <span class="value dotted">${p.raw_so_tang || p.tang || '-'} tầng</span>
                    </div>
                  </div>
                </div>

                <div class="admin-raw-section" style="margin-top: 14px;">
                  <div class="admin-raw-title">👤 THÔNG TIN NGUỒN CHỦ</div>
                  <div class="admin-raw-source">
                    <div style="display:flex; justify-content:space-between;">
                      <span style="color:#57606f;">Tên đầu chủ:</span>
                      <span style="font-weight:700;">${p.raw_ten_dau_chu || '-'}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                      <span style="color:#57606f;">SĐT đầu chủ:</span>
                      <span>
                        ${p.raw_dt_dau_chu ? `<a href="tel:${p.raw_dt_dau_chu}" class="dotted-val" style="color:var(--blue);">${p.raw_dt_dau_chu}</a>` : '-'}
                      </span>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                      <span style="color:#57606f;">Link Facebook:</span>
                      <span>
                        ${p.raw_link_fb ? `<a href="${p.raw_link_fb}" target="_blank" class="dotted-val" style="color:var(--blue);">Xem FB Đầu Chủ ↗</a>` : '-'}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Google Maps Embed -->
                <div class="admin-raw-title" style="margin-top:16px;">🗺️ BẢN ĐỒ THỰC ĐỊA</div>
                <div class="admin-map-container"></div>

                <!-- Mô tả boxed -->
                <div class="admin-mota-title">NỘI DUNG CHÍNH (THÔ)</div>
                <div class="admin-mota-box red-text">${p.raw_noi_dung_chinh || 'Chưa có nội dung chính.'}</div>

                <div class="admin-mota-title">MÔ TẢ CHI TIẾT (THÔ)</div>
                <div class="admin-mota-box black-text collapsible-box" id="adminMotaGocBox">${p.raw_mo_ta_chi_tiet || p.m || 'Chưa có mô tả chi tiết.'}</div>
                <button class="btn-show-more" id="btnExpandMotaGoc" onclick="toggleMotaGocCollapse()" style="display:none;">Xem thêm ▼</button>
              </div>
            </div>

            <!-- ACCORDION 2: BIÊN TẬP CUSTOM - SOURCE -->
            <div class="accordion-item" id="accSource">
              <div class="accordion-header" onclick="toggleAdminAccordion(this)">
                <span>✍️ BIÊN TẬP CUSTOM - SOURCE</span>
                <span class="arrow">▶</span>
              </div>
              <div class="accordion-content">
                <form class="admin-edit-form" onsubmit="event.preventDefault()">
                  <div class="admin-edit-group">
                    <label for="editNote">Ghi chú riêng (Note - Chỉ Admin thấy):</label>
                    <textarea id="editNote" rows="3" placeholder="Nhập ghi chú riêng...">${p.note || ''}</textarea>
                  </div>

                  <div class="admin-edit-group">
                    <label for="editTieuDeBds">Tiêu đề public (dưới 85 ký tự):</label>
                    <input type="text" id="editTieuDeBds" value="${p.original_row_data[39] || ''}" placeholder="Nhập tiêu đề BĐS ngắn gọn...">
                  </div>

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
                        <option value="Hẻm xe tải lý thuyết">Hẻm xe tải lý thuyết</option>
                        <option value="Hẻm xe tải">Hẻm xe tải</option>
                        <option value="Mặt tiền">Mặt tiền</option>
                      </select>
                    </div>
                  </div>

                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="admin-edit-group">
                      <label for="editDanhGia">Đánh giá:</label>
                      <select id="editDanhGia">
                        <option value="">Bình thường</option>
                        <option value="Hàng Ngon">💎 Ngon</option>
                        <option value="Hàng Lỗi">⚠️ Lỗi</option>
                      </select>
                    </div>

                    <div class="admin-edit-group">
                      <label for="editRongHem">Rộng hẻm (m):</label>
                      <input type="number" id="editRongHem" step="0.1" value="${p.rong_hem !== '-' ? p.rong_hem : ''}" placeholder="Độ rộng (m)...">
                    </div>
                  </div>

                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="admin-edit-group">
                      <label for="editSoPn">Số phòng ngủ:</label>
                      <input type="number" id="editSoPn" value="${p.so_pn !== '-' ? p.so_pn : ''}" placeholder="Số phòng...">
                    </div>

                    <div class="admin-edit-group">
                      <label for="editSoWc">Số WC:</label>
                      <input type="number" id="editSoWc" value="${p.original_row_data[33] !== '-' ? p.original_row_data[33] : ''}" placeholder="Số WC...">
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

            <!-- ACCORDION 3: PREVIEW KHÁCH HÀNG -->
            <div class="accordion-item" id="accPreview">
              <div class="accordion-header" onclick="toggleAdminAccordion(this)">
                <span>📄 PREVIEW KHÁCH HÀNG</span>
                <span class="arrow">▶</span>
              </div>
              <div class="accordion-content">
                <div style="font-size:14.5px; font-weight:700; color:#1c1c1e; margin-bottom:8px; line-height:1.4;">${p.t}</div>
                <div class="ig" style="display:grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 12px;">
                  <div class="ib"><div class="il">Giá bán</div><div class="iv hi">${p.gia} tỷ</div></div>
                  <div class="ib"><div class="il">Diện tích</div><div class="iv">${p.dt} m²</div></div>
                  <div class="ib"><div class="il">Đơn giá</div><div class="iv" style="color:var(--gold);font-weight:800">${p.giabq}</div></div>
                  <div class="ib"><div class="il">Quận/TP</div><div class="iv">${p.ql}</div></div>
                  <div class="ib"><div class="il">Phường</div><div class="iv">${p.phuong}</div></div>
                  <div class="ib"><div class="il">Loại</div><div class="iv">${p.loai_hinh}</div></div>
                  <div class="ib"><div class="il">Đường trước</div><div class="iv">${p.duong_truoc_nha}</div></div>
                  <div class="ib"><div class="il">Số tầng</div><div class="iv">${p.tang}</div></div>
                </div>
                <div class="desc" style="white-space:pre-wrap; line-height:1.6; font-size:13.5px; color:#2c3e50; background:#f8f9fa; padding:12px; border-radius:8px;">${p.m}</div>
              </div>
            </div>
          </div>
          <div class="admin-sticky-footer">
            <button class="admin-save-btn" id="saveBtn" onclick="saveSourceChanges('${p.id}')">💾 LƯU THAY ĐỔI</button>
          </div>
        `;
      } else {
        if (scta) scta.style.display = 'flex';
        
        const sortedImgs = [...p.imgs].sort((a, b) => {
          const aVis = (a.includes('facebook.com') || a.includes('fb.watch') || a.includes('fb.gg')) ? 1 : 0;
          const bVis = (b.includes('facebook.com') || b.includes('fb.watch') || b.includes('fb.gg')) ? 1 : 0;
          return bVis - aVis;
        });
        
        sbody.innerHTML = `
          <div class="gwrap" id="gw">
            <div class="gtrack" id="gt"></div>
            <div class="gdots" id="gd"></div>
            <button class="garr al" id="al" onclick="gm(-1)">‹</button>
            <button class="garr ar" id="ar" onclick="gm(1)">›</button>
          </div>
          <div class="ig" id="mG">
            <div class="ib"><div class="il">Giá bán</div><div class="iv hi">${p.gia} tỷ</div></div>
            <div class="ib"><div class="il">Diện tích</div><div class="iv">${p.dt} m²</div></div>
            <div class="ib"><div class="il">Đơn giá</div><div class="iv" style="color:var(--gold);font-weight:800">${p.giabq}</div></div>
            <div class="ib"><div class="il">Quận/TP</div><div class="iv">${p.ql}</div></div>
            <div class="ib"><div class="il">Phường</div><div class="iv">${p.phuong}</div></div>
            <div class="ib"><div class="il">Loại</div><div class="iv">${p.loai_hinh}</div></div>
            <div class="ib"><div class="il">Đường trước</div><div class="iv">${p.duong_truoc_nha}</div></div>
            <div class="ib"><div class="il">Rộng hẻm</div><div class="iv">${p.rong_hem} m</div></div>
            <div class="ib"><div class="il">Số tầng</div><div class="iv">${p.tang}</div></div>
            <div class="ib"><div class="il">Mặt tiền</div><div class="iv">${p.mat} m</div></div>
            <div class="ib"><div class="il">Hướng</div><div class="iv">${p.huong}</div></div>
            <div class="ib"><div class="il">Tình trạng</div><div class="iv">${p.tinh_trang}</div></div>
            <div class="ib"><div class="il">Ngủ tầng trệt</div><div class="iv">${p.ngu_tang_tret}</div></div>
            <div class="ib"><div class="il">CHDV</div><div class="iv">${p.chdv}</div></div>
          </div>
          <div class="desc" id="mD">${p.m}</div>
        `;
        buildG(sortedImgs.map(url => fixImgUrl(url, 'w1200')));
      }

      const btnZalo = document.getElementById('mZalo');
      if (btnZalo) {
        btnZalo.textContent = `💬 Tư vấn ngay căn này`;
        btnZalo.onclick = () => askZalo(p.id, p.t);
      }

      if (isAdmin && p.original_row_data) {
        setTimeout(() => {
          const editHuong = document.getElementById('editHuong');
          if (editHuong) editHuong.value = p.huong || '-';

          const editDuong = document.getElementById('editDuong');
          if (editDuong) editDuong.value = p.duong_truoc_nha || '-';

          const editDanhGia = document.getElementById('editDanhGia');
          if (editDanhGia) editDanhGia.value = p.danh_gia || '';

          checkMoTaCollapse();
          
          const mapContainer = document.querySelector('.admin-map-container');
          if (mapContainer) {
            const fullAddress = `${p.raw_so_nha || ''} ${p.raw_ten_duong || ''}, Phường ${p.phuong || ''}, ${p.ql || ''}, Hồ Chí Minh`.trim();
            mapContainer.innerHTML = `<iframe width="100%" height="100%" frameborder="0" style="border:0;" src="https://maps.google.com/maps?q=${encodeURIComponent(fullAddress)}&t=&z=16&ie=UTF8&iwloc=&output=embed" allowfullscreen></iframe>`;
          }

          const nImgs = p.imgs || [];
          setupScrollCarousel('carouselNha', nImgs, false);

          const sImgs = [];
          if (p.raw_sodo1) sImgs.push(p.raw_sodo1);
          if (p.raw_sodo2) sImgs.push(p.raw_sodo2);
          setupScrollCarousel('carouselSo', sImgs, true);
        }, 50);
      }

      document.getElementById('ov').classList.add('open');
      document.getElementById('sbody').scrollTop = 0;
      document.body.style.overflow = 'hidden';
    }
    function closeS() { document.getElementById('ov').classList.remove('open'); document.body.style.overflow = ''; }
    function bgC(e) { if (e.target === document.getElementById('ov')) closeS(); }

    // Admin Tools
    function toggleSelect(id, el) {
      if (el.checked) SELECTED_IDS.add(String(id));
      else SELECTED_IDS.delete(String(id));
      updateShareUI();
      saveState();
    }

    async function generateShareLink() {
      try {
        if (SELECTED_IDS.size === 0) {
          alert('Vui lòng chọn ít nhất 1 căn nhà!');
          return;
        }

        const baseUrl = window.location.origin + window.location.pathname;
        const count = SELECTED_IDS.size;
        let shareUrl = '';

        if (count === 1) {
          // Lấy duy nhất 1 ID được chọn để kích hoạt dynamic preview trên Vercel
          const singleId = [...SELECTED_IDS][0];
          const house = DATA.find(p => String(p.id) === String(singleId));
          const systemId = house ? house.system_id : singleId;
          shareUrl = `${baseUrl}?s=${systemId}`;
        } else {
          // Mã hoá bằng bitmask: mỗi căn = 1 bit, nén thành chuỗi ngắn
          const allIds = DATA.map(p => String(p.id));
          let bits = '';
          allIds.forEach(id => bits += SELECTED_IDS.has(id) ? '1' : '0');
          // Pad to multiple of 6
          while (bits.length % 6) bits += '0';
          let encoded = '';
          for (let i = 0; i < bits.length; i += 6) {
            encoded += B64[parseInt(bits.substr(i, 6), 2)];
          }
          shareUrl = `${baseUrl}?b=${encoded}`;
        }

        // Dùng Web Share API trên điện thoại
        if (navigator.share) {
          navigator.share({
            title: 'Khang Ngô Nhà Phố - ' + count + ' căn',
            url: shareUrl
          }).catch(() => { });
          return;
        }

        // Desktop: copy
        const ta = document.createElement('textarea');
        ta.value = shareUrl;
        ta.style.cssText = 'position:fixed;left:0;top:0;opacity:0;';
        document.body.appendChild(ta);
        ta.focus(); ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        alert('Đã copy link gửi khách!\n(' + count + ' căn)\n\nDán link này vào Zalo để gửi cho khách nhé.');
      } catch (e) {
        alert('Có lỗi xảy ra: ' + e.message);
      }
    }

    // Giai đoạn 1: Tạo Link kèm Tên Khách (Hiển thị Form Modal)
    function promptGenerateLink() {
      if (SELECTED_IDS.size === 0) {
        alert('Vui lòng chọn ít nhất 1 căn nhà để tạo link!');
        return;
      }
      document.getElementById('linkModalCount').textContent = SELECTED_IDS.size;
      document.getElementById('linkCustName').value = '';
      document.getElementById('linkCustTitle').value = ''; // Reset tiêu đề tùy chỉnh
      document.getElementById('linkCustNote').value = '';
      document.getElementById('linkModal').classList.add('open');
    }

    // Xử lý tạo link sau khi điền Form
    function executeGenerateLink() {
      const cName = document.getElementById('linkCustName').value.trim();
      if (!cName) {
        alert("Vui lòng nhập Tên khách hàng!");
        return;
      }

      const cTitle = document.getElementById('linkCustTitle').value.trim();
      const cNote = document.getElementById('linkCustNote').value.trim();

      // Tối ưu hóa chuỗi ghép bằng phân tách '|' và loại bỏ trường trống ở đuôi (US-034)
      let parts = [cName];
      if (cTitle) {
        parts.push(cNote || "");
        parts.push(cTitle);
      } else if (cNote) {
        parts.push(cNote);
      }
      const compactCustomerString = parts.join('|');

      try {
        // Encode và loại bỏ hoàn toàn dấu padding '=' (Base64URL)
        const encodedName = window.btoa(unescape(encodeURIComponent(compactCustomerString))).replace(/=/g, '');
        const baseUrl = window.location.origin + window.location.pathname;
        const count = SELECTED_IDS.size;
        let shareUrl = '';

        if (count === 1) {
          // Lấy duy nhất 1 ID được chọn để kích hoạt dynamic preview trên Vercel
          const singleId = [...SELECTED_IDS][0];
          const house = DATA.find(p => String(p.id) === String(singleId));
          const systemId = house ? house.system_id : singleId;
          shareUrl = `${baseUrl}?s=${systemId}&c=${encodeURIComponent(encodedName)}`;
        } else {
          // Mã hoá bằng bitmask: mỗi căn = 1 bit, nén thành chuỗi ngắn
          const allIds = DATA.map(p => String(p.id));
          let bits = '';
          allIds.forEach(id => bits += SELECTED_IDS.has(id) ? '1' : '0');
          // Pad to multiple of 6
          while (bits.length % 6) bits += '0';
          let encodedBitmask = '';
          for (let i = 0; i < bits.length; i += 6) {
            encodedBitmask += B64[parseInt(bits.substr(i, 6), 2)];
          }
          shareUrl = `${baseUrl}?b=${encodedBitmask}&c=${encodeURIComponent(encodedName)}`;
        }

        // Đóng Modal
        document.getElementById('linkModal').classList.remove('open');

        // Dùng Web Share API trên điện thoại
        if (navigator.share) {
          navigator.share({
            title: `Khang Ngô Nhà Phố - ${count} căn (Khách: ${cName})`,
            url: shareUrl
          }).catch(() => { });
          return;
        }

        const ta = document.createElement('textarea');
        ta.value = shareUrl;
        ta.style.cssText = 'position:fixed;left:0;top:0;opacity:0;';
        document.body.appendChild(ta);
        ta.focus(); ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        alert(`Đã copy link cá nhân hoá cho khách: ${cName}!\n(Gồm ${count} căn)\n\nDán link này vào Zalo để gửi cho khách nhé.`);
      } catch (e) {
        alert('Có lỗi xảy ra: ' + e.message);
      }
    }

    // Thêm nút tạo link nếu là admin
    if (isAdmin) {
      document.body.insertAdjacentHTML('beforeend', `
        <button class="selall-btn-float" id="selAllBtn" onclick="toggleSelectAll()" title="Chọn / Bỏ chọn tất cả">☐</button>
        <button class="col-btn-float" id="colFloatBtn" onclick="openColSaveModal()" title="Lưu vào bộ sưu tập" style="display: none;">📁</button>
        <button class="share-btn-float" onclick="promptGenerateLink()">
          🔗
          <span class="share-count" id="shareCount">0</span>
        </button>
      `);
    }

    function toggleSelectAll() {
      const visibleCards = [...document.querySelectorAll('#list .card')].filter(c => c.style.display !== 'none');
      const visibleIds = visibleCards.map(c => c.dataset.pid);
      const allSelected = visibleIds.every(id => SELECTED_IDS.has(id));

      visibleCards.forEach(c => {
        const pid = c.dataset.pid;
        const cb = c.querySelector('.card-sel');
        if (allSelected) {
          SELECTED_IDS.delete(pid);
          if (cb) cb.checked = false;
        } else {
          SELECTED_IDS.add(pid);
          if (cb) cb.checked = true;
        }
      });
      updateShareUI();
      const btn = document.getElementById('selAllBtn');
      btn.textContent = allSelected ? '☐' : '☑';
      btn.classList.toggle('all-on', !allSelected);
      saveState();
    }

    // Xử lý hỏi Zalo thông minh
    function askZalo(id, title) {
      const msg = `Chào Khang Ngô Nhà Phố, tôi quan tâm căn nhà mã #${id}: ${title}. Tư vấn giúp tôi nhé!`;

      // Cố gắng copy vào clipboard
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(msg).then(() => {
          alert('Đã copy mã sản phẩm -> bạn nhớ dán vào Zalo để gửi cho Khang nhé!');
          window.location.href = `https://zalo.me/${SDT}`;
        }).catch(() => {
          window.location.href = `https://zalo.me/${SDT}`;
        });
      } else {
        window.location.href = `https://zalo.me/${SDT}`;
      }
    }

    // Xử lý ẩn hiện Header khi cuộn trang (Nâng cấp: Cuộn nhanh/mạnh mới hiện menu)
    let lastScrollY = window.scrollY;
    let lastScrollTime = Date.now();
    const headerEl = document.querySelector('header');
    window.addEventListener('scroll', () => {
      const currentScrollY = window.scrollY;
      const currentScrollTime = Date.now();

      if (currentScrollY < 120) {
        headerEl.classList.remove('hide');
        lastScrollY = currentScrollY;
        lastScrollTime = currentScrollTime;
        return;
      }

      const deltaY = lastScrollY - currentScrollY; // > 0 khi cuộn lên, < 0 khi cuộn xuống
      const deltaTime = currentScrollTime - lastScrollTime;

      if (currentScrollY > lastScrollY && currentScrollY > 80) {
        // Cuộn xuống: ẩn header và tự động đóng bộ lọc
        headerEl.classList.add('hide');
        closeFilter();
      } else if (deltaY > 10) {
        // Cuộn lên: Chỉ hiện menu khi quét/vuốt lên cực kỳ nhanh và dứt khoát
        // Bắt buộc deltaY > 10px để loại bỏ các vi-điều chỉnh (micro-jitter)
        const velocity = deltaTime > 0 ? (deltaY / deltaTime) : 0;

        // Ngưỡng dứt khoát: Vận tốc vuốt cực nhanh (velocity > 1.6 px/ms) HOẶC cuộn kéo lên cực lớn trong 1 lần (> 150px)
        if (velocity > 1.6 || deltaY > 150) {
          headerEl.classList.remove('hide');
        }
      }

      lastScrollY = currentScrollY;
      lastScrollTime = currentScrollTime;
    }, { passive: true });

    // Bấm ra ngoài header → tự động đóng bộ lọc
    document.addEventListener('click', (e) => {
      if (!filterOpen) return;
      if (!e.target.closest('header')) closeFilter();
    });

    // ============================================================
    //  🔑 GOOGLE OAUTH2 & SECURE FACADE IMAGE FETCHING (US-024)
    // ============================================================
    let gTokenClient = null;

    function saveGoogleClientId() {
      const input = document.getElementById('gClientIdInput');
      if (!input) return;
      const val = input.value.trim();
      if (!val) {
        alert("Vui lòng nhập Client ID hợp lệ!");
        return;
      }
      localStorage.setItem('gClientId', val);
      alert("Đã lưu Client ID thành công! Đang khởi tạo bộ xác thực Google...");
      initGoogleAuth();
    }

    function initGoogleAuth() {
      let clientId = localStorage.getItem('gClientId');
      if (!clientId) {
        clientId = '1088195961071-25r6rpvsfmoudqokb75u0m2ugu8na0v0.apps.googleusercontent.com';
        localStorage.setItem('gClientId', clientId);
      }
      const gClientIdInput = document.getElementById('gClientIdInput');
      if (gClientIdInput) gClientIdInput.value = clientId;

      try {
        gTokenClient = google.accounts.oauth2.initTokenClient({
          client_id: clientId,
          scope: 'https://www.googleapis.com/auth/spreadsheets',
          callback: (tokenResponse) => {
            if (tokenResponse.error !== undefined) {
              console.error("OAuth2 error:", tokenResponse.error);
              showGoogleLoginButtonState(false);
              return;
            }
            const token = tokenResponse.access_token;
            const expiry = Date.now() + (tokenResponse.expires_in - 60) * 1000;
            localStorage.setItem('g_access_token', token);
            localStorage.setItem('g_token_expiry', expiry);
            showGoogleLoginButtonState(true);
            loadData();
          }
        });
        console.log("Google Auth GSI Client initialized successfully.");
      } catch (e) {
        console.error("Error initializing Google Auth GSI:", e);
      }
    }

    function handleGoogleLoginClick() {
      const clientId = localStorage.getItem('gClientId');
      if (!clientId) {
        alert("Vui lòng nhập Google OAuth Client ID của bạn ở mục 'Cấu hình Google Admin' trong Bộ lọc trước!");
        if (!filterOpen) toggleFilter();
        setTimeout(() => {
          const input = document.getElementById('gClientIdInput');
          if (input) input.focus();
        }, 300);
        return;
      }

      if (!gTokenClient) {
        initGoogleAuth();
      }

      if (gTokenClient) {
        try {
          gTokenClient.requestAccessToken();
        } catch (e) {
          console.error("Error requesting access token:", e);
          alert("Lỗi yêu cầu token. Vui lòng kiểm tra lại Client ID hoặc kết nối mạng.");
        }
      } else {
        alert("Không thể khởi tạo Client xác thực. Vui lòng tải lại trang.");
      }
    }

    function showGoogleLoginButtonState(isLoggedIn) {
      const gLoginBtn = document.getElementById('gLoginBtn');
      const gLoginText = document.getElementById('gLoginText');
      if (!gLoginBtn || !gLoginText) return;
      if (isLoggedIn) {
        gLoginBtn.style.background = '#27ae60';
        gLoginBtn.style.color = '#fff';
        gLoginBtn.style.borderColor = '#27ae60';
        gLoginText.innerText = "Đã liên kết Gmail";
      } else {
        gLoginBtn.style.background = '#fff';
        gLoginBtn.style.color = '#1c1c1e';
        gLoginBtn.style.borderColor = '#fff';
        const clientId = localStorage.getItem('gClientId');
        gLoginText.innerText = clientId ? "Đăng nhập" : "Cấu hình API";
      }
    }

    function autoLoginOrSilentRefresh() {
      const token = localStorage.getItem('g_access_token');
      const expiry = localStorage.getItem('g_token_expiry');
      const now = Date.now();

      if (token && expiry && parseInt(expiry, 10) > now) {
        console.log("Found valid access token in LocalStorage. Expiry in:", Math.round((parseInt(expiry, 10) - now) / 1000), "s");
        showGoogleLoginButtonState(true);
        loadData();
      } else {
        const clientId = localStorage.getItem('gClientId');
        if (clientId) {
          console.log("Access token expired or missing. Attempting Silent Auto-Login...");
          const checkAndRefresh = () => {
            if (gTokenClient) {
              try {
                gTokenClient.requestAccessToken({ prompt: 'none' });
              } catch (e) {
                console.warn("Silent token request failed:", e);
                showGoogleLoginButtonState(false);
              }
            } else {
              setTimeout(checkAndRefresh, 300);
            }
          };
          checkAndRefresh();
        } else {
          showGoogleLoginButtonState(false);
        }
      }
    }

    function fetchFacadeImages(token) {
      if (!token) return;
      const url = `/api/get-facade-images`;

      fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
        .then(res => {
          if (!res.ok) {
            if (res.status === 401 || res.status === 403) {
              console.warn("OAuth token invalid or unauthorized. Cleared from storage.");
              localStorage.removeItem('g_access_token');
              localStorage.removeItem('g_token_expiry');
              showGoogleLoginButtonState(false);
            }
            throw new Error(`Google Sheets API returned status ${res.status}`);
          }
          return res.json();
        })
        .then(data => {
          const values = data.values || [];
          const facadeMap = {};
          values.forEach(row => {
            if (row.length >= 1) {
              const id = row[0];
              const img = row[row.length - 1] || '';
              if (id && img) {
                facadeMap[id] = img;
              }
            }
          });

          // Merge facade images
          DATA.forEach(p => {
            if (facadeMap[p.id]) {
              p.img_mat_tien = facadeMap[p.id];
            }
          });

          console.log("Securely fetched and merged", Object.keys(facadeMap).length, "facade images.");
          render();
        })
        .catch(err => {
          console.error("Error fetching facade images from private sheet:", err);
        });
    }

    async function requestPullListing() {
      const soNha = document.getElementById('pullSoNha').value.trim();
      const duong = document.getElementById('pullDuong').value.trim();
      
      if (!soNha || !duong) {
        alert("Vui lòng nhập đầy đủ Số nhà và Tên đường!");
        return;
      }
      
      const token = localStorage.getItem('g_access_token');
      const expiry = localStorage.getItem('g_token_expiry');
      const now = Date.now();
      
      if (!token || !expiry || parseInt(expiry, 10) <= now) {
        alert("Phiên đăng nhập Google đã hết hạn hoặc chưa liên kết Gmail. Vui lòng bấm 'Đăng nhập / Liên kết Gmail' trước!");
        return;
      }
      
      const btn = document.getElementById('btnPullListing');
      const spinner = document.getElementById('pullSpinner');
      
      btn.disabled = true;
      spinner.style.display = 'inline-block';
      
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
        
        const targetSoNha = norm(soNha);
        const targetDuong = norm(duong);
        
        // Tìm dòng khớp Số nhà + Đường
        const matchedRow = rows.find(r => norm(r[6]) === targetSoNha && norm(r[5]) === targetDuong);
        
        if (!matchedRow) {
          alert(`❌ Căn nhà này chưa được cào về kho Pool. Vui lòng báo Trang chạy Crawler!`);
          btn.disabled = false;
          spinner.style.display = 'none';
          return;
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
        
        const systemId = matchedRow[71]; // Cột 71 (System ID)
        if (!systemId) {
          throw new Error("Dữ liệu căn nhà trong Pool thiếu System ID. Vui lòng cào lại hoặc biên tập lại!");
        }
        
        const existIdx = sourceRows.findIndex(sr => sr[37] === systemId);
        const targetRowNumber = existIdx !== -1 ? (existIdx + 2) : (sourceRows.length + 2);
        
        // Step 3: Map dữ liệu 78 cột từ Pool -> 41 cột sang Source
        const finalImages = [];
        const anhDuocChon = (matchedRow[61] || "").toString().replace(/\s/g, '');
        const anhHemDuocChon = (matchedRow[62] || "").toString().replace(/\s/g, '');
        
        if (anhDuocChon === "") {
          alert("⚠️ Căn nhà này chưa được dán nhãn ảnh nội thất an toàn ở Curator App! Vui lòng nhờ Trang biên tập ảnh trước.");
          btn.disabled = false;
          spinner.style.display = 'none';
          return;
        }
        
        const noithatIndices = anhDuocChon.split(',');
        
        // 1. Cover
        const firstNoithatIdx = parseInt(noithatIndices[0]);
        if (!isNaN(firstNoithatIdx) && firstNoithatIdx >= 1 && firstNoithatIdx <= 15) {
          const coverImgUrl = matchedRow[39 + firstNoithatIdx];
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
              const hemUrl = matchedRow[29 + hemIdx];
              if (hemUrl) {
                finalImages.push(hemUrl);
                addedHem++;
              }
            }
          }
        } else {
          const availableHem = [];
          for (let i = 1; i <= 10; i++) {
            const hemUrl = matchedRow[29 + i];
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
          if (!isNaN(imgIdx) && imgIdx >= 1 && imgIdx <= 15) {
            const imgUrl = matchedRow[39 + imgIdx];
            if (imgUrl) finalImages.push(imgUrl);
          }
        }
        
        while (finalImages.length < 10) finalImages.push("");
        
        // Xử lý Cú pháp (Lấy từ Nội dung chính thô)
        const noiDungChinh = matchedRow[9] || "";
        let cuPhap = noiDungChinh;
        const matchCuPhap = noiDungChinh.match(/^(.*?Quận\s+[A-Za-zÀ-ỹ0-9\s]+?)\s+[\d\.]+(?:-[\d\.]+)?\s*tỷ/i);
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
        
        // Xây dựng publicRowData 41 cột cho Sheet Source
        const publicRowData = [
          `=IMAGE(AM${targetRowNumber})`, // 0: Hinh_mat_tien (Cột A)
          cuPhap,                        // 1: Cu_phap (Cột B)
          "",                            // 2: Note (Cột C)
          matchedRow[54],                // 3: id (Cột D)
          matchedRow[55],                // 4: tieu_de (Cột E)
          matchedRow[13],                // 5: dien_tich (Cột F)
          matchedRow[15],                // 6: so_tang (Cột G)
          matchedRow[16],                // 7: mat_tien (Cột H)
          formatGia(matchedRow[57]),     // 8: gia (Cột I)
          formatQuan(matchedRow[3]),     // 9: quan (Cột J)
          matchedRow[4],                 // 10: phuong (Cột K)
          loaiHinh,                      // 11: loai_hinh (Cột L)
          matchedRow[17],                // 12: huong_nha (Cột M)
          matchedRow[58],                // 13: duong_truoc_nha (Cột N)
          matchedRow[59],                // 14: do_rong_hem (Cột O)
          matchedRow[60],                // 15: tinh_trang_nha (Cột P)
          matchedRow[66],                // 16: danh_gia (Cột Q)
          matchedRow[67],                // 17: ngu_tang_tret (Cột R)
          matchedRow[68],                // 18: chdv (Cột S)
          matchedRow[56],                // 19: mo_ta (Cột T)
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
          matchedRow[65],                // 31: phuong_cu (Cột AF)
          matchedRow[63],                // 32: so_pn (Cột AG)
          matchedRow[64],                // 33: so_wc (Cột AH)
          matchedRow[5],                 // 34: ten_duong (Cột AI)
          "",                            // 35: gio_dang (Cột AJ)
          "",                            // 36: trang_thai (Cột AK)
          systemId,                      // 37: System ID (Cột AL)
          matchedRow[29],                // 38: Hình Mặt Tiền (Cột AM)
          "",                            // 39: Tiêu đề BDS (Cột AN)
          false                          // 40: Đăng BDS (Cột AO)
        ];
        
        // Step 4: Ghi đè/Thêm mới vào Sheet Source
        const writeUrl = `https://sheets.googleapis.com/v4/spreadsheets/${SOURCE_SHEET_ID}/values/Source!A${targetRowNumber}:AO${targetRowNumber}?valueInputOption=USER_ENTERED`;
        const writeRes = await fetch(writeUrl, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ values: [publicRowData] })
        });
        
        if (!writeRes.ok) {
          throw new Error(`Không thể ghi dữ liệu sang Sheet Source (Mã: ${writeRes.status}).`);
        }
        
        // Cập nhật lại trường Last Sync của dòng đó bên Sheet Pool
        try {
          const poolRowNumber = rows.indexOf(matchedRow) + 2;
          const syncDateStr = new Date().toLocaleString("vi-VN", { timeZone: "Asia/Ho_Chi_Minh" });
          await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!BZ${poolRowNumber}:BZ${poolRowNumber}?valueInputOption=USER_ENTERED`, {
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
        
        alert(`🎉 Đã đồng bộ lên sóng thành công căn nhà #${matchedRow[54]} (${matchedRow[55]})!`);
        
        // Clear form
        document.getElementById('pullSoNha').value = '';
        document.getElementById('pullDuong').value = '';
        
        // Tải lại dữ liệu web
        loadData();
        
      } catch (err) {
        alert(`❌ Lỗi đồng bộ: ${err.message}`);
        console.error(err);
      } finally {
        btn.disabled = false;
        spinner.style.display = 'none';
      }
    }

    // ============================================================
    // [COLLECTIONS MANAGEMENT HELPERS]
    // ============================================================
    function updateShareUI() {
      const shareCountEl = document.getElementById('shareCount');
      if (shareCountEl) shareCountEl.textContent = SELECTED_IDS.size;
      
      const colFloatBtn = document.getElementById('colFloatBtn');
      if (colFloatBtn) {
        colFloatBtn.style.display = SELECTED_IDS.size > 0 ? 'flex' : 'none';
      }
    }

    function openColViewModal() {
      const viewList = document.getElementById('colViewList');
      if (!viewList) return;
      viewList.innerHTML = '';
      
      // 1. Thêm bộ sưu tập Mặc định: Yêu thích (Thích)
      const favCount = favs.size;
      const favItem = document.createElement('div');
      favItem.style.cssText = 'display:flex; align-items:center; justify-content:space-between; padding:12px 16px; background:rgba(255,255,255,0.05); border-radius:10px; cursor:pointer; transition:background 0.2s;';
      favItem.innerHTML = `
        <div style="display:flex; align-items:center; gap:8px;" onclick="viewCollection('favorites')">
          <span style="font-size:16px;">❤️</span>
          <span style="font-weight:600; font-size:14px;">Căn nhà đã thích</span>
          <span style="font-size:12px; color:var(--sub);">(${favCount} căn)</span>
        </div>
      `;
      favItem.onclick = () => {
        viewCollection('favorites');
        document.getElementById('colViewModal').classList.remove('open');
      };
      viewList.appendChild(favItem);
      
      // 2. Thêm các bộ sưu tập tự tạo
      Object.keys(collections).forEach(name => {
        const count = collections[name].length;
        const item = document.createElement('div');
        item.style.cssText = 'display:flex; align-items:center; justify-content:space-between; padding:12px 16px; background:rgba(255,255,255,0.05); border-radius:10px; cursor:pointer; transition:background 0.2s; margin-top:8px;';
        item.innerHTML = `
          <div style="display:flex; align-items:center; gap:8px; flex:1;" onclick="viewCollection('${name.replace(/'/g, "\\'")}')">
            <span style="font-size:16px;">📁</span>
            <span style="font-weight:600; font-size:14px; word-break:break-all;">${name}</span>
            <span style="font-size:12px; color:var(--sub);">(${count} căn)</span>
          </div>
          <button onclick="deleteCollection('${name.replace(/'/g, "\\'")}', event)" style="background:none; border:none; color:var(--sub); font-size:14px; cursor:pointer; padding:4px 8px; display:flex; align-items:center; justify-content:center; transition:color 0.15s;" title="Xóa bộ sưu tập">🗑️</button>
        `;
        item.querySelector('div').onclick = () => {
          viewCollection(name);
          document.getElementById('colViewModal').classList.remove('open');
        };
        viewList.appendChild(item);
      });
      
      document.getElementById('colViewModal').classList.add('open');
    }

    function openColSaveModal() {
      if (SELECTED_IDS.size === 0) {
        alert('Vui lòng chọn ít nhất 1 căn nhà!');
        return;
      }
      
      document.getElementById('colSaveModalCount').textContent = SELECTED_IDS.size;
      document.getElementById('newColName').value = '';
      
      const saveList = document.getElementById('colSaveList');
      if (!saveList) return;
      saveList.innerHTML = '';
      
      const colNames = Object.keys(collections);
      if (colNames.length === 0) {
        saveList.innerHTML = '<div style="text-align:center; padding:12px; font-size:13px; color:var(--sub);">Chưa có bộ sưu tập nào. Hãy tạo bộ sưu tập đầu tiên ở trên nhé!</div>';
      } else {
        colNames.forEach(name => {
          const count = collections[name].length;
          const btn = document.createElement('button');
          btn.style.cssText = 'width:100%; text-align:left; padding:12px 16px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:8px; color:#fff; font-weight:600; font-size:13px; cursor:pointer; font-family:inherit; transition:background 0.2s; margin-bottom:8px;';
          btn.innerHTML = `📁 ${name} <span style="font-size:11px; color:var(--sub); font-weight:normal;">(${count} căn)</span>`;
          btn.onclick = () => {
            saveToExistingCollection(name);
            document.getElementById('colSaveModal').classList.remove('open');
          };
          saveList.appendChild(btn);
        });
      }
      
      document.getElementById('colSaveModal').classList.add('open');
    }

    function createNewCollection() {
      const name = document.getElementById('newColName').value.trim();
      if (!name) {
        alert('Vui lòng nhập tên bộ sưu tập!');
        return;
      }
      
      if (collections[name]) {
        if (!confirm(`Bộ sưu tập "${name}" đã tồn tại. Bạn có muốn ghi đè/nạp thêm vào bộ sưu tập này không?`)) {
          return;
        }
      }
      
      const idsToSave = Array.from(SELECTED_IDS);
      collections[name] = idsToSave;
      localStorage.setItem('adminCollections', JSON.stringify(collections));
      
      // Xóa check sau khi lưu
      SELECTED_IDS.clear();
      updateShareUI();
      
      renderCollectionsManager();
      
      alert(`Đã tạo bộ sưu tập "${name}" với ${idsToSave.length} căn thành công!`);
      document.getElementById('colSaveModal').classList.remove('open');
      
      if (activeCollectionName === name) {
        viewCollection(name);
      } else {
        render();
      }
    }

    function saveToExistingCollection(name) {
      if (!collections[name]) return;
      
      const currentIds = collections[name];
      const newIds = Array.from(SELECTED_IDS);
      
      const merged = Array.from(new Set([...currentIds, ...newIds]));
      const addedCount = merged.length - currentIds.length;
      
      collections[name] = merged;
      localStorage.setItem('adminCollections', JSON.stringify(collections));
      
      SELECTED_IDS.clear();
      updateShareUI();
      
      renderCollectionsManager();
      
      alert(`Đã lưu thêm ${addedCount} căn mới vào bộ sưu tập "${name}" thành công! (Tổng số: ${merged.length} căn)`);
      
      if (activeCollectionName === name) {
        viewCollection(name);
      } else {
        render();
      }
    }

    function viewCollection(name) {
      activeCollectionName = name;
      
      SELECTED_IDS.clear();
      updateShareUI();
      
      const bar = document.getElementById('activeColBar');
      const text = document.getElementById('activeColNameText');
      if (bar && text) {
        let count = 0;
        let displayName = '';
        if (name === 'favorites') {
          count = favs.size;
          displayName = '❤️ Căn nhà đã thích';
        } else {
          count = collections[name] ? collections[name].length : 0;
          displayName = `📂 ${name}`;
        }
        text.innerHTML = `<b>${displayName}</b> (${count} căn)`;
        bar.style.display = 'flex';
      }
      
      render();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function exitCollectionView() {
      activeCollectionName = null;
      
      const bar = document.getElementById('activeColBar');
      if (bar) bar.style.display = 'none';
      
      render();
    }

    function deleteCollection(name, event) {
      if (event) event.stopPropagation();
      if (!confirm(`Bạn có chắc chắn muốn xóa bộ sưu tập "${name}" không?`)) {
        return;
      }
      
      delete collections[name];
      localStorage.setItem('adminCollections', JSON.stringify(collections));
      
      renderCollectionsManager();
      
      if (activeCollectionName === name) {
        exitCollectionView();
      } else {
        openColViewModal();
      }
    }

    function removeFromCol(id, colName, event) {
      if (event) event.stopPropagation();
      
      if (colName === 'favorites') {
        favs.delete(String(id));
        localStorage.setItem('favs', JSON.stringify(Array.from(favs)));
        updateFavBtnUI();
      } else if (collections[colName]) {
        collections[colName] = collections[colName].filter(x => String(x) !== String(id));
        localStorage.setItem('adminCollections', JSON.stringify(collections));
        renderCollectionsManager();
      }
      
      viewCollection(colName);
    }

    function renderCollectionsManager() {
      const manager = document.getElementById('collectionsManager');
      if (!manager) return;
      manager.innerHTML = '';
      
      const colNames = Object.keys(collections);
      if (colNames.length === 0) {
        manager.innerHTML = '<span style="font-size:12px; color:rgba(255,255,255,0.4); padding:6px 0;">Chưa có bộ sưu tập. Chọn căn & bấm 📁 để tạo.</span>';
        return;
      }
      
      colNames.forEach(name => {
        const count = collections[name].length;
        const chip = document.createElement('div');
        chip.style.cssText = 'display:inline-flex; align-items:center; gap:6px; background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:4px 10px; font-size:12px; font-weight:600; color:#fff; cursor:pointer; transition:background 0.2s;';
        chip.innerHTML = `
          <span onclick="viewCollection('${name.replace(/'/g, "\\'")}')">📁 ${name} (${count})</span>
          <span onclick="deleteCollection('${name.replace(/'/g, "\\'")}', event)" style="color:rgba(255,255,255,0.5); font-size:11px; padding-left:4px; border-left:1px solid rgba(255,255,255,0.2);" title="Xóa">✕</span>
        `;
        manager.appendChild(chip);
      });
    }

    // ============================================================
    //  ⚡ ADMIN CURATION DASHBOARD EXTRA HELPERS (US-039)
    // ============================================================
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

    window.setupScrollCarousel = function(containerId, imageUrls, isLegalImg = false) {
      const container = document.getElementById(containerId);
      if (!container) return;

      const track = container.querySelector('.admin-scroll-carousel');
      const dotsContainer = container.querySelector('.admin-carousel-dots');
      if (!track || !dotsContainer) return;

      track.innerHTML = '';
      dotsContainer.innerHTML = '';

      if (imageUrls.length === 0) {
        track.innerHTML = `<div style="width:100%; height:100%; display:flex; align-items:center; justify-content:center; color:var(--sub); font-size:12.5px; font-weight:600; background:#f8f9fa;">Chưa có hình ảnh</div>`;
        return;
      }

      imageUrls.forEach((url, idx) => {
        const cleanUrl = fixImgUrl(url, 'w800');
        const item = document.createElement('div');
        item.className = 'admin-carousel-item';
        item.setAttribute('onclick', `openZoomOverlay('${cleanUrl.replace(/'/g, "\\'")}')`);
        item.style.cursor = 'zoom-in';
        item.innerHTML = `<img src="${cleanUrl}" alt="Hình ${idx + 1}" loading="lazy">`;
        track.appendChild(item);

        const dot = document.createElement('div');
        dot.className = 'admin-dot' + (idx === 0 ? ' on' : '');
        dotsContainer.appendChild(dot);
      });

      track.onscroll = () => {
        const width = track.clientWidth;
        const scrollLeft = track.scrollLeft;
        const activeIdx = Math.round(scrollLeft / (width * 0.85));
        const dots = dotsContainer.querySelectorAll('.admin-dot');
        dots.forEach((dot, dIdx) => {
          dot.classList.toggle('on', dIdx === activeIdx);
        });
      };
    };

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

    window.showToast = function(msg, type = 'success') {
      let container = document.getElementById('toastContainer');
      if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = `
          position: fixed;
          top: 20px;
          left: 50%;
          transform: translateX(-50%);
          z-index: 200000;
          display: flex;
          flex-direction: column;
          gap: 10px;
          pointer-events: none;
          width: 90%;
          max-width: 320px;
        `;
        document.body.appendChild(container);
      }

      const toast = document.createElement('div');
      toast.style.cssText = `
        background: ${type === 'success' ? '#27ae60' : '#e74c3c'};
        color: white;
        padding: 12px 20px;
        border-radius: 12px;
        font-size: 13.5px;
        font-weight: 700;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        gap: 8px;
        opacity: 0;
        transform: translateY(-20px);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
      `;
      toast.innerHTML = `
        <span>${type === 'success' ? '✅' : '❌'}</span>
        <span>${msg}</span>
      `;
      container.appendChild(toast);

      toast.offsetHeight;

      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';

      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        setTimeout(() => {
          toast.remove();
        }, 300);
      }, 3000);
    };

    window.saveSourceChanges = async function(id) {
      const p = DATA.find(x => String(x.id) === String(id));
      if (!p) {
        showToast("Không tìm thấy thông tin căn nhà!", "error");
        return;
      }

      const token = localStorage.getItem('g_access_token');
      const expiry = localStorage.getItem('g_token_expiry');
      const now = Date.now();

      if (!token || !expiry || parseInt(expiry, 10) <= now) {
        showToast("Phiên đăng nhập Google đã hết hạn. Vui lòng liên kết lại Gmail!", "error");
        return;
      }

      const saveBtn = document.getElementById('saveBtn');
      if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '⌛ Đang lưu...';
      }

      try {
        const note = document.getElementById('editNote').value.trim();
        const tieuDeBds = document.getElementById('editTieuDeBds').value.trim();
        const huong = document.getElementById('editHuong').value;
        const duong = document.getElementById('editDuong').value;
        const danhGia = document.getElementById('editDanhGia').value;
        const rongHem = document.getElementById('editRongHem').value.trim();
        const soPn = document.getElementById('editSoPn').value.trim();
        const soWc = document.getElementById('editSoWc').value.trim();
        const nguTret = document.getElementById('editNguTret').checked ? 'Có' : 'Không';
        const chdv = document.getElementById('editChdv').checked ? 'Có' : 'Không';

        p.original_row_data[2] = note;
        p.original_row_data[12] = huong;
        p.original_row_data[13] = duong;
        p.original_row_data[14] = rongHem || '-';
        p.original_row_data[16] = danhGia;
        p.original_row_data[17] = nguTret;
        p.original_row_data[18] = chdv;
        p.original_row_data[30] = new Date().toISOString();
        p.original_row_data[32] = soPn || '-';
        p.original_row_data[33] = soWc || '-';
        p.original_row_data[39] = tieuDeBds;

        p.note = note;
        p.huong = huong;
        p.duong_truoc_nha = duong;
        p.rong_hem = rongHem || '-';
        p.danh_gia = danhGia;
        p.ngu_tang_tret = nguTret;
        p.chdv = chdv;
        p.so_pn = soPn || '-';

        const SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE';
        const writeUrl = `https://sheets.googleapis.com/v4/spreadsheets/${SOURCE_SHEET_ID}/values/Source!A${p.source_row_index}:AO${p.source_row_index}?valueInputOption=USER_ENTERED`;

        const writeRes = await fetch(writeUrl, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ values: [p.original_row_data] })
        });

        if (!writeRes.ok) {
          throw new Error(`Google Sheets API returned status ${writeRes.status}`);
        }

        showToast("Đã lưu thay đổi lên Google Sheets thành công!");
        closeS();
        render();
      } catch (err) {
        console.error("Lỗi lưu dữ liệu:", err);
        showToast(`Lỗi lưu thay đổi: ${err.message}`, "error");
      } finally {
        if (saveBtn) {
          saveBtn.disabled = false;
          saveBtn.innerHTML = '💾 LƯU THAY ĐỔI';
        }
      }
    };

    // Khởi động
    updateFavBtnUI();
    if (isAdmin) {
      updateShareUI();
      renderCollectionsManager();
      setTimeout(initGoogleAuth, 800);
    }
    loadData();
  