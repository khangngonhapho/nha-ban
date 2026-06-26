// lego_filters.js
(function() {
  // Expose global filter variables on window
  window.selDistricts = new Set();
  window.selWards = new Set();
  window.selDuongs = new Set();
  window.selHuong = new Set();
  window.selGia = new Set();
  window.selDanhGia = new Set();
  window.filterOpen = false;
  window.showFavOnly = false;
  window.showOnAirOnly = false;

  // ── Multi-select helpers ──
  window.tSel = function(set, val) {
    if (val === 'all') { set.clear(); return; }
    if (set.has(val)) set.delete(val); else set.add(val);
  };

  window.syncTabUI = function(containerId, set) {
    document.querySelectorAll('#' + containerId + ' .tab').forEach(btn => {
      const v = btn.getAttribute('data-val');
      btn.classList.toggle('on', v === 'all' ? set.size === 0 : set.has(v));
    });
  };

  // ── Custom Multiselect Event Handlers ──
  window.toggleMultiselect = function(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;
    document.querySelectorAll('.multiselect-container').forEach(other => {
      if (other !== el) other.classList.remove('open');
    });
    el.classList.toggle('open');
  };

  window.toggleOption = function(category, val, event) {
    if (event && event.target.tagName === 'INPUT') {
      return;
    }
    const container = document.getElementById(category + 'Options');
    if (!container) return;
    const checkbox = container.querySelector(`input[value="${val}"]`);
    if (checkbox) {
      checkbox.checked = !checkbox.checked;
      window.updateSelectionFromCheckboxes(category);
    }
  };

  window.updateSelectionFromCheckboxes = function(category) {
    let set;
    if (category === 'district') set = window.selDistricts;
    else if (category === 'ward') set = window.selWards;
    else if (category === 'duong') set = window.selDuongs;
    else if (category === 'huong') set = window.selHuong;
    if (!set) return;

    const container = document.getElementById(category + 'Options');
    if (!container) return;

    set.clear();
    container.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
      set.add(cb.value);
    });

    window.updateMultiselectPlaceholder(category);

    if (category === 'district') {
      window.selWards.clear(); window.selDuongs.clear(); window.selHuong.clear();
      window.buildWardTabs(); window.buildDuongTabs(); window.buildHuongTabs();
    } else if (category === 'ward') {
      window.selDuongs.clear(); window.selHuong.clear();
      window.buildDuongTabs(); window.buildHuongTabs();
    }

    window.updateFilterSummary();
    if (typeof window.updateStats === 'function') window.updateStats();
    window.applyFilter();
  };

  window.updateMultiselectPlaceholder = function(category) {
    let set, namesMap;
    if (category === 'district') {
      set = window.selDistricts;
      namesMap = {
        q1: 'Quận 1', q2: 'Quận 2', q3: 'Quận 3', q4: 'Quận 4', q5: 'Quận 5', q6: 'Quận 6',
        q7: 'Quận 7', q8: 'Quận 8', q9: 'Quận 9', q10: 'Quận 10', q11: 'Quận 11', q12: 'Quận 12',
        pn: 'Phú Nhuận', tb: 'Tân Bình', bt: 'Bình Thạnh', gv: 'Gò Vấp',
        tp: 'Tân Phú', btan: 'Bình Tân', td: 'Thủ Đức',
        hm: 'Hóc Môn', nb: 'Nhà Bè', bc: 'Bình Chánh', cc: 'Củ Chi', cg: 'Cần Giờ'
      };
    } else if (category === 'ward') {
      set = window.selWards;
    } else if (category === 'duong') {
      set = window.selDuongs;
    } else if (category === 'huong') {
      set = window.selHuong;
    }
    const el = document.getElementById(category + 'Placeholder');
    if (!el) return;

    if (!set || set.size === 0) {
      el.textContent = 'Tất cả';
      el.style.color = 'rgba(44, 44, 46, 0.5)';
    } else {
      const selectedNames = [...set].map(val => namesMap ? (namesMap[val] || val) : val);
      el.textContent = selectedNames.join(', ');
      el.style.color = '#2c2c2e';
    }
  };

  // Close dropdowns on click outside
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.multiselect-container')) {
      document.querySelectorAll('.multiselect-container.open').forEach(el => {
        el.classList.remove('open');
      });
    }
  });

  window.applyGia = function(arr) {
    if (!window.selGia.size) return arr;
    return arr.filter(p => {
      const g = parseFloat(p.gia) || 0;
      return [...window.selGia].some(r => {
        if (r === 'lt7') return g < 7;
        if (r === '7-10') return g >= 7 && g <= 10;
        if (r === '10-15') return g > 10 && g <= 15;
        if (r === '15-20') return g > 15 && g <= 20;
        if (r === 'gt20') return g > 20;
        return false;
      });
    });
  };

  window.toggleSearchClearBtn = function() {
    const sInput = document.getElementById('bdsSearchInput');
    const clearBtn = document.getElementById('searchClear');
    if (sInput && clearBtn) {
      clearBtn.style.display = sInput.value.trim() ? 'flex' : 'none';
    }
  };

  window.clearSearchInput = function() {
    const sInput = document.getElementById('bdsSearchInput');
    if (sInput) {
      sInput.value = '';
      window.onSearchInput();
    }
  };

  let searchDebounceTimeout = null;
  window.onSearchInput = function() {
    window.toggleSearchClearBtn();
    if (searchDebounceTimeout) clearTimeout(searchDebounceTimeout);
    searchDebounceTimeout = setTimeout(() => {
      if (typeof window.updateStats === 'function') window.updateStats();
      window.applyFilter();
      if (typeof window.saveState === 'function') window.saveState();
    }, 250);
  };

  window.toggleSearchBar = function() {
    const bar = document.getElementById('searchBar');
    const btn = document.getElementById('searchToggleBtn');
    const input = document.getElementById('bdsSearchInput');
    if (!bar || !btn || !input) return;
    const isOpen = bar.classList.toggle('open');
    btn.classList.toggle('active', isOpen);
    if (isOpen) {
      setTimeout(() => input.focus(), 150);
    } else {
      input.value = '';
      window.onSearchInput();
    }
  };

  window.getFiltered = function() {
    let a = (window.isAdmin && window.activeMode === 'pool') ? window.getMappedPoolData() : window.DATA;
    
    // Lọc động: Chỉ hiện căn Public (US-039.7)
    if (window.isAdmin && window.activeMode === 'pool' && window.showOnAirOnly) {
      a = a.filter(p => window.DATA.some(x => {
        if (x.system_id && p.system_id) {
          return String(x.system_id).trim() === String(p.system_id).trim();
        }
        return x.id && p.id && String(x.id).trim() === String(p.id).trim();
      }));
    }
    
    const sv = (document.getElementById('bdsSearchInput')?.value || '').trim();
    if (sv) {
      // Helper to remove accents / diacritics for Vietnamese search
      function removeAccents(str) {
        if (str === null || str === undefined) return '';
        const s = String(str);
        if (!s) return '';
        return s
          .normalize('NFD')
          .replace(/[\u0300-\u036f]/g, '')
          .replace(/đ/g, 'd')
          .replace(/Đ/g, 'D')
          .toLowerCase()
          .trim();
      }

      if (window.isAdmin) {
        // Combined Multi-condition AND Search for Admin
        const subQueries = sv.split('+').map(s => s.trim()).filter(Boolean);
        
        // Helper to normalize street queries (Rule 1 of BDS-AGENTS.md)
        function normalizeStreetQuery(street) {
          let s = removeAccents(street);
          if (!s) return '';
          s = s.replace(/cach\s+mang\s+thang\s+8|cach\s+mang\s+thang\s+tam|cmt8/g, 'ttmc');
          s = s.replace(/ba\s+thang\s+hai|3\/2|3-2|3\s+thang\s+2/g, 'htb');
          s = s.replace(/duong\s+so\s+7/g, '7sd');
          return s;
        }

        // Helper to match Vietnamese complex house numbers
        function matchHouseNumber(rawSoNha, querySoNha) {
          const cleanRaw = String(rawSoNha || '').trim().toLowerCase();
          const cleanQuery = String(querySoNha || '').trim().toLowerCase();
          if (!cleanQuery) return true;
          if (!cleanRaw) return false;
          
          // Rule 2: compound numbers "1168.42+44" -> "1168.42"
          const normalizedRaw = cleanRaw.split('+')[0].trim();
          
          // Tìm tiếp đầu ngữ (prefix matching) cho số nhà
          if (normalizedRaw.startsWith(cleanQuery)) return true;
          
          return false;
        }
        
        a = a.filter(p => {
          return subQueries.every(sub => {
            const subCleaned = removeAccents(sub);
            
            // 1. Match Price query: e.g. "25 tỷ", "25.5 tỷ"
            const priceMatch = sub.match(/^([\d,.]+)\s*tỷ$/i) || sub.match(/([\d,.]+)\s*tỷ/i);
            if (priceMatch) {
              const numStr = priceMatch[1].replace(',', '.');
              const num = parseFloat(numStr);
              const pGia = parseFloat(p.gia) || 0;
              if (numStr.includes('.')) {
                // Decimal price: exact match
                return Math.abs(pGia - num) < 0.001;
              } else {
                // Integer price: prefix match range [num, num+1)
                return pGia >= num && pGia < num + 1;
              }
            }
            
            // 2. Match House Number + Street: starts with a digit
            const houseStreetMatch = sub.match(/^(\d+[\d/a-zA-Z.]*)\s*(.*)$/);
            if (houseStreetMatch) {
              const houseNumQuery = houseStreetMatch[1];
              const streetQuery = houseStreetMatch[2].trim();
              
              let hnMatch = matchHouseNumber(p.raw_so_nha, houseNumQuery);
              if (!hnMatch && p.cu_phap) {
                const cuPhapMatch = p.cu_phap.trim().match(/^(\d+[\d/a-zA-Z.]*)\s*(.*)$/);
                if (cuPhapMatch) {
                  hnMatch = matchHouseNumber(cuPhapMatch[1], houseNumQuery);
                }
              }
              if (!hnMatch) return false;
              
              if (streetQuery) {
                const normStreetQ = normalizeStreetQuery(streetQuery);
                const normRawDuong = normalizeStreetQuery(p.raw_ten_duong);
                const normDuongTruoc = normalizeStreetQuery(p.duong_truoc_nha);
                const normTenDuong = normalizeStreetQuery(p.ten_duong);
                const titleMatch = removeAccents(p.t).includes(removeAccents(streetQuery));
                return normRawDuong.includes(normStreetQ) || normDuongTruoc.includes(normStreetQ) || normTenDuong.includes(normStreetQ) || titleMatch;
              }
              return true;
            }
            
            // 3. Fallback: General text match
            const normSub = normalizeStreetQuery(sub);
            const streetMatch = normalizeStreetQuery(p.raw_ten_duong).includes(normSub) || 
                                normalizeStreetQuery(p.duong_truoc_nha).includes(normSub) ||
                                normalizeStreetQuery(p.ten_duong).includes(normSub);
            const titleMatch = removeAccents(p.t).includes(subCleaned);
            const pMatch = removeAccents(p.phuong).includes(subCleaned);
            const idMatch = removeAccents(p.id).includes(subCleaned);
            const qMatch = removeAccents(p.q).includes(subCleaned) ||
                           removeAccents(p.ql).includes(subCleaned) ||
                           (subCleaned === 'phu nhuan' && p.q === 'pn') ||
                           (subCleaned === 'tan binh' && p.q === 'tb') ||
                           (subCleaned === 'binh thanh' && p.q === 'bt') ||
                           (subCleaned === 'go vap' && p.q === 'gv') ||
                           (subCleaned === 'quan 3' && p.q === 'q3') ||
                           (subCleaned === 'quan 10' && p.q === 'q10');
                           
            const dauChuMatch = removeAccents(p.raw_ten_dau_chu).includes(subCleaned);
            const dtMatch = removeAccents(p.raw_dt_dau_chu).includes(subCleaned);
            const cpMatch = removeAccents(p.cu_phap).includes(subCleaned);
            const soNhaMatch = removeAccents(p.raw_so_nha).includes(subCleaned) || (p.cu_phap && removeAccents(p.cu_phap.split(' ')[0]).includes(subCleaned));
            const duongMatch = removeAccents(p.raw_ten_duong).includes(subCleaned) || removeAccents(p.ten_duong).includes(subCleaned);
            
            return idMatch || titleMatch || streetMatch || pMatch || qMatch ||
                   dauChuMatch || dtMatch || cpMatch || soNhaMatch || duongMatch;
          });
        });
      } else {
        // Regular client search logic with accent-free search support
        const svCleaned = removeAccents(sv);
        a = a.filter(p => {
          const idMatch = removeAccents(p.id).includes(svCleaned);
          const tMatch = removeAccents(p.t).includes(svCleaned);
          const dMatch = removeAccents(p.duong_truoc_nha).includes(svCleaned) || 
                         removeAccents(p.ten_duong).includes(svCleaned) || 
                         removeAccents(p.raw_ten_duong).includes(svCleaned);
          const pMatch = removeAccents(p.phuong).includes(svCleaned);
          const qMatch = removeAccents(p.q).includes(svCleaned) ||
            removeAccents(p.ql).includes(svCleaned) ||
            (svCleaned === 'phu nhuan' && p.q === 'pn') ||
            (svCleaned === 'tan binh' && p.q === 'tb') ||
            (svCleaned === 'binh thanh' && p.q === 'bt') ||
            (svCleaned === 'go vap' && p.q === 'gv') ||
            (svCleaned === 'quan 3' && p.q === 'q3') ||
            (svCleaned === 'quan 10' && p.q === 'q10');
          return idMatch || tMatch || dMatch || pMatch || qMatch;
        });
      }
    }

    // LỌC THEO TIÊU CHÍ BĐS CHECKBOXES (US-076.3)
    const activeCriteria = Array.from(document.querySelectorAll('.filter-criterion:checked')).map(el => el.getAttribute('data-val'));
    if (activeCriteria.length > 0) {
      a = a.filter(p => activeCriteria.every(crit => window.matchCriteriaHelper(p, crit)));
    }

    // LỌC THEO BỘ LỌC ĐỘNG TỰ SINH (US-100)
    if (window.activeDynamicFilters) {
      for (const [field, filterVal] of Object.entries(window.activeDynamicFilters)) {
        if (filterVal) {
          if (filterVal instanceof Set) {
            if (filterVal.size > 0) {
              a = a.filter(p => {
                const jsonUiObj = p.json_ui_parsed || {};
                const valInListing = jsonUiObj[field] || '';
                return filterVal.has(String(valInListing));
              });
            }
          } else {
            a = a.filter(p => {
              const jsonUiObj = p.json_ui_parsed || {};
              const valInListing = jsonUiObj[field] || '';
              return String(valInListing).toLowerCase().includes(String(filterVal).toLowerCase());
            });
          }
        }
      }
    }

    // LỌC THEO BỘ LỌC RANGE THÔNG SỐ CHI TIẾT NÂNG CAO (US-076)
    const giaMin = document.getElementById('filterGiaMin')?.value || '';
    const giaMax = document.getElementById('filterGiaMax')?.value || '';
    const dtTrenSoMin = document.getElementById('filterDtTrenSoMin')?.value || '';
    const dtTrenSoMax = document.getElementById('filterDtTrenSoMax')?.value || '';
    const dtThucTeMin = document.getElementById('filterDtThucTeMin')?.value || '';
    const dtThucTeMax = document.getElementById('filterDtThucTeMax')?.value || '';
    const ngangMin = document.getElementById('filterNgangMin')?.value || '';
    const ngangMax = document.getElementById('filterNgangMax')?.value || '';
    const hemMin = document.getElementById('filterHemMin')?.value || '';
    const hemMax = document.getElementById('filterHemMax')?.value || '';
    const phongMin = document.getElementById('filterPhongMin')?.value || '';
    const phongMax = document.getElementById('filterPhongMax')?.value || '';

    const pFHelper = window.parseFloatHelper || parseFloatHelper;
    const pGiaHelper = window.parseGia || parseGia;

    if (giaMin !== '' || giaMax !== '') {
      console.log('--- Price Filter Debug ---', { giaMin, giaMax, pFMin: pFHelper(giaMin), pFMax: pFHelper(giaMax) });
      a = a.filter(p => {
        let val = parseFloat(p.gia);
        if (isNaN(val) || val === 0) {
          val = pGiaHelper(p.raw_gia_chao) || 0;
        }
        const minVal = pFHelper(giaMin);
        const maxVal = pFHelper(giaMax);
        const res = !((giaMin !== '' && val < minVal) || (giaMax !== '' && val > maxVal));
        console.log(`Checking listing ${p.id}: gia=${p.gia}, val=${val}, minVal=${minVal}, maxVal=${maxVal}, res=${res}`);
        return res;
      });
    }

    if (dtTrenSoMin !== '' || dtTrenSoMax !== '') {
      a = a.filter(p => {
        let val = pFHelper(p.raw_dt_tren_so);
        if (isNaN(val) || val === 0) {
          val = pFHelper(p.dt) || 0;
        }
        if (dtTrenSoMin !== '' && val < pFHelper(dtTrenSoMin)) return false;
        if (dtTrenSoMax !== '' && val > pFHelper(dtTrenSoMax)) return false;
        return true;
      });
    }

    if (dtThucTeMin !== '' || dtThucTeMax !== '') {
      a = a.filter(p => {
        let val = pFHelper(p.raw_dt_thuc_te);
        if (isNaN(val) || val === 0) {
          val = pFHelper(p.dt) || 0;
        }
        if (dtThucTeMin !== '' && val < pFHelper(dtThucTeMin)) return false;
        if (dtThucTeMax !== '' && val > pFHelper(dtThucTeMax)) return false;
        return true;
      });
    }

    if (ngangMin !== '' || ngangMax !== '') {
      a = a.filter(p => {
        let val = pFHelper(p.raw_mat_tien);
        if (isNaN(val) || val === 0) {
          val = pFHelper(p.mat) || 0;
        }
        if (ngangMin !== '' && val < pFHelper(ngangMin)) return false;
        if (ngangMax !== '' && val > pFHelper(ngangMax)) return false;
        return true;
      });
    }

    if (hemMin !== '' || hemMax !== '') {
      a = a.filter(p => {
        let val = pFHelper(p.raw_duong_truoc_nha);
        if (isNaN(val) || val === 0) {
          val = pFHelper(p.rong_hem) || 0;
        }
        if (hemMin !== '' && val < pFHelper(hemMin)) return false;
        if (hemMax !== '' && val > pFHelper(hemMax)) return false;
        return true;
      });
    }

    if (phongMin !== '' || phongMax !== '') {
      a = a.filter(p => {
        let val = parseInt(p.raw_so_pn, 10);
        if (isNaN(val) || val === 0) {
          val = parseInt(p.so_pn, 10) || 0;
        }
        if (phongMin !== '' && val < parseInt(phongMin, 10)) return false;
        if (phongMax !== '' && val > parseInt(phongMax, 10)) return false;
        return true;
      });
    }

    if (window.showFavOnly) a = a.filter(p => window.favs.has(p.system_id ? String(p.system_id) : String(p.id)));
    if (window.selDistricts.size) a = a.filter(p => window.selDistricts.has(p.q));
    if (window.selWards.size) a = a.filter(p => window.selWards.has(p.phuong));
    if (window.selDuongs.size) a = a.filter(p => window.selDuongs.has(p.duong_truoc_nha));
    if (window.selHuong.size) a = a.filter(p => window.selHuong.has(p.huong));
    a = window.applyGia(a);
    if (window.selDanhGia.size) a = a.filter(p => window.selDanhGia.has(p.danh_gia));

    // LỌC THEO BỘ SƯU TẬP HOẶC DANH SÁCH YÊU THÍCH CỦA ADMIN
    if (window.activeCollectionName) {
      if (window.activeCollectionName === 'favorites') {
        a = a.filter(p => window.favs.has(p.system_id ? String(p.system_id) : String(p.id)));
      } else if (window.collections[window.activeCollectionName]) {
        const colIds = new Set(window.collections[window.activeCollectionName].map(String));
        a = a.filter(p => colIds.has(p.system_id ? String(p.system_id) : String(p.id)));
      }
    }
    return a;
  };

  // Helper so khớp tiêu chí thô hoặc keywords fallback (US-076.3)
  window.matchCriteriaHelper = function(p, criterion) {
    const textToSearch = [
      p.t || '',
      p.m || '',
      p.raw_phan_loai || '',
      p.raw_mo_ta_chi_tiet || '',
      p.raw_tieu_de_public || ''
    ].join(' ').toLowerCase();

    const c = criterion.toLowerCase();
    
    if (p.raw_phan_loai && p.raw_phan_loai.toLowerCase().includes(c)) return true;

    if (c === 'chdv') {
      return p.chdv === 'Có' || (p.chdv && String(p.chdv).toLowerCase().includes('có')) || textToSearch.includes('chdv') || textToSearch.includes('căn hộ dịch vụ');
    }

    return textToSearch.includes(c);
  };

  // Tự động dựng checklist chỉ chứa các tiêu chí hiện diện trong dữ liệu thô (US-076.3)
  window.renderCriteriaCheckboxes = function(data) {
    const allPossibleCriteria = [
      "CHDV"
    ];
    
    const grid = document.querySelector('.criteria-grid');
    if (!grid) return;
    grid.innerHTML = '';
    
    // Lọc các tiêu chí có tối thiểu 1 căn trong data thỏa mãn
    const matchedCriteria = allPossibleCriteria.filter(crit => {
      const cLower = crit.toLowerCase();
      return data.some(p => {
        if (p.raw_phan_loai) {
          const tags = p.raw_phan_loai.split(',').map(t => t.trim().toLowerCase());
          if (tags.includes(cLower)) return true;
        }
        return window.matchCriteriaHelper(p, crit);
      });
    });
    
    // Render các checkbox
    matchedCriteria.forEach(crit => {
      const label = document.createElement('label');
      label.className = 'criterion-item';
      label.innerHTML = `
        <input type="checkbox" class="filter-criterion" data-val="${crit}" onchange="window.onSearchInput()">
        <span>${crit}</span>
      `;
      grid.appendChild(label);
    });
    
    // Ẩn phần tiêu chí và vách ngăn nếu không có tiêu chí nào khớp
    const section = document.querySelector('.criteria-section');
    if (section) {
      section.style.display = matchedCriteria.length > 0 ? 'block' : 'none';
    }
    const divider = document.querySelector('.filter-divider');
    if (divider) {
      divider.style.display = matchedCriteria.length > 0 ? 'block' : 'none';
    }
  };

  // Tự động ẩn hiện các bộ lọc giá/đánh giá tĩnh dựa trên dữ liệu hiện có (US-076.3)
  window.updateStaticTabsVisibility = function(data) {
    // 1. Gia tabs
    const hasLt7 = data.some(p => { const g = parseFloat(p.gia) || 0; return g > 0 && g < 7; });
    const has7to10 = data.some(p => { const g = parseFloat(p.gia) || 0; return g >= 7 && g <= 10; });
    const has10to15 = data.some(p => { const g = parseFloat(p.gia) || 0; return g > 10 && g <= 15; });
    const has15to20 = data.some(p => { const g = parseFloat(p.gia) || 0; return g > 15 && g <= 20; });
    const hasGt20 = data.some(p => { const g = parseFloat(p.gia) || 0; return g > 20; });

    const giaTabs = document.getElementById('giaTabs');
    const giaLbl = document.getElementById('giaLbl');
    if (giaTabs) {
      const btnLt7 = giaTabs.querySelector('[data-val="lt7"]');
      const btn7_10 = giaTabs.querySelector('[data-val="7-10"]');
      const btn10_15 = giaTabs.querySelector('[data-val="10-15"]');
      const btn15_20 = giaTabs.querySelector('[data-val="15-20"]');
      const btnGt20 = giaTabs.querySelector('[data-val="gt20"]');

      if (btnLt7) btnLt7.style.display = hasLt7 ? '' : 'none';
      if (btn7_10) btn7_10.style.display = has7to10 ? '' : 'none';
      if (btn10_15) btn10_15.style.display = has10to15 ? '' : 'none';
      if (btn15_20) btn15_20.style.display = has15to20 ? '' : 'none';
      if (btnGt20) btnGt20.style.display = hasGt20 ? '' : 'none';

      const hasAnyPriceOption = hasLt7 || has7to10 || has10to15 || has15to20 || hasGt20;
      if (giaLbl) giaLbl.style.display = hasAnyPriceOption ? '' : 'none';
      giaTabs.style.display = hasAnyPriceOption ? 'flex' : 'none';
    }

    // 2. Danh gia tabs
    const hasNgon = data.some(p => p.danh_gia === 'Hàng Ngon');
    const hasLoi = data.some(p => p.danh_gia === 'Hàng Lỗi');

    const danhGiaTabs = document.getElementById('danhGiaTabs');
    const danhGiaLbl = document.getElementById('danhGiaLbl');
    if (danhGiaTabs) {
      const btnNgon = danhGiaTabs.querySelector('[data-val="Hàng Ngon"]');
      const btnLoi = danhGiaTabs.querySelector('[data-val="Hàng Lỗi"]');

      if (btnNgon) btnNgon.style.display = hasNgon ? '' : 'none';
      if (btnLoi) btnLoi.style.display = hasLoi ? '' : 'none';

      const hasAnyRatingOption = hasNgon || hasLoi;
      if (danhGiaLbl) danhGiaLbl.style.display = hasAnyRatingOption ? '' : 'none';
      danhGiaTabs.style.display = hasAnyRatingOption ? 'flex' : 'none';
    }
  };

  // ── Filter panel toggle ──
  window.toggleFilter = function() {
    window.filterOpen = !window.filterOpen;
    document.getElementById('filterPanel').classList.toggle('open', window.filterOpen);
    const btn = document.getElementById('filterBtn');
    btn.classList.toggle('active', window.filterOpen);
    if (window.innerWidth < 768) {
      document.documentElement.classList.toggle('filter-active', window.filterOpen);
      document.body.classList.toggle('filter-active', window.filterOpen);
    }
  };

  window.closeFilter = function() {
    if (!window.filterOpen) return;
    window.filterOpen = false;
    document.getElementById('filterPanel').classList.remove('open');
    const btn = document.getElementById('filterBtn');
    const anyActive = !!(window.selDistricts.size || window.selWards.size || window.selDuongs.size || window.selHuong.size || window.selGia.size || window.selDanhGia.size || document.querySelectorAll('.filter-criterion:checked').length);
    btn.classList.toggle('active', anyActive);
    if (window.innerWidth < 768) {
      document.documentElement.classList.remove('filter-active');
      document.body.classList.remove('filter-active');
    }
  };

  // ── Build district tabs dynamically ──
  window.buildDistrictTabs = function() {
    const districtsInPool = [...new Set(window.DATA.map(p => p.q).filter(Boolean))];
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

    const container = document.getElementById('districtOptions');
    const box = document.getElementById('districtMulti');
    const lbl = document.getElementById('districtLbl');
    if (!container || !box) return;

    if (districtsInPool.length === 0) {
      if (lbl) lbl.style.display = 'none';
      box.style.display = 'none';
    } else {
      if (lbl) lbl.style.display = '';
      box.style.display = 'block';
      
      container.innerHTML = districtsInPool.map(d => {
        const name = dNamesFull[d] || d.toUpperCase();
        const checked = window.selDistricts.has(d) ? 'checked' : '';
        return `
          <div class="multiselect-option" onclick="window.toggleOption('district', '${d}', event)">
            <input type="checkbox" value="${d}" ${checked} onclick="event.stopPropagation()" onchange="window.updateSelectionFromCheckboxes('district')">
            <span>${name}</span>
          </div>
        `;
      }).join('');
      
      window.updateMultiselectPlaceholder('district');
    }
  };

  // ── Build ward tabs dynamically ──
  const WARD_PRIORITY = [
    "Xuân Hoà", "Xuân Hòa",
    "Bàn Cờ",
    "Nhiêu Lộc",
    "Cầu Kiệu",
    "Đức Nhuận",
    "Phú Nhuận",
    "Vườn Lài",
    "Hoà Hưng", "Hòa Hưng",
    "Diên Hồng",
    "Gia Định",
    "Bình Thạnh",
    "Bình Lợi Trung",
    "Thạnh Mỹ Tây",
    "Bình Quới",
    "Tân Sơn Hòa",
    "Tân Sơn Nhất",
    "Tân Bình",
    "Bảy Hiền",
    "Tân Hòa"
  ];

  function normalizeVietnameseTones(str) {
    if (!str) return '';
    return str.normalize('NFC')
      .replace(/o\u0300/g, 'ò').replace(/o\u0301/g, 'ó').replace(/o\u0309/g, 'ỏ').replace(/o\u0303/g, 'õ').replace(/o\u0323/g, 'ọ')
      .replace(/a\u0300/g, 'à').replace(/a\u0301/g, 'á').replace(/a\u0309/g, 'ả').replace(/a\u0303/g, 'ã').replace(/a\u0323/g, 'ạ')
      .replace(/o\u0302\u0300/g, 'ồ').replace(/o\u0302\u0301/g, 'ố').replace(/o\u0302\u0309/g, 'ổ').replace(/o\u0302\u0303/g, 'ỗ').replace(/o\u0302\u0323/g, 'ộ')
      .replace(/a\u0302\u0300/g, 'ầ').replace(/a\u0302\u0301/g, 'ấ').replace(/a\u0302\u0309/g, 'ẩ').replace(/a\u0302\u0303/g, 'ẫ').replace(/a\u0302\u0323/g, 'ậ')
      .replace(/e\u0302\u0300/g, 'ề').replace(/e\u0302\u0301/g, 'ế').replace(/e\u0302\u0309/g, 'ể').replace(/e\u0302\u0303/g, 'ễ').replace(/e\u0302\u0323/g, 'ệ')
      .replace(/oà/g, 'òa').replace(/oá/g, 'óa').replace(/oả/g, 'ỏa').replace(/oã/g, 'õa').replace(/oạ/g, 'ọa')
      .replace(/uý/g, 'úy').replace(/uỳ/g, 'ùy').replace(/uỷ/g, 'ủy').replace(/uỹ/g, 'ũy').replace(/uỵ/g, 'ụy')
      .replace(/oè/g, 'òe').replace(/oé/g, 'óe').replace(/oẻ/g, 'ỏe').replace(/oẽ/g, 'õe').replace(/oẹ/g, 'ọe')
      .replace(/uâ\u0300/g, 'uầ').replace(/uâ\u0301/g, 'uấ').replace(/uâ\u0309/g, 'uẩ').replace(/uâ\u0303/g, 'uẫ').replace(/uâ\u0323/g, 'uậ')
      .trim().toLowerCase();
  }

  function sortWardsByPriority(wardList) {
    const priorityMap = {};
    WARD_PRIORITY.forEach((w, idx) => {
      priorityMap[normalizeVietnameseTones(w)] = idx;
    });

    return wardList.sort((a, b) => {
      const normA = normalizeVietnameseTones(a);
      const normB = normalizeVietnameseTones(b);
      const idxA = priorityMap[normA] !== undefined ? priorityMap[normA] : 9999;
      const idxB = priorityMap[normB] !== undefined ? priorityMap[normB] : 9999;
      
      if (idxA !== idxB) {
        return idxA - idxB;
      }
      return a.localeCompare(b, 'vi');
    });
  }

  const STATIC_WARD_MAP = {
    q3: ["Xuân Hòa", "Bàn Cờ", "Nhiêu Lộc"],
    q10: ["Vườn Lài", "Hòa Hưng", "Diên Hồng"],
    bt: ["Gia Định", "Bình Thạnh", "Bình Lợi Trung", "Thạnh Mỹ Tây", "Bình Quới"],
    tb: ["Tân Sơn Hòa", "Tân Sơn Nhất", "Tân Bình", "Bảy Hiền", "Tân Hòa"],
    pn: ["Cầu Kiệu", "Đức Nhuận", "Phú Nhuận"]
  };

  window.buildWardTabs = function() {
    if (!window.isAdmin) return;
    let wards = [];
    
    if (window.selDistricts.size === 0) {
      const staticWards = [];
      ['q3', 'pn', 'q10', 'bt', 'tb'].forEach(d => {
        if (STATIC_WARD_MAP[d]) staticWards.push(...STATIC_WARD_MAP[d]);
      });
      const dataWards = [...new Set(window.DATA.map(p => p.phuong).filter(w => w && w !== '-' && w !== 'phuong'))];
      const combined = [...new Set([...staticWards, ...dataWards])];
      wards = sortWardsByPriority(combined);
    } else {
      const staticWards = [];
      for (const d of window.selDistricts) {
        if (STATIC_WARD_MAP[d]) {
          staticWards.push(...STATIC_WARD_MAP[d]);
        }
      }
      const pool = window.DATA.filter(p => window.selDistricts.has(p.q));
      const dataWards = [...new Set(pool.map(p => p.phuong).filter(w => w && w !== '-' && w !== 'phuong'))];
      const combined = [...new Set([...staticWards, ...dataWards])];
      wards = sortWardsByPriority(combined);
    }
    const container = document.getElementById('wardOptions');
    const box = document.getElementById('wardMulti');
    const wl = document.getElementById('wardLbl');
    if (!container || !box) return;

    if (!wards.length) { 
      box.classList.remove('has-wards'); 
      box.style.display = 'none';
      if (wl) wl.style.display = 'none'; 
      return; 
    }
    if (wl) wl.style.display = 'block';
    box.classList.add('has-wards');
    box.style.display = '';

    container.innerHTML = wards.map(w => {
      const checked = window.selWards.has(w) ? 'checked' : '';
      return `
        <div class="multiselect-option" onclick="window.toggleOption('ward', '${w}', event)">
          <input type="checkbox" value="${w}" ${checked} onclick="event.stopPropagation()" onchange="window.updateSelectionFromCheckboxes('ward')">
          <span>${w}</span>
        </div>
      `;
    }).join('');
    
    window.updateMultiselectPlaceholder('ward');
  };

  // ── Build duong tabs dynamically ──
  window.buildDuongTabs = function() {
    if (!window.isAdmin) return;
    const duongs = ["Hẻm ba gác", "Hẻm ô tô lý thuyết", "Hẻm ô tô", "Mặt tiền đường"];
    const container = document.getElementById('duongOptions');
    const box = document.getElementById('duongMulti');
    const dl = document.getElementById('duongLbl');
    if (!container || !box) return;

    if (dl) dl.style.display = 'block';
    box.classList.add('has-duong');
    box.style.display = '';

    container.innerHTML = duongs.map(d => {
      const checked = window.selDuongs.has(d) ? 'checked' : '';
      return `
        <div class="multiselect-option" onclick="window.toggleOption('duong', '${d}', event)">
          <input type="checkbox" value="${d}" ${checked} onclick="event.stopPropagation()" onchange="window.updateSelectionFromCheckboxes('duong')">
          <span>${d}</span>
        </div>
      `;
    }).join('');
    
    window.updateMultiselectPlaceholder('duong');
  };

  // ── Build huong (direction) tabs dynamically ──
  window.buildHuongTabs = function() {
    if (!window.isAdmin) return;
    let pool = window.selDistricts.size ? window.DATA.filter(p => window.selDistricts.has(p.q)) : window.DATA;
    if (window.selWards.size) pool = pool.filter(p => window.selWards.has(p.phuong));
    const huongs = [...new Set(pool.map(p => p.huong).filter(h => h && h !== '-'))].sort();
    const container = document.getElementById('huongOptions');
    const box = document.getElementById('huongMulti');
    const hl = document.getElementById('huongLbl');
    if (!container || !box) return;

    if (!huongs.length) { 
      box.classList.remove('has-huong'); 
      box.style.display = 'none';
      if (hl) hl.style.display = 'none'; 
      return; 
    }
    if (hl) hl.style.display = 'block';
    box.classList.add('has-huong');
    box.style.display = '';

    container.innerHTML = huongs.map(h => {
      const checked = window.selHuong.has(h) ? 'checked' : '';
      return `
        <div class="multiselect-option" onclick="window.toggleOption('huong', '${h}', event)">
          <input type="checkbox" value="${h}" ${checked} onclick="event.stopPropagation()" onchange="window.updateSelectionFromCheckboxes('huong')">
          <span>${h}</span>
        </div>
      `;
    }).join('');
    
    window.updateMultiselectPlaceholder('huong');
  };

  // ── Toggle functions (multi-select) ──
  window.tGia = function(val) {
    window.tSel(window.selGia, val); window.syncTabUI('giaTabs', window.selGia);
    window.updateFilterSummary(); if (typeof window.updateStats === 'function') window.updateStats(); window.applyFilter();
  };
  window.tDanhGia = function(val) {
    window.tSel(window.selDanhGia, val); window.syncTabUI('danhGiaTabs', window.selDanhGia);
    window.updateFilterSummary(); if (typeof window.updateStats === 'function') window.updateStats(); window.applyFilter();
  };

  window.updateFilterSummary = function() {
    const dNames = {
      q1: 'Q.1', q2: 'Q.2', q3: 'Q.3', q4: 'Q.4', q5: 'Q.5', q6: 'Q.6',
      q7: 'Q.7', q8: 'Q.8', q9: 'Q.9', q10: 'Q.10', q11: 'Q.11', q12: 'Q.12',
      pn: 'P.Nhuận', tb: 'T.Bình', bt: 'B.Thạnh', gv: 'G.Vấp',
      tp: 'T.Phú', btan: 'B.Tân', td: 'T.Đức',
      hm: 'H.Môn', nb: 'N.Bè', bc: 'B.Chánh', cc: 'C.Chi', cg: 'C.Giờ'
    };
    const gNames = { 'lt7': '<7t', '7-10': '7-10t', '10-15': '10-15t', '15-20': '15-20t', 'gt20': '>20t' };
    const parts = [];
    if (window.selDistricts.size) parts.push([...window.selDistricts].map(d => dNames[d] || d).join('+'));
    if (window.selWards.size) parts.push('P.' + [...window.selWards].join('+'));
    if (window.selDuongs.size) parts.push([...window.selDuongs].join('+'));
    if (window.selHuong.size) parts.push('🧭' + [...window.selHuong].join('+'));
    if (window.selGia.size) parts.push([...window.selGia].map(g => gNames[g] || g).join('+'));
    if (window.selDanhGia.size) parts.push([...window.selDanhGia].map(d => d === 'Hàng Ngon' ? '💎' : '⚠️').join(''));
    
    if (window.activeDynamicFilters) {
      for (const [field, val] of Object.entries(window.activeDynamicFilters)) {
        if (val) {
          if (val instanceof Set) {
            if (val.size > 0) {
              parts.push([...val].join('+'));
            }
          } else {
            parts.push(val);
          }
        }
      }
    }

    if (window.activeCollectionName) {
      const colDisplayName = window.activeCollectionName === 'favorites' ? 'Yêu thích' : window.activeCollectionName;
      parts.push(`📁 BST: ${colDisplayName}`);
    }

    const activeCriteria = Array.from(document.querySelectorAll('.filter-criterion:checked')).map(el => el.getAttribute('data-val'));
    if (activeCriteria.length > 0) {
      parts.push(`🏷️ Tiêu chí: ${activeCriteria.join('+')}`);
    }
    
    document.getElementById('filterSummary').textContent = parts.length ? parts.join(' · ') : 'Tất cả';
    const anyDynamicActive = Object.values(window.activeDynamicFilters || {}).some(val => {
      if (val instanceof Set) return val.size > 0;
      return !!val;
    });
    const anyActive = !!(
      window.selDistricts.size || 
      window.selWards.size || 
      window.selDuongs.size || 
      window.selHuong.size || 
      window.selGia.size || 
      window.selDanhGia.size || 
      anyDynamicActive ||
      window.activeCollectionName ||
      activeCriteria.length ||
      window.showFavOnly
    );
    document.getElementById('filterBtn').classList.toggle('active', anyActive || window.filterOpen);
    document.getElementById('resetBtn').style.display = anyActive ? 'inline-flex' : 'none';

    // Hiển thị dòng thứ 2 (bộ lọc hiện tại) chỉ khi có filter hoạt động
    const bar = document.getElementById('filterBar');
    if (bar) {
      bar.style.display = (window.isAdmin && anyActive) ? 'flex' : 'none';
    }

    if (typeof window.saveState === 'function') window.saveState();
  };

  window.resetFilters = function() {
    window.selDistricts.clear(); window.selWards.clear(); window.selDuongs.clear(); window.selHuong.clear(); window.selGia.clear(); window.selDanhGia.clear();
    window.buildDistrictTabs();
    window.syncTabUI('giaTabs', window.selGia);
    window.syncTabUI('danhGiaTabs', window.selDanhGia);

    // Xóa bộ sưu tập và yêu thích ẩn
    window.activeCollectionName = null;
    localStorage.removeItem('activeCollectionName');
    window.showFavOnly = false;
    if (typeof window.updateFavBtnUI === 'function') window.updateFavBtnUI();
    const activeColBar = document.getElementById('activeColBar');
    if (activeColBar) activeColBar.style.display = 'none';

    // Xóa ô tìm kiếm
    const sInput = document.getElementById('bdsSearchInput');
    if (sInput) sInput.value = '';
    window.toggleSearchClearBtn();

    // Xóa các ô lọc thông số chi tiết nâng cao
    const advInputs = [
      'filterGiaMin', 'filterGiaMax',
      'filterDtTrenSoMin', 'filterDtTrenSoMax',
      'filterDtThucTeMin', 'filterDtThucTeMax',
      'filterNgangMin', 'filterNgangMax',
      'filterHemMin', 'filterHemMax',
      'filterPhongMin', 'filterPhongMax'
    ];
    advInputs.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '';
    });

    // Xóa các tiêu chí checkbox BĐS
    document.querySelectorAll('.filter-criterion').forEach(el => el.checked = false);

    // Xóa các bộ lọc động
    window.activeDynamicFilters = {};
    document.querySelectorAll('.dynamic-filter-select').forEach(sel => {
      sel.value = "";
    });
    document.querySelectorAll('.multiselect-container[id^="dynamic_multi_"]').forEach(container => {
      container.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
      const placeholder = container.querySelector('.multiselect-placeholder');
      if (placeholder) {
        placeholder.textContent = 'Tất cả';
        placeholder.style.color = 'rgba(44, 44, 46, 0.5)';
      }
    });

    // Ward, Duong & Huong tabs cần rebuild vì là dynamic
    window.buildWardTabs(); window.buildDuongTabs(); window.buildHuongTabs();
    window.updateFilterSummary(); if (typeof window.updateStats === 'function') window.updateStats(); window.applyFilter();
  };

  window.clearAllFilters = function() {
    window.resetFilters();
    if (typeof window.saveState === 'function') window.saveState();
  };

  window.toggleFavFilter = function() {
    if (!window.isAdmin) {
      window.showFavOnly = !window.showFavOnly;
      if (typeof window.updateFavBtnUI === 'function') window.updateFavBtnUI();
      if (typeof window.saveState === 'function') window.saveState();
      if (typeof window.updateStats === 'function') window.updateStats(); window.applyFilter();
    } else {
      if (typeof window.openColViewModal === 'function') window.openColViewModal();
    }
  };

  // Lọc bằng cách tạo lại DOM để giải quyết triệt để giới hạn hiển thị 200 căn trong Kho Pool
  let inApplyFilter = false;
  window.applyFilter = function() {
    if (inApplyFilter) {
      const cards = document.querySelectorAll('#list .card');
      const visibleCount = cards.length;
      
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

      // US-039.3: Smart Pool Fallback khi không có kết quả
      window.checkPoolFallbackSearch(visibleCount);
      if (typeof window.updateShareUI === 'function') window.updateShareUI();
      return;
    }

    inApplyFilter = true;
    try {
      if (typeof window.render === 'function') window.render();
    } finally {
      inApplyFilter = false;
    }
  };

  window.checkPoolFallbackSearch = function(visibleCount) {
    const fallbackContainer = document.getElementById('poolFallbackArea');
    if (fallbackContainer) fallbackContainer.remove();
    
    if (!window.isAdmin || window.activeMode === 'pool' || visibleCount > 0) return;
    
    const searchVal = (document.getElementById('bdsSearchInput')?.value || '').trim();
    
    if (!searchVal) return;
    
    const list = document.getElementById('list');
    const d = document.createElement('div');
    d.id = 'poolFallbackArea';
    d.style.cssText = 'grid-column: 1 / -1; text-align: center; padding: 24px; background: rgba(255, 191, 36, 0.06); border: 1.5px dashed var(--gold); border-radius: 16px; margin: 15px 0; color: #fff;';
    
    d.innerHTML = `
      <div style="font-size: 14px; font-weight: 800; margin-bottom: 6px; color: var(--gold); text-transform: uppercase; letter-spacing: 0.5px;">🔍 KHÔNG CÓ KẾT QUẢ TRÊN SÓNG</div>
      <div style="font-size: 12.5px; color: rgba(255,255,255,0.75); margin-bottom: 16px; line-height: 1.45;">
        Không tìm thấy căn nào đã lên sóng khớp với từ khóa <b>"${searchVal}"</b>.<br>Bạn có muốn quét và tìm kiếm trong kho <b>Pool thô</b> không?
      </div>
      <button onclick="executePoolFallbackSearch('${searchVal.replace(/'/g, "\\'")}')" 
        style="background: var(--gold); color: #1c1c1e; border: none; padding: 10px 18px; border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer; font-family: inherit; transition: transform 0.2s;">
        ⚡ QUÉT TRONG POOL THÔ
      </button>
      <div id="poolFallbackResults" style="margin-top: 20px; display: flex; flex-direction: column; gap: 8px; text-align: left;"></div>
    `;
    list.appendChild(d);
  };

  window.searchPoolRows = function(query) {
    if (!query || !window.POOL_ROWS.length) return [];
    const q = query.toLowerCase().trim();
    return window.POOL_ROWS.filter(row => {
      const soNha = String(row[6] || '').toLowerCase();
      const duong = String(row[5] || '').toLowerCase();
      const ma = String(row[55] || '').toLowerCase();
      const dauChu = String(row[75] || '').toLowerCase();
      const sdt = String(row[74] || '').toLowerCase();
      const ndChinh = String(row[9] || '').toLowerCase();
      
      return soNha.includes(q) || duong.includes(q) || ma.includes(q) || dauChu.includes(q) || sdt.includes(q) || ndChinh.includes(q);
    });
  };

  window.toggleShowOnAirOnly = function(isChecked) {
    if (!window.isAdmin) return;
    window.showOnAirOnly = isChecked;
    if (typeof window.updateStats === 'function') window.updateStats();
    window.applyFilter();
    if (typeof window.saveState === 'function') window.saveState();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // ── Dynamic Filters Configuration Loading & Rendering (US-100) ──
  window.JSON_UI_CONFIG = null;
  window.activeDynamicFilters = {};

  window.loadDynamicFiltersConfig = async function() {
    try {
      const res = await fetch('/api/config');
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'success') {
          window.JSON_UI_CONFIG = data.config;
          window.renderDynamicFilters();
        }
      }
    } catch (e) {
      console.warn("Failed to load dynamic filters configuration from /api/config:", e);
    }
  };

  window.renderDynamicFilters = function() {
    const container = document.getElementById('dynamicFiltersContainer');
    if (!container) return;
    container.innerHTML = '';
    
    if (!window.JSON_UI_CONFIG || !window.JSON_UI_CONFIG.json_ui_filters) return;
    
    window.JSON_UI_CONFIG.json_ui_filters.forEach(filter => {
      const field = filter.field;
      const label = filter.label;
      const type = filter.type;
      
      const lbl = document.createElement('div');
      lbl.className = 'filter-section-lbl';
      lbl.textContent = label;
      lbl.id = `lbl_${field}`;
      container.appendChild(lbl);
      
      if (type === 'select') {
        const select = document.createElement('select');
        select.id = `filter_${field}`;
        select.className = 'dynamic-filter-select';
        select.style.cssText = `
          width: 100%;
          box-sizing: border-box;
          padding: 10px 12px;
          border: 1.5px solid #e2ded6;
          border-radius: 8px;
          background: #ffffff;
          color: #3a3a3c;
          font-family: inherit;
          font-size: 13.5px;
          font-weight: 600;
          outline: none;
          margin-bottom: 12px;
          appearance: none;
          background-image: url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%233a3a3c' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
          background-repeat: no-repeat;
          background-position: right 12px center;
          background-size: 14px;
          padding-right: 32px;
        `;
        
        select.onchange = function() {
          window.activeDynamicFilters[field] = select.value;
          window.updateFilterSummary();
          if (typeof window.updateStats === 'function') window.updateStats();
          window.applyFilter();
        };
        
        const options = filter.options || [];
        options.forEach(opt => {
          const optionEl = document.createElement('option');
          optionEl.value = opt;
          optionEl.textContent = opt === "" ? "Tất cả" : opt;
          if (window.activeDynamicFilters[field] === opt) {
            optionEl.selected = true;
          }
          select.appendChild(optionEl);
        });
        
        container.appendChild(select);
      } else if (type === 'multiselect') {
        const multiselectDiv = document.createElement('div');
        multiselectDiv.id = `dynamic_multi_${field}`;
        multiselectDiv.className = 'multiselect-container';
        
        const trigger = document.createElement('div');
        trigger.className = 'multiselect-trigger';
        trigger.onclick = function(e) {
          e.stopPropagation();
          window.toggleMultiselect(multiselectDiv.id);
        };
        
        const placeholder = document.createElement('span');
        placeholder.id = `dynamic_placeholder_${field}`;
        placeholder.className = 'multiselect-placeholder';
        placeholder.textContent = 'Tất cả';
        placeholder.style.color = 'rgba(44, 44, 46, 0.5)';
        
        const arrowSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        arrowSvg.setAttribute('class', 'multiselect-arrow');
        arrowSvg.setAttribute('viewBox', '0 0 24 24');
        arrowSvg.innerHTML = `<polyline points="6 9 12 15 18 9" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`;
        
        trigger.appendChild(placeholder);
        trigger.appendChild(arrowSvg);
        
        const optionsDiv = document.createElement('div');
        optionsDiv.id = `dynamic_options_${field}`;
        optionsDiv.className = 'multiselect-options';
        
        const selectedSet = window.activeDynamicFilters[field] || new Set();
        
        const options = filter.options || [];
        options.forEach(opt => {
          const optionEl = document.createElement('div');
          optionEl.className = 'multiselect-option';
          optionEl.onclick = function(e) {
            e.stopPropagation();
            const checkbox = optionEl.querySelector('input[type="checkbox"]');
            if (checkbox) {
              checkbox.checked = !checkbox.checked;
              window.updateDynamicSelectionFromCheckboxes(field);
            }
          };
          
          const checkbox = document.createElement('input');
          checkbox.type = 'checkbox';
          checkbox.value = opt;
          if (selectedSet instanceof Set && selectedSet.has(opt)) {
            checkbox.checked = true;
          }
          checkbox.onclick = function(e) {
            e.stopPropagation();
          };
          checkbox.onchange = function() {
            window.updateDynamicSelectionFromCheckboxes(field);
          };
          
          const span = document.createElement('span');
          span.textContent = opt;
          
          optionEl.appendChild(checkbox);
          optionEl.appendChild(span);
          optionsDiv.appendChild(optionEl);
        });
        
        if (selectedSet instanceof Set && selectedSet.size > 0) {
          placeholder.textContent = [...selectedSet].join(', ');
          placeholder.style.color = '#2c2c2e';
        }
        
        multiselectDiv.appendChild(trigger);
        multiselectDiv.appendChild(optionsDiv);
        container.appendChild(multiselectDiv);
      }
    });
  };

  window.updateDynamicSelectionFromCheckboxes = function(field) {
    const optionsDiv = document.getElementById(`dynamic_options_${field}`);
    if (!optionsDiv) return;
    
    if (!window.activeDynamicFilters[field] || !(window.activeDynamicFilters[field] instanceof Set)) {
      window.activeDynamicFilters[field] = new Set();
    }
    
    const selectedSet = window.activeDynamicFilters[field];
    selectedSet.clear();
    
    optionsDiv.querySelectorAll('input[type="checkbox"]:checked').forEach(cb => {
      selectedSet.add(cb.value);
    });
    
    // Update placeholder
    const placeholder = document.getElementById(`dynamic_placeholder_${field}`);
    if (placeholder) {
      if (selectedSet.size === 0) {
        placeholder.textContent = 'Tất cả';
        placeholder.style.color = 'rgba(44, 44, 46, 0.5)';
      } else {
        placeholder.textContent = [...selectedSet].join(', ');
        placeholder.style.color = '#2c2c2e';
      }
    }
    
    window.updateFilterSummary();
    if (typeof window.updateStats === 'function') window.updateStats();
    window.applyFilter();
  };

  // Auto load config on script load
  window.loadDynamicFiltersConfig();

})();
