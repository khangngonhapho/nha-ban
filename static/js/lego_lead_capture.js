(function () {
  'use strict';

  // Initialize customer variables on window
  if (typeof window.displayCustomerName === 'undefined') {
    window.displayCustomerName = "";
  }
  if (typeof window.trackingCustomerName === 'undefined') {
    window.trackingCustomerName = "";
  }

  function checkLeadCapture(isClientView) {
    const isPreview = new URLSearchParams(window.location.search).get('preview') === 'true';
    if (isPreview) {
      return;
    }
    if (isClientView) {
      const savedName = localStorage.getItem('client_name');
      const savedPhone = localStorage.getItem('client_phone');
      if (savedName && savedPhone) {
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

  function submitLeadCapture() {
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
      window.trackAction("Khách tự đăng ký", `Tên: ${name} - SĐT: ${phone}`);
      const dataLength = window.DATA ? window.DATA.length : 0;
      if (dataLength > 0) {
        window.trackAction("Mở danh sách nhà", `Số lượng hiển thị: ${dataLength} căn`);
      }
    }
  }

  function scheduleViewing(id, title) {
    if (typeof window.trackAction === 'function') {
      window.trackAction("Hẹn lịch xem nhà", `Mã căn: #${id} - ${title}`);
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
        window.trackAction("Mở form nhu cầu khác", `Mã căn: #${id}`);
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
      window.trackAction("Gửi nhu cầu khác", `Xem căn #${id} chưa phù hợp. Nhu cầu: ${reqText}`);
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
