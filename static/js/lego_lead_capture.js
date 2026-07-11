(function () {
  'use strict';

  const TRACKING_SHEET_ID = '1zCAP0pUSZdVNxbEkVl94y_hJc1ShM4PqtB-fxpm_I5Y';

  // Initialize customer variables on window
  if (typeof window.displayCustomerName === 'undefined') {
    window.displayCustomerName = "";
  }
  if (typeof window.trackingCustomerName === 'undefined') {
    window.trackingCustomerName = "";
  }

  // Helper to compute SHA-256 in client JS using Web Crypto API
  async function sha256(text) {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const hash = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  // Show premium glassmorphic lock screen
  function showLockScreen(message) {
    let overlay = document.getElementById('secureLockOverlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'secureLockOverlay';
      overlay.style.cssText = `
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(13, 13, 15, 0.96);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        z-index: 100000;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #e4e4e7;
        text-align: center;
        padding: 30px;
        font-family: 'Outfit', sans-serif;
      `;
      document.body.appendChild(overlay);
    }
    overlay.innerHTML = `
      <div style="background: rgba(26, 26, 30, 0.7); border: 1.5px solid rgba(255, 191, 36, 0.2); border-radius: 24px; padding: 40px 30px; max-width: 440px; box-shadow: 0 10px 40px rgba(0,0,0,0.5);">
        <span style="font-size: 64px; margin-bottom: 20px; display: inline-block;">🔒</span>
        <h2 style="color: #ffbf24; font-size: 24px; font-weight: 800; margin-bottom: 12px; font-family: inherit;">TRUY CẬP BỊ KHÓA</h2>
        <p style="color: #a1a1aa; font-size: 14.5px; line-height: 1.6; font-family: inherit;">${message}</p>
        <div style="margin-top: 24px; font-size: 11px; color: #a1a1aa; opacity: 0.5;">
          BDS Khang Ngô - Hệ thống Bảo mật Rổ hàng VIP
        </div>
      </div>
    `;
    
    // Disable scrolling
    document.body.style.overflow = 'hidden';
    
    // Hide main list container to prevent DOM inspection leaks
    const listContainer = document.getElementById('listContainer');
    if (listContainer) listContainer.style.display = 'none';
  }

  // Run security validation (blacklist and forwarding checks)
  async function runSecurityChecks(name, phone) {
    if (!phone) return true;
    
    const cleanPhone = phone.replace(/[\s\.-]/g, "");
    const phoneHash = await sha256(cleanPhone);
    
    // 1. Check Blacklist via GViz JSON query
    try {
      const blacklistUrl = `https://docs.google.com/spreadsheets/d/${TRACKING_SHEET_ID}/gviz/tq?tqx=out:json&sheet=Public_Phone_Blacklist&t=${Date.now()}`;
      const blRes = await fetch(blacklistUrl);
      if (blRes.ok) {
        const blText = await blRes.text();
        const blJsonStart = blText.indexOf('setResponse(') + 12;
        const blJsonEnd = blText.lastIndexOf(')');
        const blJson = JSON.parse(blText.substring(blJsonStart, blJsonEnd));
        
        const blockedHashes = (blJson.table.rows || []).map(r => r.c && r.c[0] ? String(r.c[0].v).trim() : '').filter(Boolean);
        if (blockedHashes.includes(phoneHash)) {
          showLockScreen("Số điện thoại của anh/chị đã bị chặn truy cập hệ thống. Vui lòng liên hệ trực tiếp với anh Khang Ngô để được hỗ trợ.");
          return false;
        }
      }
    } catch (err_bl) {
      console.warn("[⚠️ BLACKLIST CHECK FAILED] Skipping blacklist check:", err_bl);
    }

    // 2. Check Secure Link Status
    const urlParams = new URLSearchParams(window.location.search);
    const linkId = urlParams.get('lnk');
    if (linkId) {
      try {
        const linkStatusUrl = `https://docs.google.com/spreadsheets/d/${TRACKING_SHEET_ID}/gviz/tq?tqx=out:json&sheet=Public_Link_Status&t=${Date.now()}`;
        const statusRes = await fetch(linkStatusUrl);
        if (statusRes.ok) {
          const statusText = await statusRes.text();
          const jsonStart = statusText.indexOf('setResponse(') + 12;
          const jsonEnd = statusText.lastIndexOf(')');
          const json = JSON.parse(statusText.substring(jsonStart, jsonEnd));
          
          const rows = json.table.rows || [];
          const linkRow = rows.find(r => r.c && r.c[0] && String(r.c[0].v).trim() === linkId);
          
          if (!linkRow) {
            showLockScreen("Liên kết chia sẻ này không tồn tại hoặc đã bị xóa khỏi hệ thống.");
            return false;
          }
          
          const status = linkRow.c[1] ? String(linkRow.c[1].v).trim() : 'Active';
          const expiresAt = linkRow.c[2] ? String(linkRow.c[2].v).trim() : '';
          const boundHash = linkRow.c[3] ? String(linkRow.c[3].v).trim() : '';
          
          // Check if Revoked
          if (status === 'Revoked') {
            showLockScreen("Liên kết này đã bị thu hồi quyền truy cập bởi Admin Khang Ngô.");
            return false;
          }
          
          // Check if Expired
          if (expiresAt && new Date(expiresAt) < new Date()) {
            showLockScreen("Liên kết chia sẻ này đã hết hạn xem. Vui lòng liên hệ anh Khang Ngô để nhận liên kết mới.");
            return false;
          }
          
          // Check Forwarding (First-Come-First-Lock)
          if (boundHash && boundHash.trim()) {
            if (boundHash.trim() !== phoneHash) {
              // Forwarding detected! Log alert event to sheet before locking out
              if (typeof window.trackAction === 'function') {
                let originalClientName = "Không rõ";
                const customerToken = urlParams.get('c');
                if (customerToken) {
                  try {
                    let safeToken = customerToken.replace(/ /g, '+');
                    while (safeToken.length % 4) safeToken += '=';
                    originalClientName = decodeURIComponent(escape(window.atob(safeToken)));
                  } catch (e_dec) {}
                }
                
                window.trackAction(
                  "Link bị chuyển tiếp", 
                  `SĐT nhận: ${phone} (${name}) - Khóa bởi khách gốc: ${originalClientName} (SĐT hash: ${boundHash}) - Link ID: ${linkId}`
                );
              }
              
              // Clear credentials
              localStorage.removeItem('client_name');
              localStorage.removeItem('client_phone');
              
              showLockScreen("Liên kết này được tạo riêng tư và đã được khóa cố định vào số điện thoại của khách hàng chính thức. Bạn không được quyền truy cập link chuyển tiếp này.");
              return false;
            }
          } else {
            // Bind/Lock this phone number hash to the link in real-time
            try {
              const bindRes = await fetch('/api/links/bind', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ link_id: linkId, phone_hash: phoneHash })
              });
              const bindData = await bindRes.json();
              if (bindData.status === 'success') {
                console.log(`[🔒 SECURE BIND] Successfully bound link ${linkId} to phone hash ${phoneHash}`);
              }
            } catch (err_bind) {
              console.error("Lỗi bind SĐT vào link:", err_bind);
            }
          }
        }
      } catch (err_link) {
        console.warn("[⚠️ SECURE LINK CHECK FAILED] Skipping link status check:", err_link);
      }
    }
    return true;
  }

  async function checkLeadCapture(isClientView) {
    const isPreview = new URLSearchParams(window.location.search).get('preview') === 'true';
    if (isPreview) {
      return;
    }
    
    // Auto-detect secure link and force client verification
    const urlParams = new URLSearchParams(window.location.search);
    const linkId = urlParams.get('lnk');
    if (linkId) {
      isClientView = true;
    }
    
    if (isClientView) {
      const savedName = localStorage.getItem('client_name');
      const savedPhone = localStorage.getItem('client_phone');
      if (savedName && savedPhone) {
        // Run security checks (blacklist and secure link checks)
        const isPassed = await runSecurityChecks(savedName, savedPhone);
        if (!isPassed) return; // Blocked!
        
        window.displayCustomerName = savedName;
        window.trackingCustomerName = `${savedName} - ${savedPhone}`;
        
        const banner = document.getElementById('welcomeBanner');
        if (banner) {
          banner.innerHTML = `👋 Xin chào <b>${window.displayCustomerName}</b>, đây là danh sách nhà Khang Ngô chọn riêng cho anh/chị!`;
          banner.style.display = 'block';
        }
      } else {
        const leadModal = document.getElementById('leadCaptureModal');
        if (leadModal) {
          leadModal.style.display = 'flex';
          leadModal.classList.add('open');
          
          if (window.displayCustomerName) {
            const leadNameInput = document.getElementById('leadCustName');
            if (leadNameInput) leadNameInput.value = window.displayCustomerName;
          }
        }
      }
    }
  }

  async function submitLeadCapture() {
    const nameInput = document.getElementById('leadCustName');
    const phoneInput = document.getElementById('leadCustPhone');
    const name = nameInput ? nameInput.value.trim() : "";
    let phone = phoneInput ? phoneInput.value.trim() : "";
    
    if (!name) {
      alert("Vui lòng nhập Tên của anh/chị!");
      if (nameInput) nameInput.focus();
      return;
    }
    if (!phone) {
      alert("Vui lòng nhập Số điện thoại liên hệ!");
      if (phoneInput) phoneInput.focus();
      return;
    }
    
    const phoneClean = phone.replace(/[\s\.-]/g, "");
    if (!/^(0\d{9}|[1-9]\d{8})$/.test(phoneClean)) {
      alert("Số điện thoại không hợp lệ! Vui lòng nhập số điện thoại di động Việt Nam gồm 10 chữ số.");
      if (phoneInput) phoneInput.focus();
      return;
    }
    
    if (typeof window.formatPhone === 'function') {
      phone = window.formatPhone(phoneClean);
    } else {
      phone = phoneClean;
    }
    
    // Run security checks before saving credentials to localStorage!
    const isPassed = await runSecurityChecks(name, phone);
    if (!isPassed) return; // Blocked!
    
    localStorage.setItem('client_name', name);
    localStorage.setItem('client_phone', phone);
    
    window.displayCustomerName = name;
    window.trackingCustomerName = `${name} - ${phone}`;
    
    const leadModal = document.getElementById('leadCaptureModal');
    if (leadModal) {
      leadModal.style.display = 'none';
      leadModal.classList.remove('open');
    }
    
    const banner = document.getElementById('welcomeBanner');
    if (banner) {
      banner.innerHTML = `👋 Xin chào <b>${window.displayCustomerName}</b>, đây là danh sách nhà Khang Ngô chọn riêng cho anh/chị!`;
      banner.style.display = 'block';
    }
    
    if (typeof window.trackAction === 'function') {
      // Append secure link details if present
      const urlParams = new URLSearchParams(window.location.search);
      const linkId = urlParams.get('lnk') || '';
      const actionDetails = linkId ? `Tên: ${name} - SĐT: ${phone} (Link ID: ${linkId})` : `Tên: ${name} - SĐT: ${phone}`;
      
      window.trackAction("Khách tự đăng ký", actionDetails);
      const dataLength = window.DATA ? window.DATA.length : 0;
      if (dataLength > 0) {
        window.trackAction("Mở danh sách nhà", `Số lượng hiển thị: ${dataLength} căn`);
      }
    }
  }

  function scheduleViewing(id, title) {
    if (typeof window.trackAction === 'function') {
      const urlParams = new URLSearchParams(window.location.search);
      const linkId = urlParams.get('lnk') || '';
      const actionDetails = linkId ? `Mã căn: #${id} - ${title} (Link ID: ${linkId})` : `Mã căn: #${id} - ${title}`;
      window.trackAction("Hẹn lịch xem nhà", actionDetails);
    }
    const name = localStorage.getItem('client_name') || window.displayCustomerName || "Khách hàng";
    const phone = localStorage.getItem('client_phone') || "";
    const phoneStr = phone ? ` (SĐT: ${phone})` : "";
    const msg = `Chào anh Khang Ngô, tôi là ${name}${phoneStr}. Tôi quan tâm căn nhà mã #${id}: ${title}. Tôi muốn hẹn lịch đi xem nhà thực tế nhé!`;
    const sdt = window.SDT || "0902688000";
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(msg).then(() => {
        alert('Đã copy tin nhắn đặt lịch! Anh/chị hãy dán (Paste) gửi qua Zalo sắp mở ra nhé.');
        window.location.href = `https://zalo.me/${sdt}`;
      }).catch(() => {
        window.location.href = `https://zalo.me/${sdt}`;
      });
    } else {
      window.location.href = `https://zalo.me/${sdt}`;
    }
  }

  function showRequirementForm(id) {
    const form = document.getElementById(`clientReqForm_${id}`);
    if (form) {
      const isHidden = form.style.display === 'none';
      form.style.display = isHidden ? 'block' : 'none';
      if (typeof window.trackAction === 'function') {
        const urlParams = new URLSearchParams(window.location.search);
        const linkId = urlParams.get('lnk') || '';
        const actionDetails = linkId ? `Mã căn: #${id} (Link ID: ${linkId})` : `Mã căn: #${id}`;
        window.trackAction("Mở form nhu cầu khác", actionDetails);
      }
      if (isHidden) {
        setTimeout(() => {
          const textarea = document.getElementById(`clientReqText_${id}`);
          if (textarea) textarea.focus();
        }, 100);
      }
    }
  }

  function submitClientRequirement(id, title) {
    const textEl = document.getElementById(`clientReqText_${id}`);
    if (!textEl) return;
    const reqText = textEl.value.trim();
    if (!reqText) {
      alert("Vui lòng ghi lại nhu cầu tìm nhà của anh/chị!");
      textEl.focus();
      return;
    }
    
    if (typeof window.trackAction === 'function') {
      const urlParams = new URLSearchParams(window.location.search);
      const linkId = urlParams.get('lnk') || '';
      const actionDetails = linkId ? `Xem căn #${id} chưa phù hợp. Nhu cầu: ${reqText} (Link ID: ${linkId})` : `Xem căn #${id} chưa phù hợp. Nhu cầu: ${reqText}`;
      window.trackAction("Gửi nhu cầu khác", actionDetails);
    }
    const name = localStorage.getItem('client_name') || window.displayCustomerName || "Khách hàng";
    const phone = localStorage.getItem('client_phone') || "";
    const phoneStr = phone ? ` (SĐT: ${phone})` : "";
    const msg = `Chào anh Khang Ngô, tôi là ${name}${phoneStr}. Tôi xem căn #${id} chưa phù hợp. Nhu cầu thực tế của tôi là: ${reqText}. Anh tìm giúp tôi căn phù hợp nhé!`;
    const sdt = window.SDT || "0902688000";
    
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(msg).then(() => {
        alert('Đã ghi nhận nhu cầu! Lời nhắn đã được copy, anh/chị hãy dán (Paste) gửi qua Zalo cho Khang nhé.');
        window.location.href = `https://zalo.me/${sdt}`;
      }).catch(() => {
        window.location.href = `https://zalo.me/${sdt}`;
      });
    } else {
      window.location.href = `https://zalo.me/${sdt}`;
    }
    
    textEl.value = "";
    const form = document.getElementById(`clientReqForm_${id}`);
    if (form) form.style.display = 'none';
  }

  // Register globally
  window.checkLeadCapture = checkLeadCapture;
  window.submitLeadCapture = submitLeadCapture;
  window.scheduleViewing = scheduleViewing;
  window.showRequirementForm = showRequirementForm;
  window.submitClientRequirement = submitClientRequirement;

})();
