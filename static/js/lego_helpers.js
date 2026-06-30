/**
 * Lego Frontend - Utility Helpers Module (lego_helpers.js)
 * Contains helper functions, data cleaners, image download utilities, and sorting/filtering states.
 */

// Global Configuration & State variables
window.SHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0';
window.SDT = '0979841573';
window.activeMode = window.isAdmin ? 'pool' : 'source'; // Mặc định Pool cho Admin khi vào trang (US-039.7)
window.MAPPED_POOL_DATA = [];
window.CURRENT_EDITING_LISTING = null;
window.displayCustomerName = "";
window.trackingCustomerName = "";
window.sharedIds = null;
window.currentSortType = 'newest'; // 'newest' or 'price'
window.currentSortDir = 'desc'; // 'desc' = high/newest first, 'asc' = low/oldest first
window.hasErrorState = false;

// Fallback formatPhone helper
window.formatPhone = function(phone) {
  if (!phone) return '';
  let s = String(phone).trim().replace(/[\s\.-]/g, '');
  if (/^[1-9]\d{8}$/.test(s)) {
    return '0' + s;
  }
  return s;
};

// Tracking helper
window.trackAction = function(action, details = "") {
  if (window.isAdmin || !window.trackingCustomerName) return; // Không track Admin
  const TRACKING_URL = 'https://script.google.com/macros/s/AKfycbxsFXAQiX11LaSAslvefiv7ncWcHVgeyyd8Gi2pgRAneHhyZpE0AZKjP4rRrHD15oNN1g/exec';
  try {
    fetch(TRACKING_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customer: window.trackingCustomerName,
        action: action,
        details: details
      })
    }).catch(e => { });
  } catch (error) { }
};

// Custom Base64 chars for Bitmask
const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';

// Decode bitmask helper
window.decodeBitmask = function(encoded, allIds) {
  let bits = '';
  for (let i = 0; i < encoded.length; i++) {
    const ch = encoded[i];
    const val = B64.indexOf(ch);
    if (val === -1) continue;
    bits += val.toString(2).padStart(6, '0');
  }
  const selected = [];
  for (let i = 0; i < allIds.length; i++) {
    if (bits[i] === '1') selected.push(allIds[i]);
  }
  return selected;
};

// AI Curation Auto-fill logic
window.autoFillCurationDetails = async function() {
  const editTieuDe = document.getElementById('editTieuDeBds');
  const editMoTa = document.getElementById('editMoTaBds');
  const btn = document.getElementById('btnAutoFillCuration');
  
  if (!window.CURRENT_EDITING_LISTING) return;
  const p = window.CURRENT_EDITING_LISTING;
  
  const confirmProceed = confirm("Hành động này sẽ xóa thông tin Tiêu đề public và Mô tả public cũ để thay bằng thông tin mới tự động điền bằng AI. Bạn có chắc chắn muốn tiếp tục không?");
  if (!confirmProceed) return;
  
  let originalBtnText = "";
  if (btn) {
    originalBtnText = btn.innerHTML;
    btn.innerHTML = "⏳ Đang chạy AI...";
    btn.disabled = true;
    btn.style.opacity = "0.6";
  }
  
  try {
    const payload = {
      soNha: p.raw_so_nha || '',
      duong: p.raw_ten_duong || '',
      phuong: p.phuong || '',
      quan: p.ql || '',
      noiDungChinh: p.raw_noi_dung_chinh || '',
      moTaChiTiet: p.raw_mo_ta_chi_tiet || '',
      dtThucTe: p.raw_dt_thuc_te || p.dt || '',
      dtTrenSo: p.raw_dt_tren_so || p.dt || '',
      matTien: p.raw_mat_tien || p.mat || '',
      soTang: p.raw_so_tang || p.tang || '',
      soPhongNgu: p.so_pn !== '-' ? p.so_pn : '',
      soToilet: (p.original_row_data && p.original_row_data[33] !== '-') ? p.original_row_data[33] : (p.raw_so_wc || ''),
      giaChao: p.raw_gia_chao || p.gia || '',
      duongTruocNha: p.rong_hem || p.raw_duong_truoc_nha || '',
      phanLoaiHem: p.duong_truoc_nha || (p.json_ui_parsed && p.json_ui_parsed.Criteria_Duong_truoc_nha) || '',
      phanLoai: p.danh_gia || ''
    };
    
    const gToken = localStorage.getItem('g_access_token') || '';
    const headers = { 'Content-Type': 'application/json' };
    if (gToken) {
      headers['Authorization'] = `Bearer ${gToken}`;
    }
    
    const res = await fetch('/api/ai/generate', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(payload)
    });
    
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.message || `Lỗi server HTTP ${res.status}`);
    }
    
    const data = await res.json();
    if (data.status === 'success') {
      if (editTieuDe) editTieuDe.value = data.tieu_de_public || '';
      if (editMoTa) editMoTa.value = data.mo_ta_public || '';
      
      p.phuong_cu = data.phuong_cu || '';
      if (p.original_row_data) {
        p.original_row_data[66] = data.phuong_cu || '';
      }
      if (p.pool_row_data) {
        p.pool_row_data[66] = data.phuong_cu || '';
      }
      
      if (editTieuDe) editTieuDe.dispatchEvent(new Event('input'));
      if (editMoTa) editMoTa.dispatchEvent(new Event('input'));
      
      showToast("🤖 AI biên tập Tiêu đề và Mô tả thành công!", "success");
    } else {
      throw new Error(data.message || "Lỗi không xác định từ AI.");
    }
  } catch (err) {
    console.error("Lỗi Tự động điền AI:", err);
    showToast("⚠️ " + err.message + " -> Dùng mẫu mặc định.", "warning");
    
    if (editTieuDe) editTieuDe.value = p.raw_tieu_de_public || generateAutoTitle(p);
    if (editMoTa) editMoTa.value = p.m || p.raw_mo_ta_public || generateAutoDescription(p);
    
    if (editTieuDe) editTieuDe.dispatchEvent(new Event('input'));
    if (editMoTa) editMoTa.dispatchEvent(new Event('input'));
  } finally {
    if (btn) {
      btn.innerHTML = originalBtnText;
      btn.disabled = false;
      btn.style.opacity = "1";
    }
  }
};

// Title cutter
window.cutTitleToDistrict = function(title) {
  if (!title) return '';
  let s = String(title).trim();
  const regex = /^(.*?\b(Quận\s+[a-z0-9àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]+|Q\.\s*[a-z0-9àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ]+|Q\d+)\b)/i;
  const match = s.match(regex);
  if (match) {
    return match[1].trim();
  }
  return s;
};

// Raw description formatter
window.formatRawDescription = function(text) {
  if (!text) return '';
  let s = String(text).trim();
  s = s.replace(/(\.|\!|\?)\s+(?=[A-ZÂĂĐÊÔƠƯàáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬĐÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ0-9\-+*•👉✅⚡🔥])/g, '$1\n');
  s = s.replace(/\s*([\-+*•👉✅⚡🔥])\s*/g, '\n$1 ');
  
  const lines = s.split('\n')
    .map(line => line.trim())
    .filter(line => /[a-zA-Z0-9àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬĐÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ]/.test(line));
    
  return lines.join('\n');
};

// Commission extractor
window.extractCommission = function(p) {
  const text = (p.raw_noi_dung_chinh || '').trim();
  if (!text) return '-';
  const matchH = text.match(/\b(H\d(?:GB|GB-N|N|)?)\b/i);
  if (matchH) return matchH[1].toUpperCase();
  const matchPct = text.match(/\b(\d+(?:\.\d+)?%)\b/);
  if (matchPct) return matchPct[1];
  if (p.raw_loai_hd && p.raw_loai_hd !== '-') return p.raw_loai_hd;
  return '-';
};

// Length calculator
window.getDaiNha = function(p) {
  if (p.cu_phap) {
    const parts = String(p.cu_phap).trim().split(/\s+/);
    const idxTy = parts.findIndex(part => part.toLowerCase().includes('tỷ'));
    if (idxTy >= 3) {
      const possibleDai = parseFloat(parts[idxTy - 2]);
      const possibleNgang = parseFloat(parts[idxTy - 3]);
      if (possibleDai > 0 && possibleNgang > 0 && Math.abs(possibleDai * possibleNgang - parseFloat(p.dt)) / parseFloat(p.dt) < 0.25) {
        return possibleDai;
      }
    }
  }
  
  const textToSearch = ((p.t || '') + ' ' + (p.m || '')).toLowerCase();
  const matchX = textToSearch.match(/(?:[^\d]|^)(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)(?:[^\d]|$)/);
  if (matchX) {
    const possibleNgang = parseFloat(matchX[1]);
    const possibleDai = parseFloat(matchX[2]);
    if (possibleDai > 0 && possibleNgang > 0 && Math.abs(possibleDai * possibleNgang - parseFloat(p.dt)) / parseFloat(p.dt) < 0.25) {
      return possibleDai;
    }
  }
  
  const dtVal = parseFloat(p.dt) || 0;
  const ngangVal = parseFloat(p.mat) || 0;
  if (dtVal > 0 && ngangVal > 0) {
    return Math.round((dtVal / ngangVal) * 10) / 10;
  }
  return 0;
};

// Helper to parse price float
function parseGia(val) {
  if (!val) return 0;
  let s = String(val).trim().toLowerCase();
  s = s.replace(/,/g, '.');
  let num = parseFloat(s);
  if (isNaN(num)) return 0;
  if (s.includes('triệu') || s.includes('tr') || num > 500) {
    return num / 1000;
  }
  return num;
}

// Clean consecutive newlines
function cleanConsecutiveNewlines(text) {
  if (!text) return '';
  return String(text).replace(/\n{3,}/g, '\n\n').trim();
}

// Pool rows mapper
window.getMappedPoolData = function() {
  if (window.MAPPED_POOL_DATA.length === POOL_ROWS.length && window.MAPPED_POOL_DATA.length > 0) {
    return window.MAPPED_POOL_DATA;
  }
  if (!POOL_ROWS || !POOL_ROWS.length) return [];
  
  window.MAPPED_POOL_DATA = POOL_ROWS.map((row, index) => {
    const systemId = row[72] || row[71] || '';
    const dt = parseFloat(row[14] || row[13]) || 0;
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
      temp_id: index + 1,
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
      m: cleanConsecutiveNewlines(row[57] || ''),
      imgs: poolImgs,
      system_id: systemId,
      so_pn: row[64] || '-',
      img_mat_tien: row[29] || '',

      raw_ten_dau_chu: row[75] || '',
      raw_dt_dau_chu: row[74] || '',
      raw_link_fb: row[76] || '',
      raw_noi_dung_chinh: String(row[9] || '').replace(/\r\n|\r|\n/g, ' '),
      raw_mo_ta_chi_tiet: cleanConsecutiveNewlines(row[10] || ''),
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
    p.dai_nha = window.getDaiNha(p);
    
    // Parse JSON_UI cho Kho Pool của Admin
    let jsonUiVal = row[93] || '';
    if (!jsonUiVal || !String(jsonUiVal).trim().startsWith('{')) {
      for (let i = row.length - 1; i >= 0; i--) {
        const val = row[i];
        const valStr = val ? String(val).trim() : '';
        if (valStr && valStr.startsWith('{') && valStr.endsWith('}')) {
          jsonUiVal = valStr;
          break;
        }
      }
    }
    p.json_ui_parsed = {};
    if (jsonUiVal) {
      try { p.json_ui_parsed = JSON.parse(jsonUiVal); } catch(e) {}
    }
    
    return p;
  });
  return window.MAPPED_POOL_DATA;
};

// Update switcher counts
window.updateSwitcherCounts = function() {
  const poolEl = document.getElementById('countPool');
  if (poolEl) poolEl.textContent = POOL_ROWS ? POOL_ROWS.length : '0';
};

// Data finalizing logic
window.finalizeData = function(fullList) {
  window.isDataLoaded = true;
  const urlParams = new URLSearchParams(window.location.search);
  const shareBitmask = urlParams.get('b');
  const shareToken = urlParams.get('s');
  
  if (shareBitmask) {
    const allIds = fullList.filter(p => !p.is_invisible).map(p => String(p.id));
    window.sharedIds = window.decodeBitmask(shareBitmask, allIds);
  } else if (shareToken) {
    try {
      // 1. Thử giải mã Base64URL safe danh sách ID phân cách bằng dấu phẩy
      let normalizedToken = shareToken.replace(/-/g, '+').replace(/_/g, '/');
      while (normalizedToken.length % 4) normalizedToken += '=';
      const decoded = atob(normalizedToken);
      if (decoded.includes(',') || decoded.startsWith('SYS-') || /^[a-zA-Z0-9,._-]+$/.test(decoded)) {
        window.sharedIds = decoded.split(',').map(s => s.trim()).filter(Boolean);
      } else {
        // Thử parse JSON
        const parsed = JSON.parse(decoded);
        if (Array.isArray(parsed)) window.sharedIds = parsed;
      }
    } catch (e) {
      // 2. Fallback cho link cũ không mã hóa trực tiếp
      window.sharedIds = shareToken.split(',').map(s => s.trim()).filter(Boolean);
    }
  }
  
  if (window.sharedIds) {
    window.sharedIds = window.sharedIds.map(tk => {
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

  if (window.sharedIds) {
    DATA = fullList.filter(p => window.sharedIds.map(String).includes(String(p.id)) && !p.is_invisible);
  } else if (!window.isAdmin) {
    DATA = [];
    window.showError('Vui lòng liên hệ <b>Khang Ngô Nhà Phố</b> để được cung cấp thông tin.');
  } else {
    DATA = fullList.filter(p => !p.is_invisible);
  }

  const isPreview = new URLSearchParams(window.location.search).get('preview') === 'true';
  const isClientView = (shareBitmask || window.sharedIds) && !window.isAdmin && !isPreview;
  if (typeof window.checkLeadCapture === 'function') {
    window.checkLeadCapture(isClientView);
  }

  if (DATA.length > 0) {
    window.trackAction("Mở danh sách nhà", `Số lượng hiển thị: ${DATA.length} căn`);
  }

  if (typeof renderCriteriaCheckboxes === 'function') renderCriteriaCheckboxes(DATA);
  if (typeof updateStaticTabsVisibility === 'function') updateStaticTabsVisibility(DATA);
  window.restoreState();
  window.updateSortButtonsUI();

  if (typeof buildDistrictTabs === 'function') buildDistrictTabs();
  if (typeof buildWardTabs === 'function') buildWardTabs();
  if (typeof buildDuongTabs === 'function') buildDuongTabs();
  if (typeof buildHuongTabs === 'function') buildHuongTabs();
  if (typeof window.renderDynamicFilters === 'function') window.renderDynamicFilters();
  if (typeof updateFilterSummary === 'function') updateFilterSummary();
  window.updateStats();
  if (typeof render === 'function') render();
  window.updateSwitcherCounts();

  if (isPreview && DATA.length > 0) {
    setTimeout(() => {
      openS(DATA[0].id);
    }, 100);
  }
  if (window.isAdmin) {
    window.showGoogleLoginButtonState(true);
  }

  if (window.isAdmin && shareToken && shareToken.startsWith('SYS-')) {
    const isOnAir = fullList.some(h => h.system_id === shareToken);
    if (!isOnAir && POOL_ROWS && POOL_ROWS.length) {
      const poolRow = POOL_ROWS.find(r => String(r[72] || r[71] || '').trim() === String(shareToken).trim());
      if (poolRow) {
        setTimeout(() => {
          if (typeof openPoolS === 'function') openPoolS(shareToken);
        }, 800);
        return;
      }
    }
  }

  if (window.isAdmin) {
    const autoPreviewId = localStorage.getItem('auto_preview_listing_id');
    if (autoPreviewId) {
      localStorage.removeItem('auto_preview_listing_id');
      setTimeout(() => {
        openS(autoPreviewId, null, true);
      }, 850);
    }

    const autoShareId = localStorage.getItem('auto_share_zalo_listing_id');
    if (autoShareId) {
      localStorage.removeItem('auto_share_zalo_listing_id');
      setTimeout(() => {
        if (confirm(`🎉 Căn nhà #${autoShareId} đã LÊN SÓNG thành công và đang hiển thị trên Customer View!\n\nBạn có muốn tạo Link chia sẻ gửi Zalo cho khách hàng ngay bây giờ không?`)) {
          if (typeof shareZaloFromAdminDetail === 'function') shareZaloFromAdminDetail(autoShareId);
        }
      }, 1250);
    }
  }
};

// Password Prompter
let loginClickCount = 0;
let lastLoginClickTime = 0;
window.triggerAdminAuthPrompt = async function() {
  const now = Date.now();
  if (now - lastLoginClickTime > 2000) {
    loginClickCount = 0;
  }
  lastLoginClickTime = now;
  loginClickCount++;
  if (loginClickCount < 5) return;
  loginClickCount = 0;
  
  const pw = prompt("Nhập mật khẩu Admin để đăng nhập:");
  if (pw === null) return;
  
  const ADMIN_PASSWORD_HASH = '47d21fb4481381e84d4395fe14126396fe40e872abdcfa973f6c66c12997c35f';
  const hashedInput = await sha256(pw.trim());
  if (hashedInput === ADMIN_PASSWORD_HASH) {
    localStorage.setItem('isAdminSession', 'true');
    alert("Đăng nhập Admin thành công!");
    const url = new URL(window.location.href);
    url.searchParams.delete('pwd');
    url.searchParams.delete('pw');
    url.searchParams.delete('c');
    url.searchParams.delete('b');
    url.searchParams.delete('s');
    window.location.href = url.toString();
  } else {
    alert("Sai mật khẩu Admin!");
  }
};

// Error displayer
window.showError = function(msg) {
  window.hasErrorState = true;
  const list = document.getElementById('list');
  if (!list) return;
  list.innerHTML = '';
  
  const adminLoginLink = !window.isAdmin ? `
    <div style="margin-top: 24px; padding-top: 16px; border-top: 1px dashed rgba(255,255,255,0.08);">
      <span onclick="triggerAdminAuthPrompt()" style="font-size: 12px; color: var(--sub); cursor: pointer; opacity: 0.4; transition: all 0.2s; display: inline-flex; align-items: center; gap: 4px; font-family: inherit; font-weight: 500; user-select: none; -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none;" onmouseover="this.style.opacity=0.8; this.style.color='var(--gold)'" onmouseout="this.style.opacity=0.4; this.style.color='var(--sub)'">
        🔒 Hệ thống quản trị viên
      </span>
    </div>
  ` : '';

  list.insertAdjacentHTML('beforeend', `
    <div class="err-box">
      <h3>🏠 Thông báo</h3>
      <p style="font-size: 15px; font-weight: 500;">${msg}</p>
      ${adminLoginLink}
    </div>`);
};

// Filter state saving
window.saveState = function() {
  const shareBitmask = new URLSearchParams(window.location.search).get('b');
  const shareToken = new URLSearchParams(window.location.search).get('s');
  if (!window.isAdmin || shareBitmask || shareToken) return;
  
  const serializedDynamicFilters = {};
  if (window.activeDynamicFilters) {
    for (const [field, val] of Object.entries(window.activeDynamicFilters)) {
      if (val instanceof Set) {
        serializedDynamicFilters[field] = { type: 'set', data: [...val] };
      } else {
        serializedDynamicFilters[field] = val;
      }
    }
  }
  
  const state = {
    districts: [...selDistricts],
    wards: [...selWards],
    duongs: [...selDuongs],
    huongs: [...selHuong],
    gia: [...selGia],
    danhGia: [...selDanhGia],
    selectedIds: [...SELECTED_IDS],
    favOnly: showFavOnly,
    showOnAirOnly: showOnAirOnly,
    search: document.getElementById('bdsSearchInput')?.value || '',
    adv: {
      giaMin: document.getElementById('filterGiaMin')?.value || '',
      giaMax: document.getElementById('filterGiaMax')?.value || '',
      dtTrenSoMin: document.getElementById('filterDtTrenSoMin')?.value || '',
      dtTrenSoMax: document.getElementById('filterDtTrenSoMax')?.value || '',
      dtThucTeMin: document.getElementById('filterDtThucTeMin')?.value || '',
      dtThucTeMax: document.getElementById('filterDtThucTeMax')?.value || '',
      ngangMin: document.getElementById('filterNgangMin')?.value || '',
      ngangMax: document.getElementById('filterNgangMax')?.value || '',
      hemMin: document.getElementById('filterHemMin')?.value || '',
      hemMax: document.getElementById('filterHemMax')?.value || '',
      phongMin: document.getElementById('filterPhongMin')?.value || '',
      phongMax: document.getElementById('filterPhongMax')?.value || ''
    },
    criteria: Array.from(document.querySelectorAll('.filter-criterion:checked')).map(el => el.getAttribute('data-val')),
    dynamicFilters: serializedDynamicFilters
  };
  localStorage.setItem('adminState', JSON.stringify(state));
};

// Filter state restoring
window.restoreState = function() {
  const shareBitmask = new URLSearchParams(window.location.search).get('b');
  const shareToken = new URLSearchParams(window.location.search).get('s');
  if (!window.isAdmin || shareBitmask || shareToken) return;
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
    if (state.showOnAirOnly !== undefined) {
      showOnAirOnly = state.showOnAirOnly;
      const toggle = document.getElementById('onAirToggle');
      if (toggle) toggle.checked = showOnAirOnly;
    }

    const sInput = document.getElementById('bdsSearchInput');
    if (sInput && state.search) {
      sInput.value = state.search;
      if (typeof toggleSearchClearBtn === 'function') toggleSearchClearBtn();
    }

    if (state.adv) {
      const advKeys = [
        { id: 'filterGiaMin', val: state.adv.giaMin },
        { id: 'filterGiaMax', val: state.adv.giaMax },
        { id: 'filterDtTrenSoMin', val: state.adv.dtTrenSoMin },
        { id: 'filterDtTrenSoMax', val: state.adv.dtTrenSoMax },
        { id: 'filterDtThucTeMin', val: state.adv.dtThucTeMin },
        { id: 'filterDtThucTeMax', val: state.adv.dtThucTeMax },
        { id: 'filterNgangMin', val: state.adv.ngangMin },
        { id: 'filterNgangMax', val: state.adv.ngangMax },
        { id: 'filterHemMin', val: state.adv.hemMin },
        { id: 'filterHemMax', val: state.adv.hemMax },
        { id: 'filterPhongMin', val: state.adv.phongMin },
        { id: 'filterPhongMax', val: state.adv.phongMax }
      ];
      advKeys.forEach(k => {
        const el = document.getElementById(k.id);
        if (el && k.val !== undefined) el.value = k.val;
      });
    }

    if (state.criteria) {
      const critSet = new Set(state.criteria);
      document.querySelectorAll('.filter-criterion').forEach(el => {
        el.checked = critSet.has(el.getAttribute('data-val'));
      });
    } else {
      document.querySelectorAll('.filter-criterion').forEach(el => el.checked = false);
    }

    if (state.dynamicFilters) {
      window.activeDynamicFilters = {};
      for (const [field, val] of Object.entries(state.dynamicFilters)) {
        if (val && typeof val === 'object' && val.type === 'set' && Array.isArray(val.data)) {
          const newSet = new Set(val.data);
          window.activeDynamicFilters[field] = newSet;
          
          // Re-check checkboxes in the UI if rendered
          const optionsDiv = document.getElementById(`dynamic_options_${field}`);
          if (optionsDiv) {
            optionsDiv.querySelectorAll('input[type="checkbox"]').forEach(cb => {
              cb.checked = newSet.has(cb.value);
            });
            const placeholder = document.getElementById(`dynamic_placeholder_${field}`);
            if (placeholder) {
              if (newSet.size === 0) {
                placeholder.textContent = 'Tất cả';
                placeholder.style.color = 'rgba(44, 44, 46, 0.5)';
              } else {
                placeholder.textContent = [...newSet].join(', ');
                placeholder.style.color = '#2c2c2e';
              }
            }
          }
        } else {
          window.activeDynamicFilters[field] = val;
          const selectEl = document.getElementById(`filter_${field}`);
          if (selectEl) {
            selectEl.value = val || '';
          }
        }
      }
    } else {
      window.activeDynamicFilters = {};
    }

    if (typeof syncTabUI === 'function') {
      syncTabUI('giaTabs', selGia);
      syncTabUI('danhGiaTabs', selDanhGia);
    }

    window.updateSortButtonsUI();
    if (typeof window.updateFavBtnUI === 'function') window.updateFavBtnUI();

    const sc = document.getElementById('shareCount');
    if (sc) sc.textContent = SELECTED_IDS.size;

    if (window.activeCollectionName && typeof window.viewCollection === 'function') {
      window.viewCollection(window.activeCollectionName, false);
    }
  } catch (e) {
    console.error('Lỗi restore state:', e);
  }
};

// Update statistics
window.updateStats = function() {
  const arr = typeof getFiltered === 'function' ? getFiltered() : [];
  if (!arr.length) {
    const totalBadge = document.getElementById('totalBadge');
    if (totalBadge) totalBadge.textContent = '0 BĐS';
    
    const sTong = document.getElementById('sTong');
    if (sTong) sTong.textContent = '0';
    
    const sTang = document.getElementById('sTang');
    if (sTang) sTang.textContent = '-';
    
    const sGia = document.getElementById('sGia');
    if (sGia) sGia.textContent = '-';
    
    const sDt = document.getElementById('sDt');
    if (sDt) sDt.textContent = '-';
    
    const sQuan = document.getElementById('sQuan');
    if (sQuan) sQuan.textContent = '-';
    return;
  }
  const gias = arr.map(p => parseFloat(p.gia)).filter(Boolean);
  const dts = arr.map(p => parseFloat(p.dt)).filter(Boolean);
  const tangs = arr.map(p => parseFloat(p.tang)).filter(Boolean);
  const quans = [...new Set(arr.map(p => p.q).filter(Boolean))].length;
  
  const sTong = document.getElementById('sTong');
  if (sTong) sTong.textContent = arr.length;
  
  const sTang = document.getElementById('sTang');
  if (sTang) sTang.textContent = tangs.length ? `${Math.min(...tangs)}–${Math.max(...tangs)}` : '-';
  
  const sGia = document.getElementById('sGia');
  if (sGia) sGia.textContent = gias.length ? `${Math.min(...gias).toFixed(1)}–${Math.max(...gias).toFixed(1)}` : '-';
  
  const sDt = document.getElementById('sDt');
  if (sDt) sDt.textContent = dts.length ? `${Math.min(...dts)}–${Math.max(...dts)}` : '-';
  
  const sQuan = document.getElementById('sQuan');
  if (sQuan) sQuan.textContent = quans || '-';
  
  const totalBadge = document.getElementById('totalBadge');
  if (totalBadge) totalBadge.textContent = `${arr.length} BĐS`;
};

// Update sorting buttons UI
window.updateSortButtonsUI = function() {
  const btnNew = document.getElementById('sortNewBtn');
  const btnPrice = document.getElementById('sortPriceBtn');
  if (!btnNew || !btnPrice) return;

  if (window.currentSortType === 'newest') {
    btnNew.classList.add('active');
    btnNew.textContent = window.currentSortDir === 'desc' ? '⏱️⬇' : '⏱️⬆';
    btnPrice.classList.remove('active');
    btnPrice.textContent = '💰';
  } else {
    btnPrice.classList.add('active');
    btnPrice.textContent = window.currentSortDir === 'desc' ? '💰⬇' : '💰⬆';
    btnNew.classList.remove('active');
    btnNew.textContent = '⏱️';
  }
};

// Sort triggers
window.toggleSortNew = function() {
  if (window.currentSortType === 'newest') {
    window.currentSortDir = window.currentSortDir === 'desc' ? 'asc' : 'desc';
  } else {
    window.currentSortType = 'newest';
    window.currentSortDir = 'desc';
  }
  window.updateSortButtonsUI();
  window.saveState();
  if (typeof render === 'function') render();
};

window.toggleSortPrice = function() {
  if (window.currentSortType === 'price') {
    window.currentSortDir = window.currentSortDir === 'desc' ? 'asc' : 'desc';
  } else {
    window.currentSortType = 'price';
    window.currentSortDir = 'desc';
  }
  window.updateSortButtonsUI();
  window.saveState();
  if (typeof render === 'function') render();
};

// Accent striping helper
window.stripVietnameseAccents = function(str) {
  if (!str) return "";
  return str.normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/đ/g, "d")
            .replace(/Đ/g, "D");
};

// Road reverser / abbreviator
window.abbreviateAndReverseRoad = function(roadName) {
  if (!roadName) return "";
  let normalized = roadName.trim();
  if (/cách mạng tháng (tám|8)|cmt8/i.test(normalized)) {
    normalized = "CMTT";
  } else if (/ba tháng hai|3 tháng 2|3\/2|3-2/i.test(normalized)) {
    normalized = "BTH";
  } else if (/đường số (\d+)/i.test(normalized)) {
    const match = normalized.match(/đường số (\d+)/i);
    normalized = "DS" + match[1];
  }
  
  let abbr = "";
  if (normalized === "CMTT" || normalized === "BTH" || normalized.startsWith("DS")) {
    abbr = normalized;
  } else {
    const cleanRoad = window.stripVietnameseAccents(normalized);
    const words = cleanRoad.trim().split(/\s+/).filter(w => w.length > 0);
    abbr = words.map(w => w[0].toUpperCase()).join('');
  }
  const reversed = abbr.split('').reverse().join('');
  return reversed;
};

// Map house number to code
window.mapSoNha = function(soNha) {
  if (!soNha) return "";
  const map = { '1': 'M', '2': 'H', '3': 'B', '4': 'A', '5': 'N', '6': 'S', '7': 'Z', '8': 'T', '9': 'C', '0': 'O', '/': 'I', '.': 'I' };
  let res = "";
  for (let i = 0; i < soNha.length; i++) {
    const char = soNha[i];
    const lowerChar = char.toLowerCase();
    res += map[lowerChar] !== undefined ? map[lowerChar] : char.toLowerCase();
  }
  return res;
};

// ID generator
window.generateMaKhangNgo = function(soNha, duong) {
  if (!soNha || !duong) return "";
  let cleanSoNha = soNha.toString().trim();
  if (cleanSoNha.includes('+')) {
    cleanSoNha = cleanSoNha.split('+')[0].trim();
  }
  const soNhaCode = window.mapSoNha(cleanSoNha);
  const duongCode = window.abbreviateAndReverseRoad(duong);
  let combined = soNhaCode + 'I' + duongCode;
  if (combined.length > 1) {
    combined = combined[0] + 'W' + combined.substring(1);
  } else {
    combined = combined + 'W';
  }
  return combined;
};

// Automatic titles & descriptions
window.generateAutoTitle = function(p) {
  const typeStr = (p.raw_so_nha && (p.raw_so_nha.includes('/') || p.raw_so_nha.includes('.'))) ? "Hẻm" : "Mặt tiền";
  const phuongStr = p.phuong ? (p.phuong.toLowerCase().startsWith('p') ? p.phuong : 'P.' + p.phuong) : '';
  const quanStr = p.ql ? ('Q.' + p.ql) : '';
  const dtStr = (p.dt || p.raw_dt_tren_so) ? ((p.dt || p.raw_dt_tren_so) + 'm²') : '';
  return `${typeStr} ${p.raw_ten_duong || ''} ${quanStr} - ${dtStr} - ${p.gia || p.raw_gia_chao} Tỷ`;
};

window.generateAutoDescription = function(p) {
  const typeStr = (p.raw_so_nha && (p.raw_so_nha.includes('/') || p.raw_so_nha.includes('.'))) ? "HẺM XE HƠI SẠCH SẼ" : "MẶT TIỀN KINH DOANH SẦM UẤT";
  const dt = p.dt || p.raw_dt_tren_so || "-";
  const ngang = p.mat || p.raw_mat_tien || "-";
  const dai = p.dai_nha || "-";
  const ketCau = p.tang || p.raw_so_tang || "-";
  const huong = p.huong || "-";
  const gia = p.gia || p.raw_gia_chao || "-";
  const phuong = p.phuong || "-";
  const quan = p.ql || "-";
  
  return `Vị trí: ${typeStr} đường ${p.raw_ten_duong || ''}, ${phuong.startsWith('P') ? phuong : 'Phường ' + phuong}, ${quan.startsWith('Q') ? quan : 'Quận ' + quan}.\n` +
         `Thông số: Diện tích ${dt}m², bề ngang rộng ${ngang}m, chiều dài ${dai}m.\n` +
         `Kết cấu: Nhà xây ${ketCau} tầng kiên cố, hướng ${huong}.\n` +
         `Giá chào bán: ${gia} Tỷ (Chủ nhà thiện chí thương lượng trực tiếp).\n` +
         `Mô tả tiện ích: Khu vực an ninh, dân trí cao, kết nối giao thông vô cùng thuận tiện qua các trục đường huyết mạch kế bên. Tiện để ở, làm văn phòng công ty hoặc kinh doanh đa ngành nghề.`;
};

// URL normalization
window.normalizeImgUrl = function(url) {
  if (!url) return '';
  const cleanUrl = String(url).trim();
  
  const m1 = cleanUrl.match(/drive\.google\.com\/file\/d\/([^/?\s&]+)/);
  if (m1) return m1[1];
  const m2 = cleanUrl.match(/[?&]id=([^&\s]+)/);
  if (m2) return m2[1];
  const m3 = cleanUrl.match(/\/uploads\/([^/?\s&.]+)/);
  if (m3) return m3[1];
  
  const filenameMatch = cleanUrl.match(/\/([^/?\s]+)$/);
  if (filenameMatch) {
    const filename = filenameMatch[1];
    const dotIdx = filename.indexOf('.');
    return dotIdx !== -1 ? filename.substring(0, dotIdx) : filename;
  }
  
  return cleanUrl;
};

// === isListingSodoUrl ===
window.isListingSodoUrl = function(url, p) {
  if (!url) return false;
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

  // 2. Nhận diện theo curated_config nếu có
  if (p && p.curated_config && Array.isArray(p.curated_config.images)) {
    const isSodoInConfig = p.curated_config.images.some(img => {
      if (img && img.url && (img.role === 'Sơ đồ' || img.role === 'diagram')) {
        return normFn(img.url) === norm;
      }
      return false;
    });
    if (isSodoInConfig) return true;
  }

  // 3. Lấy 5 giá trị sodo hiện có của căn nhà (đọc từ DOM hoặc từ p)
  if (p) {
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
  }
  
  return false;
};

// Image downloads
window.downloadSingleImage = async function(url, fileName) {
  try {
    const cleanUrl = url.includes('res.cloudinary.com') ? url : (typeof fixImgUrl === 'function' ? fixImgUrl(url, 'w2000') : url);
    const response = await fetch(cleanUrl);
    if (!response.ok) throw new Error(`HTTP status ${response.status}`);
    const blob = await response.blob();
    let ext = 'jpg';
    const urlLower = cleanUrl.toLowerCase();
    if (urlLower.includes('.png')) ext = 'png';
    else if (urlLower.includes('.webp')) ext = 'webp';
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = `${fileName}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
  } catch (err) {
    console.error(`[DL] fetch failed: ${url}`, err);
    try {
      const response = await fetch(url);
      if (response.ok) {
        const blob = await response.blob();
        let ext = 'jpg';
        const urlLower = url.toLowerCase();
        if (urlLower.includes('.png')) ext = 'png';
        else if (urlLower.includes('.webp')) ext = 'webp';
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = `${fileName}.${ext}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
        return;
      }
    } catch (e) { console.error(`[DL] fallback failed: ${url}`, e); }
    window.open(url, '_blank');
  }
};

window.fetchAllBlobs = async function(urls, fileNames, onProgress) {
  const results = [];
  for (let i = 0; i < urls.length; i++) {
    if (onProgress) onProgress(i + 1, urls.length);
    const url = urls[i];
    const fileName = fileNames[i];
    try {
      const cleanUrl = url.includes('res.cloudinary.com') ? url : (typeof fixImgUrl === 'function' ? fixImgUrl(url, 'w2000') : url);
      let response = await fetch(cleanUrl);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const blob = await response.blob();
      let ext = 'jpg';
      const urlLower = cleanUrl.toLowerCase();
      if (urlLower.includes('.png')) ext = 'png';
      else if (urlLower.includes('.webp')) ext = 'webp';
      results.push({ ok: true, blob, name: `${fileName}.${ext}` });
    } catch (e) {
      console.warn(`Failed downloading ${url}, trying fallback without resize`, e);
      try {
        const response = await fetch(url);
        if (response.ok) {
          const blob = await response.blob();
          let ext = 'jpg';
          const urlLower = url.toLowerCase();
          if (urlLower.includes('.png')) ext = 'png';
          else if (urlLower.includes('.webp')) ext = 'webp';
          results.push({ ok: true, blob, name: `${fileName}.${ext}` });
          continue;
        }
      } catch (err) { }
      results.push({ ok: false, url, name: fileName });
    }
  }
  return results;
};

window.shareAllImagesToGallery = async function(blobResults) {
  if (!navigator.canShare || !navigator.share) return false;
  const successfulBlobs = blobResults.filter(r => r.ok);
  if (successfulBlobs.length === 0) return false;

  try {
    const files = successfulBlobs.map(r => new File([r.blob], r.name, { type: r.blob.type }));
    if (navigator.canShare({ files })) {
      await navigator.share({
        files: files,
        title: 'Lưu hình ảnh',
        text: 'Lưu toàn bộ hình ảnh căn nhà vào máy ảnh'
      });
      return true;
    }
  } catch (e) {
    console.warn("Navigator share failed, using fallback sequential download", e);
  }
  return false;
};

window.downloadSequential = async function(blobResults) {
  for (const r of blobResults) {
    if (!r.ok) continue;
    const blobUrl = URL.createObjectURL(r.blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = r.name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    await new Promise(resolve => setTimeout(resolve, 350));
    URL.revokeObjectURL(blobUrl);
  }
};

window.renderDownloadProgress = function(current, total, btn) {
  let bar = document.getElementById('dl-progress-wrap');
  if (!bar) {
    bar = document.createElement('div');
    bar.id = 'dl-progress-wrap';
    bar.style.cssText = `
      margin-top: 10px;
      width: 100%;
      background: rgba(255,255,255,0.06);
      border-radius: 8px;
      height: 16px;
      position: relative;
      overflow: hidden;
      border: 1px solid rgba(255,255,255,0.04);
    `;
    bar.innerHTML = `
      <div id="dl-progress-fill" style="width:0%; height:100%; background:var(--gold); transition:width 0.2s;"></div>
      <div id="dl-progress-label" style="position:absolute; top:0; left:0; width:100%; height:100%; display:flex; align-items:center; justify-content:center; font-size:10px; font-weight:800; color:white; text-shadow:0 1px 2px rgba(0,0,0,0.8);">🖼️ 0/${total}</div>
    `;
    if (btn && btn.parentNode) btn.parentNode.insertBefore(bar, btn.nextSibling);
    else document.body.appendChild(bar);
  }
  const pct = Math.round((current / total) * 100);
  const fillEl = document.getElementById('dl-progress-fill');
  const labelEl = document.getElementById('dl-progress-label');
  if (fillEl) fillEl.style.width = pct + '%';
  if (labelEl) labelEl.textContent = '🖼️ ' + current + '/' + total + '...';
};

window.clearDownloadProgress = function() {
  const bar = document.getElementById('dl-progress-wrap');
  if (bar) bar.remove();
};

window.downloadAllListingImages = async function(id) {
  const p = window.activeCurationListing || DATA.find(x => String(x.id) === String(id) || String(x.system_id) === String(id));
  if (!p) { alert('Không tìm thấy thông tin căn nhà!'); return; }

  const urls = [];
  const facadeUrl = (p.img_mat_tien || (p.pool_row_data ? p.pool_row_data[29] : '') || '').trim();
  if (facadeUrl) urls.push(facadeUrl);
  if (p.imgs && Array.isArray(p.imgs)) {
    p.imgs.forEach(url => {
      const u = (url || '').trim();
      if (u && !urls.includes(u)) {
        if (!window.isListingSodoUrl || !window.isListingSodoUrl(u, p)) urls.push(u);
      }
    });
  }
  if (urls.length === 0) { alert('Căn nhà này không có hình ảnh nào để tải!'); return; }

  const prefix = p.system_id || p.id || 'bds';
  const fileNames = urls.map((_, i) => `${prefix}-${i + 1}`);

  const btn = document.activeElement && document.activeElement.tagName === 'BUTTON' ? document.activeElement : null;
  const originalHTML = btn ? btn.innerHTML : null;
  if (btn) { btn.disabled = true; btn.innerHTML = '⏳ Chuẩn bị...'; }

  try {
    const blobResults = await window.fetchAllBlobs(urls, fileNames, (cur, tot) => {
      window.renderDownloadProgress(cur, tot, btn);
      if (btn) btn.innerHTML = '⏳ ' + cur + '/' + tot + '...';
    });

    const successCount = blobResults.filter(r => r.ok).length;
    const shared = await window.shareAllImagesToGallery(blobResults);

    if (!shared) {
      if (btn) btn.innerHTML = '📥 Đang lưu...';
      await window.downloadSequential(blobResults);
    }

    window.clearDownloadProgress();
    window.trackAction("Tải trọn bộ ảnh v2", `#${prefix} - ${successCount}/${urls.length} ảnh - ${shared ? 'Share' : 'Sequential'}`);
    showToast(`✅ Đã lưu ${successCount} ảnh${shared ? ' vào Gallery!' : ' thành công!'}`, 'success');

  } catch (error) {
    window.clearDownloadProgress();
    showToast('Có lỗi xảy ra khi tải ảnh: ' + error.message, 'error');
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = originalHTML || '📥 Tải toàn bộ ảnh'; }
  }
};

// Dummy curation list sorter
window.sortCurationImageGrid = function() {};
window.activeImageEditorIndex = 0;
window.carouselJustMounted = true;
window.touchStartX = 0;
window.touchEndX = 0;

// Column index resolvers
window.getPoolInteriorColIdx = function(imgIdx) {
  return imgIdx <= 15 ? (39 + imgIdx) : (67 + imgIdx);
};

window.getPoolSodoColIdx = function(sodoIdx) {
  return sodoIdx <= 2 ? (26 + sodoIdx) : (77 + sodoIdx);
};

window.getPoolAlleyColIdx = function(alleyIdx) {
  return 29 + alleyIdx;
};

// Check if pool row is currently published on air
window.isPoolRowOnAir = function(row) {
  const systemId = row[72] || row[71] || '';
  const maKN = row[55] || systemId || '';
  return DATA.some(p => (systemId && String(p.system_id) === String(systemId)) || (maKN && String(p.id) === String(maKN)));
};

// Toast notification helper
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
    background: ${type === 'success' ? '#27ae60' : (type === 'warning' ? '#f39c12' : '#e74c3c')};
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
    <span>${type === 'success' ? '✅' : (type === 'warning' ? '⚠️' : '❌')}</span>
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

// Zalo inquiry helper
window.askZalo = function(id, title) {
  const msg = `Chào Khang Ngô Nhà Phố, tôi quan tâm căn nhà mã #${id}: ${title}. Tư vấn giúp tôi nhé!`;
  const url = `https://zalo.me/0979841573?text=${encodeURIComponent(msg)}`;
  window.open(url, '_blank');
};

// Client ID saver
window.saveGoogleClientId = function() {
  const input = document.getElementById('gClientIdInput');
  if (input) {
    const val = input.value.trim();
    localStorage.setItem('gClientId', val);
    showToast("Đã lưu Client ID thành công!", "success");
    setTimeout(() => window.location.reload(), 800);
  }
};

// Login button state updater
window.showGoogleLoginButtonState = function(isLoggedIn) {
  const gLoginBtn = document.getElementById('gLoginBtn');
  const gLoginText = document.getElementById('gLoginText');
  if (gLoginBtn) {
    if (isLoggedIn) {
      gLoginBtn.style.background = "#27ae60";
      gLoginBtn.style.boxShadow = "0 4px 15px rgba(39,174,96,0.3)";
      if (gLoginText) gLoginText.textContent = "ĐÃ ĐĂNG NHẬP ADMIN";
    } else {
      gLoginBtn.style.background = "var(--gold)";
      gLoginBtn.style.boxShadow = "0 4px 15px rgba(255,191,36,0.3)";
      if (gLoginText) gLoginText.textContent = "ĐĂNG NHẬP GOOGLE ADMIN";
    }
  }
};

// Background retrieval of private facade images
window.fetchFacadeImages = async function() {
  const clientId = localStorage.getItem('gClientId');
  if (!clientId) return;
  const token = localStorage.getItem('g_access_token');
  if (!token) return;

  const url = `/api/get-facade-images`;
  try {
    const res = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!res.ok) throw new Error(`Google API status ${res.status}`);
    const data = await res.json();
    const values = data.values || [];
    const facadeMap = {};
    for (let i = 0; i < values.length; i++) {
      const row = values[i];
      const id = row[0];
      const img = row[35] || '';
      if (id && img) {
        facadeMap[String(id).trim()] = img.trim();
      }
    }
    // Update facade images in DATA store dynamically
    DATA.forEach(p => {
      const target = facadeMap[String(p.id).trim()];
      if (target) {
        p.img_mat_tien = target;
      }
    });
  } catch (err) {
    console.warn("Lỗi tải ngầm ảnh mặt tiền từ Sheets API:", err);
  }
};

// Event hook binding helper
if (window.LegoState) {
  LegoState.on('authStatusChanged', ({ isAdmin, isTokenValid }) => {
    window.isAdmin = isAdmin;
    window.showGoogleLoginButtonState(isTokenValid);
    if (isAdmin) {
      document.body.classList.add('is-admin');
      const sInput = document.getElementById('bdsSearchInput');
      if (sInput) {
        sInput.placeholder = "Tìm mã căn, đường, tên đầu chủ, ĐT...";
      }
    } else {
      document.body.classList.remove('is-admin');
      const sInput = document.getElementById('bdsSearchInput');
      if (sInput) {
        sInput.placeholder = "Tìm mã căn, đường, tiêu đề...";
      }
    }
  });

  LegoState.on('authRequired', () => {
    document.body.classList.add('is-locked');
    window.showGoogleLoginButtonState(false);
    const listContainer = document.getElementById('list');
    if (listContainer) {
      listContainer.innerHTML = `
        <div class="admin-auth-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 24px; text-align: center; background: rgba(255,255,255,0.02); border: 1.5px dashed rgba(255, 191, 36, 0.25); border-radius: 20px; margin: 40px auto; max-width: 420px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); backdrop-filter: blur(10px);">
          <div style="font-size: 50px; margin-bottom: 20px; filter: drop-shadow(0 0 10px rgba(255,191,36,0.35));">🔒</div>
          <h2 style="font-size: 18px; font-weight: 800; color: var(--gold); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; font-family: inherit;">Hệ Thống Quản Trị Viên</h2>
          <p style="font-size: 13px; color: rgba(255,255,255,0.75); line-height: 1.5; margin-bottom: 24px; font-family: inherit;">
            Chào mừng bạn đến với trang quản trị Khang Ngô Nhà Phố.
          </p>
          <button onclick="handleGoogleLoginClick()" style="background: var(--gold); color: #1c1c1e; border: none; padding: 14px 28px; border-radius: 12px; font-size: 13.5px; font-weight: 800; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: transform 0.2s; box-shadow: 0 4px 15px rgba(255,191,36,0.3); font-family: inherit; width: 100%;">
            <svg style="width:16px; height:16px; display:block;" viewBox="0 0 24 24">
              <path fill="#1c1c1e" d="M12.24 10.285V14.4h6.887c-.648 2.41-2.519 4.114-5.136 4.114-3.478 0-6.3-2.823-6.3-6.3s2.822-6.3 6.3-6.3c1.706 0 3.24.685 4.378 1.8l3.273-3.27C19.673 2.66 16.527 1.5 12.24 1.5 6.31 1.5 1.5 6.31 1.5 12.24s4.81 10.74 10.74 10.74c6.19 0 10.74-4.35 10.74-10.74 0-.724-.072-1.414-.18-2.072H12.24z"/>
            </svg>
            <span>⚡ ĐĂNG NHẬP GOOGLE ADMIN</span>
          </button>
        </div>
      `;
    }
  });

  LegoState.on('authSuccess', () => {
    document.body.classList.remove('is-locked');
  });

  LegoState.on('authError', (errMsg) => {
    alert("Lỗi xác thực Google: " + errMsg);
  });

  LegoState.on('clientIdRequired', () => {
    alert("Vui lòng nhập Google OAuth Client ID của bạn ở mục 'Cấu hình Google Admin' trong Bộ lọc trước!");
    if (!filterOpen) toggleFilter();
    setTimeout(() => {
      const input = document.getElementById('gClientIdInput');
      if (input) input.focus();
    }, 300);
  });

  LegoState.on('dataLoading', (type) => {
    if (type === 'secure') {
      document.body.classList.remove('is-locked');
      const listContainer = document.getElementById('list');
      if (listContainer) {
        listContainer.innerHTML = '<div style="text-align:center; padding: 40px; font-weight: 700; color: var(--red);">🏠 ĐANG NẠP DỮ LIỆU BẢO MẬT ADMIN SONG SONG...</div>';
      }
    }
  });

  LegoState.on('rawDataLoaded', (fullList) => {
    window.finalizeData(fullList);
  });

  LegoState.on('publicDataLoaded', () => {
    if (window.isAdmin) {
      console.log("Admin session detected in public fallback. Initiating background facade images retrieval...");
      window.fetchFacadeImages();
    }
  });

  LegoState.on('dataLoadError', (errMsg) => {
    window.showError(errMsg);
  });
}

// --- Application Initialization & Welcome Banner ---
window.initLegoApp = function() {
  const urlParams = new URLSearchParams(window.location.search);
  const customerToken = urlParams.get('c');
  if (customerToken) {
    try {
      let safeToken = customerToken.replace(/ /g, '+');
      while (safeToken.length % 4) {
        safeToken += '=';
      }
      const decoded = decodeURIComponent(escape(window.atob(safeToken)));
      const parts = decoded.split("|").map(p => p.trim());
      window.displayCustomerName = parts[0];
      window.trackingCustomerName = `${parts[0]}${parts[1] ? ' - ' + parts[1] : ''}`;
      const customPageTitle = parts[2] || "";
      if (customPageTitle) {
        document.title = customPageTitle;
      } else {
        document.title = "Giỏ hàng độc quyền - Khang Ngô Nhà Phố";
      }
    } catch (e) {
      window.displayCustomerName = "Khách Hàng";
      window.trackingCustomerName = "Khách Hàng";
      document.title = "Giỏ hàng độc quyền - Khang Ngô Nhà Phố";
    }
  } else {
    document.title = "Khang Ngô Nhà Phố";
  }

  if (window.displayCustomerName) {
    const banner = document.getElementById('welcomeBanner');
    if (banner) {
      banner.innerHTML = `👋 Xin chào <b>${window.displayCustomerName}</b>, đây là danh sách nhà Khang Ngô chọn riêng cho anh/chị!`;
      banner.style.display = 'block';
    }
  }

  if (window.isAdmin) {
    document.body.classList.add('is-admin');

    // Inject admin speed dial HTML (US-094E)
    if (!document.getElementById('adminSpeedDial')) {
      document.body.insertAdjacentHTML('beforeend', `
        <div class="admin-speed-dial" id="adminSpeedDial">
          <button class="dial-main-btn" id="dialMainBtn" onclick="toggleSpeedDial()" title="Quản lý rổ hàng">⚡</button>
          <div class="dial-actions" id="dialActions"></div>
        </div>
      `);
    }

    // Click outside handler for speed dial
    document.addEventListener('click', function(event) {
      const dial = document.getElementById('adminSpeedDial');
      const actions = document.getElementById('dialActions');
      const mainBtn = document.getElementById('dialMainBtn');
      const colViewModal = document.getElementById('colViewModal');
      const isColViewOpen = colViewModal && colViewModal.classList.contains('open');
      if (dial && actions && mainBtn && !dial.contains(event.target) && !isColViewOpen) {
        actions.classList.remove('open');
        mainBtn.innerHTML = '⚡';
      }
    });

    if (typeof window.updateShareUI === 'function') window.updateShareUI();
    if (typeof window.renderCollectionsManager === 'function') window.renderCollectionsManager();
    setTimeout(() => {
      if (window.initGoogleAuth) {
        window.initGoogleAuth();
      }
    }, 800);
  } else {
    document.body.classList.remove('is-admin');
  }

  if (typeof window.updateFavBtnUI === 'function') {
    window.updateFavBtnUI();
  }

  if (window.LegoState && typeof LegoState.loadData === 'function') {
    LegoState.loadData();
  }
};

// --- Main List Rendering Orchestration ---
window.render = function() {
  if (window.hasErrorState) return;
  const list = document.getElementById('list');
  if (!list) return;
  list.innerHTML = '';
  
  const filteredArr = typeof getFiltered === 'function' ? getFiltered() : DATA;
  const arr = filteredArr.slice().sort((a, b) => {
    if (currentSortType === 'newest') {
      let ta, tb;
      if (window.isAdmin && window.activeMode === 'pool' && window.showOnAirOnly) {
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
    if (window.isAdmin && window.activeMode === 'pool') {
      list.insertAdjacentHTML('beforeend', '<div style="text-align:center;padding:60px 20px;color:var(--sub);font-weight:500;">Không có bất động sản nào trong Kho Pool khớp với bộ lọc hiện tại.</div>');
    } else {
      list.insertAdjacentHTML('beforeend', '<div style="text-align:center;padding:60px 20px;color:var(--sub);font-weight:500;">Vui lòng liên hệ Khang Ngô Nhà Phố để được cung cấp thông tin.</div>');
    }
    return;
  }

  const isPool = (window.isAdmin && window.activeMode === 'pool');
  const maxRender = isPool ? 200 : arr.length;
  const itemsToRender = arr.slice(0, maxRender);

  const frag = document.createDocumentFragment();
  itemsToRender.forEach((p) => {
    let cardEl;
    if (window.isAdmin) {
      const curatedListing = DATA.find(x => 
        (x.system_id && p.system_id && String(x.system_id).trim() === String(p.system_id).trim()) ||
        (x.id && p.id && String(x.id).trim() === String(p.id).trim())
      );
      cardEl = window.LegoRenderAdmin.createCard(p, curatedListing, { 
        favs: favs, 
        SELECTED_IDS: SELECTED_IDS, 
        activeCollectionName: window.activeCollectionName 
      });
    } else {
      cardEl = window.LegoRenderClient.createCard(p, { 
        favs: favs, 
        activeCollectionName: window.activeCollectionName 
      });
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

  window.applyFilter();
};

window.executePoolFallbackSearch = function(query) {
  const resultsContainer = document.getElementById('poolFallbackResults');
  if (!resultsContainer) return;
  resultsContainer.innerHTML = '';
  
  const matched = typeof searchPoolRows === 'function' ? searchPoolRows(query) : [];
  if (matched.length === 0) {
    resultsContainer.innerHTML = '<div style="font-size: 13px; color: rgba(255,255,255,0.5); text-align: center; padding: 10px;">❌ Vẫn không tìm thấy căn nào trong Pool thô khớp từ khóa này.</div>';
    return;
  }
  
  resultsContainer.innerHTML = `<div style="font-size: 11.5px; font-weight: 800; color: var(--gold); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">📦 TÌM THẤY ${matched.length} CĂN TRONG POOL THÔ:</div>`;
  
  matched.slice(0, 15).forEach(row => {
    const isAlready = typeof isPoolRowOnAir === 'function' ? isPoolRowOnAir(row) : false;
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
      div.onclick = () => openS(id);
    } else {
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

// --- Share Link Generation Features ---
window.generateShareLink = async function() {
  try {
    if (SELECTED_IDS.size === 0) {
      alert('Vui lòng chọn ít nhất 1 căn nhà!');
      return;
    }

    const baseUrl = window.location.origin + window.location.pathname;
    const count = SELECTED_IDS.size;
    let shareUrl = '';

    if (count === 1) {
      const singleId = [...SELECTED_IDS][0];
      const house = DATA.find(p => String(p.id) === String(singleId));
      const systemId = house ? house.system_id : singleId;
      shareUrl = `${baseUrl}?s=${systemId}`;
    } else {
      const allIds = DATA.map(p => String(p.id));
      let bits = '';
      allIds.forEach(id => bits += SELECTED_IDS.has(id) ? '1' : '0');
      while (bits.length % 6) bits += '0';
      let encoded = '';
      for (let i = 0; i < bits.length; i += 6) {
        encoded += B64[parseInt(bits.substr(i, 6), 2)];
      }
      shareUrl = `${baseUrl}?b=${encoded}`;
    }

    if (navigator.share) {
      await navigator.share({
        title: 'Khang Ngô Nhà Phố - ' + count + ' căn',
        url: shareUrl
      });
      return;
    }

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
};

window.promptGenerateLink = function() {
  if (SELECTED_IDS.size === 0) {
    alert('Vui lòng chọn ít nhất 1 căn nhà để tạo link!');
    return;
  }
  document.getElementById('linkModalCount').textContent = SELECTED_IDS.size;
  document.getElementById('linkCustName').value = '';
  document.getElementById('linkCustTitle').value = '';
  document.getElementById('linkCustNote').value = '';
  document.getElementById('linkModal').classList.add('open');
};

window.shareZaloFromAdminDetail = function(id) {
  SELECTED_IDS.clear();
  SELECTED_IDS.add(String(id));
  if (typeof updateShareUI === 'function') updateShareUI();
  promptGenerateLink();
};

window.executeGenerateLink = function() {
  const cName = document.getElementById('linkCustName').value.trim();
  if (!cName) {
    alert("Vui lòng nhập Tên khách hàng!");
    return;
  }

  const cTitle = document.getElementById('linkCustTitle').value.trim();
  const cNote = document.getElementById('linkCustNote').value.trim();

  let parts = [cName];
  if (cTitle) {
    parts.push(cNote || "");
    parts.push(cTitle);
  } else if (cNote) {
    parts.push(cNote);
  }
  const compactCustomerString = parts.join('|');

  try {
    const encodedName = window.btoa(unescape(encodeURIComponent(compactCustomerString))).replace(/=/g, '');
    const baseUrl = window.location.origin + window.location.pathname;
    const count = SELECTED_IDS.size;
    let shareUrl = '';

    if (count === 1) {
      const singleId = [...SELECTED_IDS][0];
      const house = DATA.find(p => String(p.id) === String(singleId));
      const systemId = house ? house.system_id : singleId;
      shareUrl = `${baseUrl}?s=${systemId}&c=${encodeURIComponent(encodedName)}`;
    } else {
      const allIds = DATA.map(p => String(p.id));
      let bits = '';
      allIds.forEach(id => bits += SELECTED_IDS.has(id) ? '1' : '0');
      while (bits.length % 6) bits += '0';
      let encodedBitmask = '';
      for (let i = 0; i < bits.length; i += 6) {
        encodedBitmask += B64[parseInt(bits.substr(i, 6), 2)];
      }
      shareUrl = `${baseUrl}?b=${encodedBitmask}&c=${encodeURIComponent(encodedName)}`;
    }

    document.getElementById('linkModal').classList.remove('open');

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
    alert('Đã copy link gửi khách!\n(' + count + ' căn)\n\nDán link này vào Zalo để gửi cho khách nhé.');
  } catch (e) {
    alert('Có lỗi xảy ra: ' + e.message);
  }
};

window.executeGenerateQuickLink = function() {
  if (SELECTED_IDS.size === 0) {
    alert('Vui lòng chọn ít nhất 1 căn nhà để tạo link!');
    return;
  }
  try {
    const baseUrl = window.location.origin + window.location.pathname;
    const count = SELECTED_IDS.size;
    let shareUrl = '';

    if (count === 1) {
      const singleId = [...SELECTED_IDS][0];
      const house = DATA.find(p => String(p.id) === String(singleId));
      const systemId = house ? house.system_id : singleId;
      shareUrl = `${baseUrl}?s=${systemId}`;
    } else {
      // Mã hoá trực tiếp danh sách System ID bằng Base64URL safe để chống lệch căn khi thay đổi bộ lọc hoặc thêm tin mới
      const sysIdList = Array.from(SELECTED_IDS).map(id => {
        const house = DATA.find(p => String(p.id) === String(id));
        return house && house.system_id ? house.system_id : id;
      }).join(',');
      const encodedIds = window.btoa(sysIdList)
        .replace(/=/g, '')
        .replace(/\+/g, '-')
        .replace(/\//g, '_');
      shareUrl = `${baseUrl}?s=${encodedIds}`;
    }

    // Đóng Modal
    document.getElementById('linkModal').classList.remove('open');

    // Sao chép link vào clipboard
    const ta = document.createElement('textarea');
    ta.value = shareUrl;
    ta.style.cssText = 'position:fixed;left:0;top:0;opacity:0;';
    document.body.appendChild(ta);
    ta.focus(); ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    
    alert(`Đã copy link Công Khai Nhanh thành công!\n(Gồm ${count} căn)\n\nKhách mở link này sẽ tự nhập Tên và Số điện thoại để mở khóa xem nhà.`);
  } catch (e) {
    alert('Có lỗi xảy ra: ' + e.message);
  }
};

