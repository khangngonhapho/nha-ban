(function () {
  'use strict';

  // Initialize global states on window
  window.favs = window.favs || new Set(JSON.parse(localStorage.getItem('favs') || '[]'));
  window.SELECTED_IDS = window.SELECTED_IDS || new Set();
  window.activeCollectionName = window.activeCollectionName || null;
  
  if (!window.collections) {
    window.collections = {};
    try {
      window.collections = JSON.parse(localStorage.getItem('adminCollections') || '{}');
      if (typeof window.collections !== 'object' || window.collections === null) {
        window.collections = {};
      }
    } catch (e) {
      console.error("Error loading collections:", e);
      window.collections = {};
    }
  }

  const SELECTED_IDS = window.SELECTED_IDS;
  const favs = window.favs;

  function showNotify(msg, type = 'success') {
    if (typeof window.showToast === 'function') {
      window.showToast(msg, type);
    } else {
      alert(msg);
    }
  }

  function updateFavBtnUI() {
    const btn = document.getElementById('favFilterBtn');
    const badge = document.getElementById('favCount');
    if (!btn || !badge) return;
    const showFavOnly = window.showFavOnly;
    btn.classList.toggle('active', showFavOnly);
    btn.innerHTML = showFavOnly ? '♥' : '♡';
    if (favs.size > 0) {
      badge.textContent = favs.size;
      badge.style.display = 'flex';
    } else {
      badge.style.display = 'none';
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
    if (window.showFavOnly) {
      if (typeof window.updateStats === 'function') window.updateStats();
      if (typeof window.render === 'function') window.render();
    }
  }

  function updateShareUI() {
    const shareCountEl = document.getElementById('shareCount');
    if (shareCountEl) shareCountEl.textContent = SELECTED_IDS.size;
    
    const colFloatBtn = document.getElementById('colFloatBtn');
    if (colFloatBtn) {
      colFloatBtn.style.display = SELECTED_IDS.size > 0 ? 'flex' : 'none';
    }

    const btn = document.getElementById('selAllBtn');
    if (btn) {
      const visibleCards = Array.from(document.querySelectorAll('#list .card')).filter(c => c && c.style.display !== 'none');
      const visibleIds = visibleCards.map(c => c.dataset.pid);
      const isNowAllSelected = visibleIds.length > 0 && visibleIds.every(id => SELECTED_IDS.has(id));
      btn.textContent = isNowAllSelected ? '☑' : '☐';
      btn.classList.toggle('all-on', isNowAllSelected);
    }
  }

  function openColViewModal() {
    try {
      const viewList = document.getElementById('colViewList');
      if (!viewList) return;
      viewList.innerHTML = '';
      
      const favCount = favs.size;
      const favItem = document.createElement('div');
      favItem.style.cssText = 'display:flex; align-items:center; gap:12px; padding:12px 16px; background:rgba(0,0,0,0.03); border:1px solid rgba(0,0,0,0.08); border-radius:10px; cursor:pointer; transition:background 0.2s;';
      
      const favCb = document.createElement('input');
      favCb.type = 'checkbox';
      favCb.disabled = true;
      favCb.style.cssText = 'width:24px; height:24px; cursor:not-allowed; margin:0; flex-shrink:0; opacity:0.3;';
      
      const favInfo = document.createElement('div');
      favInfo.style.cssText = 'display:flex; align-items:center; gap:8px; flex:1;';
      favInfo.innerHTML = `
        <span style="font-size:16px;">❤️</span>
        <span style="font-weight:600; font-size:14px; color:var(--text);">Căn nhà đã thích</span>
        <span style="font-size:12px; color:var(--sub);">(${favCount} căn)</span>
      `;
      favInfo.onclick = () => {
        viewCollection('favorites');
        closeColViewModal();
      };
      
      favItem.appendChild(favCb);
      favItem.appendChild(favInfo);
      viewList.appendChild(favItem);
      
      if (typeof window.collections !== 'object' || window.collections === null) {
        window.collections = {};
      }
      Object.keys(window.collections).forEach(name => {
        const val = window.collections[name];
        if (!Array.isArray(val)) return;
        const count = val.length;
        const item = document.createElement('div');
        item.style.cssText = 'display:flex; align-items:center; gap:12px; padding:12px 16px; background:rgba(0,0,0,0.03); border:1px solid rgba(0,0,0,0.08); border-radius:10px; cursor:pointer; transition:background 0.2s; margin-top:8px;';
        
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.className = 'col-delete-checkbox';
        cb.dataset.colname = name;
        cb.style.cssText = 'width:24px; height:24px; cursor:pointer; margin:0; flex-shrink:0;';
        cb.onclick = (e) => {
          if (e) e.stopPropagation();
        };
        
        item.onclick = () => {
          cb.checked = !cb.checked;
        };
        
        const infoDiv = document.createElement('div');
        infoDiv.style.cssText = 'display:flex; align-items:center; gap:8px; flex:1;';
        infoDiv.innerHTML = `
          <span style="font-size:16px;">📁</span>
          <span style="font-weight:600; font-size:14px; color:var(--text); word-break:break-all;">${name}</span>
          <span style="font-size:12px; color:var(--sub);">(${count} căn)</span>
        `;
        infoDiv.onclick = (e) => {
          if (e) e.stopPropagation();
          viewCollection(name);
          closeColViewModal();
        };
        
        item.appendChild(cb);
        item.appendChild(infoDiv);
        viewList.appendChild(item);
      });
      
      document.getElementById('colViewModal').classList.add('open');
      
      if (typeof window.renderSpeedDialActions === 'function') {
        window.renderSpeedDialActions('colView');
      }
      const dialActions = document.getElementById('dialActions');
      const mainBtn = document.getElementById('dialMainBtn');
      if (dialActions && mainBtn) {
        dialActions.classList.add('open');
        mainBtn.classList.add('active');
      }
    } catch (err) {
      showNotify(`❌ Lỗi hiển thị danh sách bộ sưu tập: ${err.message}`, 'error');
      console.error(err);
    }
  }

  function openColSaveModal() {
    console.log("DEBUG JS: openColSaveModal called, SELECTED_IDS size =", SELECTED_IDS.size);
    try {
      if (SELECTED_IDS.size === 0) {
        showNotify('Vui lòng chọn ít nhất 1 căn nhà!', 'warning');
        return;
      }
      
      document.getElementById('colSaveModalCount').textContent = SELECTED_IDS.size;
      document.getElementById('newColName').value = '';
      
      const saveList = document.getElementById('colSaveList');
      if (!saveList) return;
      saveList.innerHTML = '';
      
      if (typeof window.collections !== 'object' || window.collections === null) {
        window.collections = {};
      }
      const colNames = Object.keys(window.collections);
      if (colNames.length === 0) {
        saveList.innerHTML = '<div style="text-align:center; padding:12px; font-size:13px; color:var(--sub);">Chưa có bộ sưu tập nào. Hãy tạo bộ sưu tập đầu tiên ở trên nhé!</div>';
      } else {
        colNames.forEach(name => {
          const val = window.collections[name];
          if (!Array.isArray(val)) return;
          const count = val.length;
          const btn = document.createElement('button');
          btn.style.cssText = 'width:100%; text-align:left; padding:12px 16px; background:rgba(0,0,0,0.03); border:1px solid rgba(0,0,0,0.08); border-radius:8px; color:#1c1c1e; font-weight:600; font-size:13px; cursor:pointer; font-family:inherit; transition:background 0.2s; margin-bottom:8px;';
          btn.innerHTML = `📁 ${name} <span style="font-size:11px; color:var(--sub); font-weight:normal;">(${count} căn)</span>`;
          btn.onclick = () => {
            saveToExistingCollection(name);
            document.getElementById('colSaveModal').classList.remove('open');
          };
          saveList.appendChild(btn);
        });
      }
      
      document.getElementById('colSaveModal').classList.add('open');
    } catch (err) {
      showNotify(`❌ Lỗi mở form lưu: ${err.message}`, 'error');
      console.error(err);
    }
  }

  function createNewCollection(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    try {
      const name = document.getElementById('newColName').value.trim();
      if (!name) {
        showNotify('Vui lòng nhập tên bộ sưu tập!', 'warning');
        return;
      }
      
      if (typeof window.collections !== 'object' || window.collections === null) {
        window.collections = {};
      }
      
      const idsToSave = Array.from(SELECTED_IDS).map(id => {
        const house = (window.DATA && window.DATA.find(p => p && String(p.id) === String(id))) || 
                      (typeof window.getMappedPoolData === 'function' && window.getMappedPoolData().find(p => p && String(p.id) === String(id)));
        return house && house.system_id ? String(house.system_id) : String(id);
      });

      if (window.collections[name]) {
        const currentIds = window.collections[name] || [];
        const merged = Array.from(new Set([...currentIds, ...idsToSave]));
        window.collections[name] = merged;
        localStorage.setItem('adminCollections', JSON.stringify(window.collections));
        
        document.querySelectorAll('.card-sel').forEach(cb => cb.checked = false);
        SELECTED_IDS.clear();
        updateShareUI();
        renderCollectionsManager();
        
        showNotify(`Bộ sưu tập "${name}" đã tồn tại. Đã nạp thêm căn mới vào bộ sưu tập này thành công! (Tổng số: ${merged.length} căn)`, 'success');
        document.getElementById('colSaveModal').classList.remove('open');
        
        viewCollection(name);
        return;
      }
      
      window.collections[name] = idsToSave;
      localStorage.setItem('adminCollections', JSON.stringify(window.collections));
      
      document.querySelectorAll('.card-sel').forEach(cb => cb.checked = false);
      
      SELECTED_IDS.clear();
      updateShareUI();
      
      renderCollectionsManager();
      
      showNotify(`Đã tạo bộ sưu tập "${name}" với ${idsToSave.length} căn thành công!`, 'success');
      document.getElementById('colSaveModal').classList.remove('open');
      
      viewCollection(name);
    } catch (err) {
      showNotify(`❌ Lỗi tạo bộ sưu tập: ${err.message}`, 'error');
      console.error(err);
    }
  }

  function saveToExistingCollection(name) {
    try {
      if (typeof window.collections !== 'object' || window.collections === null) {
        window.collections = {};
      }
      if (!window.collections[name]) return;
      
      const currentIds = window.collections[name] || [];
      const newIds = Array.from(SELECTED_IDS).map(id => {
        const house = (window.DATA && window.DATA.find(p => p && String(p.id) === String(id))) || 
                      (typeof window.getMappedPoolData === 'function' && window.getMappedPoolData().find(p => p && String(p.id) === String(id)));
        return house && house.system_id ? String(house.system_id) : String(id);
      });
      
      const merged = Array.from(new Set([...currentIds, ...newIds]));
      const addedCount = merged.length - currentIds.length;
      
      window.collections[name] = merged;
      localStorage.setItem('adminCollections', JSON.stringify(window.collections));
      
      document.querySelectorAll('.card-sel').forEach(cb => cb.checked = false);
      
      SELECTED_IDS.clear();
      updateShareUI();
      
      renderCollectionsManager();
      
      showNotify(`Đã lưu thêm ${addedCount} căn mới vào bộ sưu tập "${name}" thành công! (Tổng số: ${merged.length} căn)`, 'success');
      
      viewCollection(name);
    } catch (err) {
      showNotify(`❌ Lỗi lưu bộ sưu tập: ${err.message}`, 'error');
      console.error(err);
    }
  }

  function viewCollection(name) {
    try {
      window.activeCollectionName = name;
      
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
          count = window.collections[name] ? window.collections[name].length : 0;
          displayName = `📂 ${name}`;
        }
        text.innerHTML = `<b>${displayName}</b> (${count} căn)`;
        bar.style.display = 'flex';
      }
      
      if (typeof window.render === 'function') window.render();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      console.error("Error viewing collection:", err);
    }
  }

  function exitCollectionView() {
    console.log("DEBUG JS: exitCollectionView called");
    try {
      window.activeCollectionName = null;
      
      const bar = document.getElementById('activeColBar');
      if (bar) bar.style.display = 'none';
      
      if (typeof window.render === 'function') window.render();
    } catch (err) {
      console.error("Error exiting collection view:", err);
    }
  }

  function closeColViewModal() {
    try {
      const modal = document.getElementById('colViewModal');
      if (modal) modal.classList.remove('open');
      if (typeof window.renderSpeedDialActions === 'function') {
        window.renderSpeedDialActions('list');
      }
    } catch (err) {
      console.error("Error closing collection view modal:", err);
    }
  }

  function deleteSelectedCollections() {
    try {
      const checkboxes = document.querySelectorAll('.col-delete-checkbox:checked');
      if (checkboxes.length === 0) {
        showNotify('Vui lòng chọn ít nhất 1 bộ sưu tập để xóa!', 'warning');
        return;
      }
      
      const namesToDelete = Array.from(checkboxes).map(cb => cb.dataset.colname);
      if (!confirm(`Bạn có chắc chắn muốn xóa ${namesToDelete.length} bộ sưu tập đã chọn không?`)) {
        return;
      }
      
      if (typeof window.collections !== 'object' || window.collections === null) {
        window.collections = {};
      }
      
      namesToDelete.forEach(name => {
        delete window.collections[name];
      });
      
      localStorage.setItem('adminCollections', JSON.stringify(window.collections));
      
      renderCollectionsManager();
      
      namesToDelete.forEach(name => {
        if (window.activeCollectionName === name) {
          exitCollectionView();
        }
      });
      
      closeColViewModal();
      showNotify('Đã xóa thành công các bộ sưu tập đã chọn!', 'success');
    } catch (err) {
      showNotify(`❌ Lỗi khi xóa bộ sưu tập: ${err.message}`, 'error');
      console.error(err);
    }
  }

  function deleteCollection(name, event) {
    try {
      if (event) event.stopPropagation();
      
      const targetElement = event ? (event.currentTarget || event.target) : null;
      const btn = targetElement ? (targetElement.closest('button') || targetElement.closest('span')) : null;
      
      if (btn) {
        if (btn.getAttribute('data-confirm') === 'true') {
          if (typeof window.collections !== 'object' || window.collections === null) {
            window.collections = {};
          }
          
          delete window.collections[name];
          localStorage.setItem('adminCollections', JSON.stringify(window.collections));
          
          renderCollectionsManager();
          
          if (window.activeCollectionName === name) {
            exitCollectionView();
          }
          
          const modal = document.getElementById('colViewModal');
          if (modal && modal.classList.contains('open')) {
            openColViewModal();
          }
        } else {
          const originalText = btn.innerHTML;
          btn.setAttribute('data-confirm', 'true');
          btn.innerHTML = btn.tagName.toLowerCase() === 'button' ? '⚠️ Xóa?' : '⚠️';
          btn.style.color = '#e74c3c';
          btn.style.fontWeight = 'bold';
          
          setTimeout(() => {
            if (btn && btn.getAttribute('data-confirm') === 'true') {
              btn.setAttribute('data-confirm', 'false');
              btn.innerHTML = originalText;
              btn.style.color = btn.tagName.toLowerCase() === 'button' ? 'var(--sub)' : 'rgba(44,44,46,0.5)';
              btn.style.fontWeight = 'normal';
            }
          }, 3000);
        }
      } else {
        if (!confirm(`Bạn có chắc chắn muốn xóa bộ sưu tập "${name}" không?`)) {
          return;
        }
        if (typeof window.collections !== 'object' || window.collections === null) {
          window.collections = {};
        }
        delete window.collections[name];
        localStorage.setItem('adminCollections', JSON.stringify(window.collections));
        renderCollectionsManager();
        if (window.activeCollectionName === name) {
          exitCollectionView();
        }
        const modal = document.getElementById('colViewModal');
        if (modal && modal.classList.contains('open')) {
          openColViewModal();
        }
      }
    } catch (err) {
      showNotify(`❌ Lỗi xóa bộ sưu tập: ${err.message}`, 'error');
      console.error(err);
    }
  }

  function removeFromCol(id, colName, event) {
    try {
      if (event) event.stopPropagation();
      
      const item = (window.DATA && window.DATA.find(x => x && String(x.id) === String(id))) || 
                   (typeof window.getMappedPoolData === 'function' && window.getMappedPoolData().find(x => x && String(x.id) === String(id)));
      const systemId = item && item.system_id ? String(item.system_id) : String(id);
      
      if (colName === 'favorites') {
        favs.delete(systemId);
        localStorage.setItem('favs', JSON.stringify(Array.from(favs)));
        if (typeof window.updateFavBtnUI === 'function') window.updateFavBtnUI();
      } else if (window.collections[colName]) {
        window.collections[colName] = window.collections[colName].filter(x => String(x) !== systemId);
        localStorage.setItem('adminCollections', JSON.stringify(window.collections));
        renderCollectionsManager();
      }
      
      viewCollection(colName);
    } catch (err) {
      showNotify(`❌ Lỗi gỡ khỏi bộ sưu tập: ${err.message}`, 'error');
      console.error(err);
    }
  }

  function renderCollectionsManager() {
    try {
      const manager = document.getElementById('collectionsManager');
      if (!manager) return;
      manager.innerHTML = '';
      
      if (typeof window.collections !== 'object' || window.collections === null) {
        window.collections = {};
      }
      
      const colNames = Object.keys(window.collections);
      if (colNames.length === 0) {
        manager.innerHTML = '<span style="font-size:12px; color:rgba(44,44,46,0.5); padding:6px 6px;">Chưa có bộ sưu tập. Chọn căn & bấm 📁 để tạo.</span>';
        return;
      }
      
      colNames.forEach(name => {
        const val = window.collections[name];
        if (!Array.isArray(val)) return;
        const count = val.length;
        const chip = document.createElement('div');
        chip.style.cssText = 'display:inline-flex; align-items:center; gap:6px; background:#ffffff; border:1.5px solid #e2ded6; border-radius:16px; padding:6px 12px; font-size:12px; font-weight:600; color:#3a3a3c; cursor:pointer; transition:all 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.05);';
        
        const viewSpan = document.createElement('span');
        viewSpan.style.cssText = 'display:inline-flex; align-items:center; gap:4px;';
        viewSpan.innerHTML = `📁 ${name} (${count})`;
        viewSpan.onclick = () => viewCollection(name);
        
        const delSpan = document.createElement('span');
        delSpan.style.cssText = 'color:rgba(44,44,46,0.5); font-size:11px; padding-left:6px; border-left:1px solid #e2ded6; margin-left:2px;';
        delSpan.title = 'Xóa';
        delSpan.innerHTML = '✕';
        delSpan.onclick = (e) => {
          deleteCollection(name, e);
        };
        
        chip.appendChild(viewSpan);
        chip.appendChild(delSpan);
        manager.appendChild(chip);
      });
    } catch (err) {
      console.error("Error rendering collections manager:", err);
    }
  }

  // Register globally
  window.th = th;
  window.updateFavBtnUI = updateFavBtnUI;
  window.updateShareUI = updateShareUI;
  window.openColViewModal = openColViewModal;
  window.openColSaveModal = openColSaveModal;
  window.createNewCollection = createNewCollection;
  window.saveToExistingCollection = saveToExistingCollection;
  window.viewCollection = viewCollection;
  window.exitCollectionView = exitCollectionView;
  window.closeColViewModal = closeColViewModal;
  window.deleteSelectedCollections = deleteSelectedCollections;
  window.deleteCollection = deleteCollection;
  window.removeFromCol = removeFromCol;
  window.renderCollectionsManager = renderCollectionsManager;

})();
