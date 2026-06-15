// Lego Frontend - Client Detail View Module
// US-094C: Cô lập Module Chi tiết & Carousel thực tế của Khách hàng

(function() {
  // Lightbox State Variables
  let lbIdx = 0;
  let currentImgs = [];
  let lbImgScale = 1;
  let lbImgPosX = 0;
  let lbImgPosY = 0;
  let lbMaxTouches = 0;
  let lbStartDist = 0;
  let lbLastScale = 1;
  let lbTx = 0;
  let lbTy = 0;
  let lbDragging = false;
  let lbCw = 0;

  function isLbVideo(s) {
    return s.includes('facebook.com') || s.includes('fb.watch') || s.includes('fb.gg');
  }

  function buildLbTrack() {
    const main = document.getElementById('lbMain');
    if (!main) return;
    lbCw = main.offsetWidth;
    const track = document.createElement('div');
    track.id = 'lbTrack';
    track.style.cssText = `display:flex;height:100%;width:100%;will-change:transform;transition:none;`;
    currentImgs.forEach((s, i) => {
      const slide = document.createElement('div');
      slide.style.cssText = 'min-width:100%;height:100%;display:flex;align-items:center;justify-content:center;overflow:hidden;';
      if (isLbVideo(s)) {
        const encoded = encodeURIComponent(s);
        slide.innerHTML = `<iframe src="https://www.facebook.com/plugins/video.php?href=${encoded}&show_text=false" style="width:100%;height:100%;border:none;overflow:hidden;" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>`;
      } else {
        slide.innerHTML = `<img src="${window.fixImgUrl(s, 'w800')}" class="lb-img" id="lbImg-${i}" style="max-width:100%;max-height:100%;object-fit:contain;user-select:none;pointer-events:auto;will-change:transform;transition:transform 0.15s ease-out;" />`;
      }
      track.appendChild(slide);
    });
    main.innerHTML = '';
    main.appendChild(track);
    track.style.transform = `translateX(${-lbIdx * lbCw}px)`;
  }

  function lbAnimateTo(idx) {
    const track = document.getElementById('lbTrack');
    if (!track) return;
    lbImgScale = 1; lbImgPosX = 0; lbImgPosY = 0;
    const prev = document.getElementById(`lbImg-${lbIdx}`);
    if (prev) prev.style.transform = 'translate(0,0) scale(1)';
    lbIdx = idx;
    track.style.transition = 'transform .3s cubic-bezier(.25,.46,.45,.94)';
    track.style.transform = `translateX(${-lbIdx * lbCw}px)`;
    updateLbThumbsUI();
  }

  function openLb(i) {
    lbIdx = i;
    const lbOverlay = document.getElementById('lbOverlay');
    if (lbOverlay) lbOverlay.classList.add('open');
    buildLbTrack();
    renderLbThumbs();
    updateLbThumbsUI();
  }

  function closeLb() {
    const lbOverlay = document.getElementById('lbOverlay');
    if (lbOverlay) lbOverlay.classList.remove('open');
    const lbMain = document.getElementById('lbMain');
    if (lbMain) lbMain.innerHTML = '';
    lbImgScale = 1; lbImgPosX = 0; lbImgPosY = 0; lbMaxTouches = 0; lbStartDist = 0;
  }

  function lbMove(d) {
    if (!currentImgs || currentImgs.length === 0) return;
    const newIdx = (lbIdx + d + currentImgs.length) % currentImgs.length;
    lbAnimateTo(newIdx);
  }

  function goToLb(i) { lbAnimateTo(i); }

  function renderLbThumbs() {
    const lbThumbs = document.getElementById('lbThumbs');
    if (!lbThumbs) return;
    lbThumbs.innerHTML = currentImgs.map((s, i) => {
      if (isLbVideo(s)) return `<div class="lb-thumb-vid ${i === lbIdx ? 'on' : ''}" onclick="goToLb(${i})" id="lbt-${i}">▶</div>`;
      return `<img src="${window.fixImgUrl(s, 'w200')}" class="lb-thumb ${i === lbIdx ? 'on' : ''}" onclick="goToLb(${i})" id="lbt-${i}">`;
    }).join('');
  }

  function updateLbThumbsUI() {
    document.querySelectorAll('.lb-thumb, .lb-thumb-vid').forEach((el, i) => {
      el.classList.toggle('on', i === lbIdx);
      if (i === lbIdx) el.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    });
  }

  // Bind Events for Lightbox Touch Gestures
  function initLightboxEvents() {
    const lbMain = document.getElementById('lbMain');
    if (!lbMain) return;

    // Remove old listeners to avoid duplicates
    const newLbMain = lbMain.cloneNode(true);
    lbMain.parentNode.replaceChild(newLbMain, lbMain);

    newLbMain.addEventListener('touchstart', e => {
      e.preventDefault();
      lbMaxTouches = Math.max(lbMaxTouches, e.touches.length);
      if (e.touches.length === 2) {
        const img = document.getElementById(`lbImg-${lbIdx}`);
        if (img) {
          lbStartDist = Math.hypot(
            e.touches[0].clientX - e.touches[1].clientX,
            e.touches[0].clientY - e.touches[1].clientY
          );
          lbLastScale = lbImgScale;
        }
      } else if (e.touches.length === 1) {
        lbTx = e.touches[0].clientX;
        lbTy = e.touches[0].clientY;
        lbDragging = true;
        const track = document.getElementById('lbTrack');
        if (track) track.style.transition = 'none';
      }
    }, { passive: false });

    newLbMain.addEventListener('touchmove', e => {
      e.preventDefault();
      lbMaxTouches = Math.max(lbMaxTouches, e.touches.length);
      const img = document.getElementById(`lbImg-${lbIdx}`);
      const track = document.getElementById('lbTrack');
      if (!track) return;

      if (e.touches.length === 2 && lbStartDist > 0 && img) {
        const dist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        lbImgScale = Math.max(1, Math.min(4, lbLastScale * (dist / lbStartDist)));
        img.style.transform = `translate(${lbImgPosX}px,${lbImgPosY}px) scale(${lbImgScale})`;
      } else if (e.touches.length === 1 && lbDragging) {
        if (lbImgScale > 1) {
          const newX = lbImgPosX + (e.touches[0].clientX - lbTx);
          const newY = lbImgPosY + (e.touches[0].clientY - lbTy);
          lbTx = e.touches[0].clientX; lbTy = e.touches[0].clientY;
          lbImgPosX = newX; lbImgPosY = newY;
          if (img) img.style.transform = `translate(${lbImgPosX}px,${lbImgPosY}px) scale(${lbImgScale})`;
        } else {
          const dx = lbTx - e.touches[0].clientX;
          track.style.transform = `translateX(${-lbIdx * lbCw - dx}px)`;
        }
      }
    }, { passive: false });

    newLbMain.addEventListener('touchend', e => {
      lbDragging = false;
      const wasMulti = lbMaxTouches >= 2;
      if (e.touches.length === 0) {
        lbMaxTouches = 0; lbStartDist = 0;
      }
      if (lbImgScale <= 1.05) {
        lbImgScale = 1; lbImgPosX = 0; lbImgPosY = 0;
        const img = document.getElementById(`lbImg-${lbIdx}`);
        if (img) img.style.transform = 'translate(0,0) scale(1)';
      }
      if (e.touches.length === 0 && !wasMulti && lbImgScale <= 1.05) {
        const dx = lbTx - e.changedTouches[0].clientX;
        const newIdx = Math.abs(dx) > 50
          ? Math.max(0, Math.min(currentImgs.length - 1, lbIdx + (dx > 0 ? 1 : -1)))
          : lbIdx;
        requestAnimationFrame(() => {
          const track = document.getElementById('lbTrack');
          if (track) track.style.transition = 'transform .3s cubic-bezier(.25,.46,.45,.94)';
          requestAnimationFrame(() => {
            if (newIdx !== lbIdx) lbAnimateTo(newIdx);
            else {
              const track2 = document.getElementById('lbTrack');
              if (track2) track2.style.transform = `translateX(${-lbIdx * lbCw}px)`;
            }
          });
        });
      }
    }, { passive: false });
  }

  // Keyboard Navigation
  document.addEventListener('keydown', (e) => {
    const lb = document.getElementById('lbOverlay');
    if (lb && lb.classList.contains('open') && currentImgs && currentImgs.length > 0) {
      if (e.key === 'ArrowRight') {
        lbMove(1);
      } else if (e.key === 'ArrowLeft') {
        lbMove(-1);
      } else if (e.key === 'Escape') {
        closeLb();
      }
    }
  });

  // Setup Scroll Carousel
  function setupScrollCarousel(containerId, imageUrls, isLegalImg = false) {
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
      const cleanUrl = window.fixImgUrl(url, 'w800');
      const item = document.createElement('div');
      item.className = 'admin-carousel-item';
      item.onclick = () => {
        window.openLightboxForCarousel(imageUrls, idx);
      };
      item.style.cursor = 'zoom-in';
      item.innerHTML = `<img src="${cleanUrl}" alt="Hình ${idx + 1}" loading="lazy" decoding="async">`;
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
  }

  // Legacy Gallery functions (buildG, gm, ua)
  let gI = 0, gN = 0, tx = 0;
  function buildG(imgs) {
    gI = 0; gN = imgs.length; currentImgs = imgs;
    const gt = document.getElementById('gt'), gd = document.getElementById('gd');
    if (!gt || !gd) return;
    gt.innerHTML = ''; gd.innerHTML = '';
    const gw = document.getElementById('gw');
    if (!gw) return;
    if (!imgs.length) { gw.style.display = 'none'; return; }
    gw.style.display = '';
    imgs.forEach((s, i) => {
      const sl = document.createElement('div'); sl.className = 'gslide';
      if (s.includes('facebook.com') || s.includes('fb.watch') || s.includes('fb.gg')) {
        const encoded = encodeURIComponent(s);
        sl.innerHTML = `
      <div onclick="openLb(${i})" style="position:absolute; inset:0; z-index:10; cursor:pointer;"></div>
      <iframe src="https://www.facebook.com/plugins/video.php?href=${encoded}&show_text=false" style="width:auto;height:100%;max-width:100%;aspect-ratio:9/16;margin:0 auto;display:block;border:none;overflow:hidden;" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>`;
      } else {
        sl.innerHTML = `<img src="${window.fixImgUrl(s, 'w800')}" alt="Ảnh ${i + 1}" loading="${i === 0 ? 'eager' : 'lazy'}" onclick="openLb(${i})">`;
      }
      gt.appendChild(sl);
      const d = document.createElement('div'); d.className = 'dot' + (i === 0 ? ' on' : '');
      gd.appendChild(d);
    });
    gt.style.transform = 'translateX(0px)'; ua();

    let gwMaxTouches = 0, gwCw = 0;
    gw.ontouchstart = e => {
      gwMaxTouches = Math.max(gwMaxTouches, e.touches.length);
      if (e.touches.length === 1 && gwMaxTouches === 1) {
        gwCw = gw.offsetWidth;
        tx = e.touches[0].clientX;
        gt.style.transition = 'none';
      }
    };
    gw.ontouchmove = e => {
      e.preventDefault();
      gwMaxTouches = Math.max(gwMaxTouches, e.touches.length);
      if (gwMaxTouches >= 2 || !gwCw) return;
      const dx = tx - e.touches[0].clientX;
      gt.style.transform = `translateX(${-gI * gwCw - dx}px)`;
    };
    gw.ontouchend = e => {
      if (e.touches.length === 0) {
        const wasPinch = gwMaxTouches >= 2;
        gwMaxTouches = 0;
        if (!wasPinch) {
          const dx = tx - e.changedTouches[0].clientX;
          if (Math.abs(dx) > 50) gI = Math.max(0, Math.min(gN - 1, gI + (dx > 0 ? 1 : -1)));
        }
        document.querySelectorAll('.dot').forEach((x, i) => x.classList.toggle('on', i === gI));
        ua();
        requestAnimationFrame(() => {
          gt.style.transition = '';
          requestAnimationFrame(() => {
            gt.style.transform = `translateX(${-gI * gwCw}px)`;
          });
        });
      }
    };
  }

  function gm(d) {
    gI = Math.max(0, Math.min(gN - 1, gI + d));
    const gwEl = document.getElementById('gw');
    const cw = gwEl ? gwEl.offsetWidth : 0;
    const gt = document.getElementById('gt');
    if (gt) gt.style.transform = `translateX(${-gI * cw}px)`;
    document.querySelectorAll('.dot').forEach((x, i) => x.classList.toggle('on', i === gI));
    ua();
  }

  function ua() {
    const al = document.getElementById('al');
    const ar = document.getElementById('ar');
    if (al) al.style.display = gI === 0 ? 'none' : 'flex';
    if (ar) ar.style.display = gI === gN - 1 ? 'none' : 'flex';
  }

  // Expose lightbox and carousel functions globally
  window.openLightboxForCarousel = function(imageUrls, index) {
    currentImgs = imageUrls;
    openLb(index);
  };
  window.openLb = openLb;
  window.closeLb = closeLb;
  window.goToLb = goToLb;
  window.lbAnimateTo = lbAnimateTo;
  window.lbMove = lbMove;
  window.setupScrollCarousel = setupScrollCarousel;
  window.buildG = buildG;
  window.gm = gm;
  window.ua = ua;

  // Initialize events on page load
  document.addEventListener('DOMContentLoaded', () => {
    initLightboxEvents();
  });
  // Also run if DOMContentLoaded has already fired
  if (document.readyState === 'interactive' || document.readyState === 'complete') {
    initLightboxEvents();
  }

  // --- LegoDetailClient Component ---
  window.LegoDetailClient = {
    render: function(p, sbody) {
      let targetMatTien = p.img_mat_tien || (p.pool_row_data ? p.pool_row_data[29] : '') || '';
      // Tránh việc facade ảnh bị trôi nếu đang ở chế độ preview trong iframe
      if (window.parent && window.parent !== window) {
        try {
          const el = window.parent.document.getElementById('editCoverImgUrl');
          if (el && el.value.trim()) {
            targetMatTien = el.value.trim();
          }
        } catch(e) {}
      }
      const normMatTien = window.normalizeImgUrl ? window.normalizeImgUrl(targetMatTien) : '';
      const isFacadeUrl = (url) => {
        if (!url) return false;
        const norm = window.normalizeImgUrl ? window.normalizeImgUrl(url) : '';
        return norm !== '' && norm === normMatTien;
      };

      const cleanImgs = (p.imgs || []).filter(url => {
        return (!window.isListingSodoUrl || !window.isListingSodoUrl(url, p)) && !isFacadeUrl(url);
      });
      const sortedImgs = cleanImgs.sort((a, b) => {
        const aVis = (a.includes('facebook.com') || a.includes('fb.watch') || a.includes('fb.gg')) ? 1 : 0;
        const bVis = (b.includes('facebook.com') || b.includes('fb.watch') || b.includes('fb.gg')) ? 1 : 0;
        return bVis - aVis;
      });

      sbody.innerHTML = `
        <div style="font-size:13.5px; font-weight:700; color:#1c1c1e; margin-bottom:8px; line-height:1.4;">${p.t || p.raw_tieu_de_public || 'Chưa có tiêu đề public.'}</div>
        <div id="carouselClientDetail" style="position: relative; margin-bottom: 12px;">
          <div class="admin-scroll-carousel"></div>
          <div class="admin-carousel-dots"></div>
        </div>
        <div class="admin-raw-grid" style="margin-bottom: 12px;">
          <div class="admin-raw-cell">
            <span class="label">Giá bán:</span>
            <span class="value dotted" style="color:var(--red); font-weight:800;">${p.gia} tỷ</span>
          </div>
          <div class="admin-raw-cell">
            <span class="label">Diện tích:</span>
            <span class="value dotted">${p.dt} m²</span>
          </div>
          <div class="admin-raw-cell">
            <span class="label">Đơn giá:</span>
            <span class="value dotted" style="color:var(--gold); font-weight:800;">${p.giabq}</span>
          </div>
          <div class="admin-raw-cell">
            <span class="label">Quận/TP:</span>
            <span class="value dotted">${p.ql}</span>
          </div>
          <div class="admin-raw-cell">
            <span class="label">Phường:</span>
            <span class="value dotted">${p.phuong}</span>
          </div>
          <div class="admin-raw-cell">
            <span class="label">Loại:</span>
            <span class="value dotted">${p.loai_hinh}</span>
          </div>
          <div class="admin-raw-cell">
            <span class="label">Đường trước:</span>
            <span class="value dotted">${p.duong_truoc_nha}</span>
          </div>
          <div class="admin-raw-cell">
            <span class="label">Kết cấu:</span>
            <span class="value dotted">${p.tang} tầng</span>
          </div>
        </div>
        <div class="desc" style="white-space:pre-wrap; line-height:1.6; font-size:12px; color:#2c3e50; background:#f8f9fa; padding:12px; border-radius:8px; border:1px solid #dfe4ea;">${p.m || p.raw_mo_ta_public || 'Chưa có mô tả public.'}</div>
        
        <!-- KHUNG TƯƠNG TÁC PHẢN HỒI (US-059) -->
        <div class="client-feedback-box">
          <h4>🏡 Căn nhà này thế nào với anh/chị?</h4>
          <div class="client-feedback-btns">
            <button onclick="scheduleViewing('${p.id}', '${p.t.replace(/'/g, "\\'")}')" class="client-feedback-btn primary">
              📅 Hẹn đi xem nhà
            </button>
            <button onclick="showRequirementForm('${p.id}')" class="client-feedback-btn secondary">
              ✏️ Cần tìm căn khác, gửi lại nhu cầu
            </button>
          </div>
          
          <!-- Form ghi nhu cầu khác -->
          <div id="clientReqForm_${p.id}" class="client-req-form" style="display: none;">
            <p>Hãy chia sẻ mong muốn tìm nhà của anh/chị (Khu vực, tài chính, số phòng ngủ, hướng nhà...):</p>
            <textarea id="clientReqText_${p.id}" class="client-req-textarea" placeholder="Ví dụ: Cần tìm nhà Quận 3 hoặc Phú Nhuận, hẻm xe hơi, giá tầm 10 tỷ..."></textarea>
            <button onclick="submitClientRequirement('${p.id}', '${p.t.replace(/'/g, "\\'")}')" class="client-req-submit-btn">
              🚀 Gửi nhu cầu cho Khang Ngô
            </button>
          </div>
        </div>
      `;
      setupScrollCarousel('carouselClientDetail', sortedImgs, false);
    }
  };
})();
