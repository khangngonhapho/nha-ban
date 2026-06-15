/**
 * Lego State & Logic Core Module (Event-Driven architecture)
 * Handles state management, event publish/subscribe, authentication (Google Identity Services GSI),
 * token refresh, and Google Sheets loading logic.
 */

// Helper functions (defined locally and exposed globally)

function cv(cell) {
  return cell ? (cell.v ?? cell.f ?? '') : '';
}

function parseFloatHelper(val) {
  if (val === null || val === undefined) return 0;
  if (typeof val === 'number') return val;
  let s = String(val).trim();
  if (s.includes(',')) {
    s = s.replace(/,/g, '.');
  }
  let num = parseFloat(s);
  return isNaN(num) ? 0 : num;
}

function parseGia(val) {
  if (!val) return 0;
  let s = String(val).trim();
  if (s.includes(',')) {
    s = s.replace(/,/g, '.');
  }
  let num = parseFloat(s);
  if (isNaN(num)) return 0;
  if (num > 100) num = num / 1000;
  return Math.round(num * 1000) / 1000;
}

function cleanConsecutiveNewlines(text) {
  if (!text) return '';
  return String(text)
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .replace(/\n\s*\n\s*\n+/g, '\n\n')
    .trim();
}

function fixImgUrl(url, sz = 'w800') {
  if (!url) return '';
  if (url.includes('res.cloudinary.com')) {
    const width = sz.replace('w', '');
    return url.replace('/image/upload/', `/image/upload/q_auto,f_auto,a_auto,c_limit,w_${width}/`);
  }
  if (url.includes('thumbnail') || url.includes('uc?export')) {
    return url.replace(/sz=w\d+/, `sz=${sz}`);
  }
  const m1 = url.match(/drive\.google\.com\/file\/d\/([^/?\s]+)/);
  if (m1) return `https://drive.google.com/thumbnail?id=${m1[1]}&sz=${sz}`;
  const m2 = url.match(/[?&]id=([^&\s]+)/);
  if (m2) return `https://drive.google.com/thumbnail?id=${m2[1]}&sz=${sz}`;
  return url;
}

function getDaiNha(p) {
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
}

async function sha256(message) {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  return hashHex;
}

function generateAdminTitleFromNộiDungChinh(p) {
  if (!p) return '';
  let poolItem = p;
  if (!p.isFromPoolOnly && LegoState.POOL_ROWS && LegoState.POOL_ROWS.length && p.system_id) {
    const row = LegoState.POOL_ROWS.find(r => String(r[72] || r[71] || '').trim() === String(p.system_id).trim());
    if (row) {
      poolItem = {
        raw_noi_dung_chinh: String(row[9] || '').replace(/\r\n|\r|\n/g, ' '),
        raw_so_nha: String(row[6] || ''),
        raw_ten_duong: String(row[5] || ''),
        t: String(row[56] || row[55] || row[9] || '')
      };
    }
  }
  const text = String(poolItem.raw_noi_dung_chinh || '').trim();
  const titleStr = String(poolItem.t || '');
  if (!text) {
    const cleanedT = titleStr.includes('|') ? titleStr.substring(titleStr.indexOf('|') + 1).trim() : titleStr;
    const soNhaStr = String(poolItem.raw_so_nha || '');
    const duongStr = String(poolItem.raw_ten_duong || '');
    return `${soNhaStr ? soNhaStr + ' ' : ''}${duongStr ? duongStr : cleanedT}`;
  }
  const priceRegex = /\b\d+(?:[\.,-]\d+)?\s*(?:tỷ|ty|tỉ)(?!\w)/i;
  const match = text.match(priceRegex);
  if (match) {
    return text.substring(0, match.index).trim().replace(/\s+/g, ' ');
  }
  return text.replace(/\s+/g, ' ');
}

// Expose helpers globally
window.cv = cv;
window.parseFloatHelper = parseFloatHelper;
window.parseGia = parseGia;
window.cleanConsecutiveNewlines = cleanConsecutiveNewlines;
window.fixImgUrl = fixImgUrl;
window.getDaiNha = getDaiNha;
window.sha256 = sha256;
window.generateAdminTitleFromNộiDungChinh = generateAdminTitleFromNộiDungChinh;

// Core State Store & Event System definition
const listeners = {};

const LegoState = {
  // State variables
  DATA: [],
  POOL_ROWS: [],
  isAdmin: false,
  isTokenValid: false,
  gCodeClient: null,
  isSecureLoaded: false,
  isDataLoaded: false,
  secureLoadAttempted: false,
  tokenResolvers: [],

  // Pub/Sub Implementation
  on(event, callback) {
    if (!listeners[event]) listeners[event] = [];
    listeners[event].push(callback);
  },

  emit(event, data) {
    if (listeners[event]) {
      listeners[event].forEach(cb => cb(data));
    }
  },

  // Initialize status from localStorage
  init() {
    const token = localStorage.getItem('g_access_token');
    const expiry = localStorage.getItem('g_token_expiry');
    const now = Date.now();
    this.isTokenValid = !!(token && expiry && parseInt(expiry, 10) > now);
    const isSavedAdmin = localStorage.getItem('isAdminSession') === 'true';
    this.isAdmin = this.isTokenValid || isSavedAdmin;
    
    this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: this.isTokenValid });

    // Periodically check background token refresh
    setInterval(() => {
      if (!this.isAdmin) return;
      const tok = localStorage.getItem('g_access_token');
      const exp = localStorage.getItem('g_token_expiry');
      const currentTime = Date.now();

      if (tok && exp) {
        const timeRemaining = parseInt(exp, 10) - currentTime;
        if (timeRemaining > 0 && timeRemaining < 15 * 60 * 1000) {
          const refreshToken = localStorage.getItem('g_refresh_token');
          if (refreshToken) {
            console.log("Token sắp hết hạn. Đang làm mới ngầm định kỳ...");
            const activeClientId = localStorage.getItem('gClientId') || '1088195961071-25r6rpvsfmoudokb75u0m2ugu8na0v0.apps.googleusercontent.com';
            fetch('/api/auth/refresh', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                refresh_token: refreshToken,
                client_id: activeClientId
              })
            })
            .then(res => {
              if (res.ok) {
                return res.json().then(tokenData => {
                  const newToken = tokenData.access_token;
                  const newExpiry = Date.now() + (tokenData.expires_in - 60) * 1000;
                  localStorage.setItem('g_access_token', newToken);
                  localStorage.setItem('g_token_expiry', newExpiry);
                  this.isTokenValid = true;
                  this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: this.isTokenValid });
                  console.log("Làm mới token định kỳ thành công.");
                });
              }
            })
            .catch(e => {
              console.warn("Background silent refresh failed:", e);
            });
          }
        }
      }
    }, 5 * 60 * 1000);
  },

  // Google OAuth GSI Flow Methods
  initGoogleAuth() {
    if (typeof google === 'undefined' || !google.accounts || !google.accounts.oauth2) {
      console.warn("Google GSI Client not loaded yet. Retrying in 100ms...");
      setTimeout(() => this.initGoogleAuth(), 100);
      return;
    }

    let clientId = localStorage.getItem('gClientId');
    if (!clientId) {
      clientId = '1088195961071-25r6rpvsfmoudokb75u0m2ugu8na0v0.apps.googleusercontent.com';
      localStorage.setItem('gClientId', clientId);
    }
    const gClientIdInput = document.getElementById('gClientIdInput');
    if (gClientIdInput) gClientIdInput.value = clientId;

    try {
      this.gCodeClient = google.accounts.oauth2.initCodeClient({
        client_id: clientId,
        scope: 'https://www.googleapis.com/auth/spreadsheets',
        ux_mode: 'popup',
        access_type: 'offline',
        callback: async (response) => {
          if (response.error !== undefined) {
            console.error("OAuth2 error:", response.error);
            this.isTokenValid = false;
            this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: false });
            
            if (this.tokenResolvers.length > 0) {
              this.promptInteractiveLogin();
            }
            return;
          }
          const authCode = response.code;
          console.log("Authorization code received. Exchanging for tokens...");
          
          try {
            const res = await fetch('/api/auth/token', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ 
                code: authCode, 
                client_id: clientId,
                redirect_uri: 'postmessage' 
              })
            });
            
            if (!res.ok) {
              const errData = await res.json();
              throw new Error(errData.error || 'Token exchange failed');
            }
            
            const tokenData = await res.json();
            const token = tokenData.access_token;
            const refresh = tokenData.refresh_token;
            const expiry = Date.now() + (tokenData.expires_in - 60) * 1000;
            
            localStorage.setItem('g_access_token', token);
            if (refresh) {
              localStorage.setItem('g_refresh_token', refresh);
            }
            localStorage.setItem('g_token_expiry', expiry);
            localStorage.setItem('isAdminSession', 'true');

            this.isTokenValid = true;
            this.isAdmin = true;
            this.secureLoadAttempted = false;

            this.emit('authStatusChanged', { isAdmin: true, isTokenValid: true });
            this.emit('authSuccess');
            
            const resolvers = this.tokenResolvers;
            this.tokenResolvers = [];
            
            if (resolvers.length > 0) {
              console.log("Đã tự động gia hạn token ngầm thành công cho tác vụ đang chờ.");
              resolvers.forEach(r => r.resolve(token));
            } else {
              this.isSecureLoaded = false;
              this.isDataLoaded = false;
              this.loadData();
            }
          } catch (err) {
            console.error("Token exchange error:", err);
            this.emit('authError', err.message);
            this.isTokenValid = false;
            this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: false });
          }
        }
      });
      console.log("Google Auth GSI Code Client initialized successfully.");
      
      const token = localStorage.getItem('g_access_token');
      const expiry = localStorage.getItem('g_token_expiry');
      const now = Date.now();
      this.isTokenValid = !!(token && expiry && parseInt(expiry, 10) > now);
      this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: this.isTokenValid });
    } catch (e) {
      console.error("Error initializing Google Auth GSI:", e);
    }
  },

  handleGoogleLoginClick() {
    const clientId = localStorage.getItem('gClientId');
    if (!clientId) {
      this.emit('clientIdRequired');
      return;
    }

    if (!this.gCodeClient) {
      this.initGoogleAuth();
    }

    if (this.gCodeClient) {
      try {
        this.gCodeClient.requestCode();
      } catch (e) {
        console.error("Error requesting auth code:", e);
        this.emit('authError', "Lỗi xác thực Google. Vui lòng kiểm tra lại Client ID hoặc kết nối mạng.");
      }
    } else {
      this.emit('authError', "Không thể khởi tạo Client xác thực. Vui lòng tải lại trang.");
    }
  },

  promptInteractiveLogin() {
    if (confirm("Phiên đăng nhập Google đã hết hiệu lực. Nhấp OK để liên kết lại tài khoản Gmail và tự động hoàn thành lưu dữ liệu!")) {
      try {
        this.gCodeClient.requestCode();
      } catch (e) {
        console.error("Interactive login request failed:", e);
        const resolvers = this.tokenResolvers;
        this.tokenResolvers = [];
        resolvers.forEach(r => r.reject(e));
      }
    } else {
      const resolvers = this.tokenResolvers;
      this.tokenResolvers = [];
      resolvers.forEach(r => r.reject(new Error("Người dùng từ chối đăng nhập lại")));
    }
  },

  autoLoginOrSilentRefresh() {
    const token = localStorage.getItem('g_access_token');
    const expiry = localStorage.getItem('g_token_expiry');
    const now = Date.now();

    if (token && expiry && parseInt(expiry, 10) > now) {
      console.log("Found valid access token in LocalStorage. Expiry in:", Math.round((parseInt(expiry, 10) - now) / 1000), "s");
      this.isTokenValid = true;
      this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: true });
      this.loadData();
    } else {
      const refreshToken = localStorage.getItem('g_refresh_token');
      if (refreshToken) {
        console.log("Access token expired or missing. Refreshing using refresh token proxy...");
        const activeClientId = localStorage.getItem('gClientId') || '1088195961071-25r6rpvsfmoudokb75u0m2ugu8na0v0.apps.googleusercontent.com';
        fetch('/api/auth/refresh', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            refresh_token: refreshToken,
            client_id: activeClientId
          })
        })
        .then(res => {
          if (!res.ok) throw new Error("Failed to refresh token on startup");
          return res.json();
        })
        .then(tokenData => {
          const tokenVal = tokenData.access_token;
          const expiryVal = Date.now() + (tokenData.expires_in - 60) * 1000;
          localStorage.setItem('g_access_token', tokenVal);
          localStorage.setItem('g_token_expiry', expiryVal);
          this.isTokenValid = true;
          this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: true });
          this.loadData();
        })
        .catch(err => {
          console.warn("Auto token refresh failed on startup:", err);
          this.isTokenValid = false;
          this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: false });
        });
      } else {
        this.isTokenValid = false;
        this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: false });
      }
    }
  },

  ensureValidGoogleToken() {
    return new Promise((resolve, reject) => {
      const token = localStorage.getItem('g_access_token');
      const expiry = localStorage.getItem('g_token_expiry');
      const now = Date.now();

      if (token && expiry && parseInt(expiry, 10) > now + 300 * 1000) {
        return resolve(token);
      }

      this.tokenResolvers.push({ resolve, reject });

      if (this.tokenResolvers.length > 1) {
        return;
      }

      const refreshToken = localStorage.getItem('g_refresh_token');
      if (refreshToken) {
        console.log("Token expired or close to expiry. Refreshing using refresh token proxy...");
        const activeClientId = localStorage.getItem('gClientId') || '1088195961071-25r6rpvsfmoudokb75u0m2ugu8na0v0.apps.googleusercontent.com';
        fetch('/api/auth/refresh', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            refresh_token: refreshToken,
            client_id: activeClientId
          })
        })
        .then(res => {
          if (!res.ok) throw new Error("Failed to refresh token");
          return res.json();
        })
        .then(tokenData => {
          const newToken = tokenData.access_token;
          const newExpiry = Date.now() + (tokenData.expires_in - 60) * 1000;
          localStorage.setItem('g_access_token', newToken);
          localStorage.setItem('g_token_expiry', newExpiry);
          
          this.isTokenValid = true;
          this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: true });

          const resolvers = this.tokenResolvers;
          this.tokenResolvers = [];
          resolvers.forEach(r => r.resolve(newToken));
        })
        .catch(err => {
          console.error("Refresh token exchange failed:", err);
          this.promptInteractiveLogin();
        });
      } else {
        this.promptInteractiveLogin();
      }
    });
  },

  // Sheets Loading Logic
  async loadData() {
    const old = document.getElementById('_gs');
    if (old) old.remove();
    const oldAdmin = document.getElementById('_gs_admin');
    if (oldAdmin) oldAdmin.remove();

    let token = localStorage.getItem('g_access_token');
    let expiry = localStorage.getItem('g_token_expiry');
    const now = Date.now();
    let isTokenValid = !!(token && expiry && parseInt(expiry, 10) > now);

    if (this.isAdmin && !isTokenValid) {
      const refreshToken = localStorage.getItem('g_refresh_token');
      if (refreshToken) {
        console.log("Access token expired. Attempting silent refresh via server proxy...");
        try {
          const activeClientId = localStorage.getItem('gClientId') || '1088195961071-25r6rpvsfmoudokb75u0m2ugu8na0v0.apps.googleusercontent.com';
          const res = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              refresh_token: refreshToken,
              client_id: activeClientId
            })
          });
          if (res.ok) {
            const tokenData = await res.json();
            token = tokenData.access_token;
            expiry = Date.now() + (tokenData.expires_in - 60) * 1000;
            localStorage.setItem('g_access_token', token);
            localStorage.setItem('g_token_expiry', expiry);
            this.isTokenValid = true;
            isTokenValid = true;
            this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: true });
            console.log("Silent refresh succeeded on loadData.");
          } else {
            console.warn("Silent refresh failed on loadData, status:", res.status);
          }
        } catch (e) {
          console.error("Silent refresh error on loadData:", e);
        }
      }
    }

    if (this.isAdmin && !isTokenValid) {
      console.log("Admin accessed without valid Google token. Displaying Auth Screen...");
      this.emit('authRequired');
      return;
    }

    if (this.isAdmin && isTokenValid && !this.secureLoadAttempted) {
      console.log("Loading parallel Admin data...");
      this.secureLoadAttempted = true;
      this.emit('dataLoading', 'secure');

      const POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw';
      const SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE';

      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 seconds timeout

        const [sourceRes, poolRes] = await Promise.all([
          fetch(`https://sheets.googleapis.com/v4/spreadsheets/${SOURCE_SHEET_ID}/values/Source!A2:ZZ`, {
            headers: { 'Authorization': `Bearer ${token}` },
            signal: controller.signal
          }),
          fetch(`https://sheets.googleapis.com/v4/spreadsheets/${POOL_SHEET_ID}/values/Pool!A2:ZZ`, {
            headers: { 'Authorization': `Bearer ${token}` },
            signal: controller.signal
          })
        ]);

        clearTimeout(timeoutId);

        if (!sourceRes.ok || !poolRes.ok) {
          if (sourceRes.status === 401 || sourceRes.status === 403 || poolRes.status === 401 || poolRes.status === 403) {
            console.warn("OAuth token invalid or unauthorized. Cleared from storage.");
            localStorage.removeItem('g_access_token');
            localStorage.removeItem('g_token_expiry');
            this.isTokenValid = false;
            this.emit('authStatusChanged', { isAdmin: this.isAdmin, isTokenValid: false });
          }
          throw new Error(`Lỗi tải API Google Sheets (Source: ${sourceRes.status}, Pool: ${poolRes.status})`);
        }

        const sourceDataJson = await sourceRes.json();
        const poolDataJson = await poolRes.json();

        const sourceRows = sourceDataJson.values || [];
        const poolRows = poolDataJson.values || [];
        this.POOL_ROWS = poolRows;

        const fullList = sourceRows
          .map((sr, index) => {
            if (index === 0) return null; // Bỏ qua hàng tiêu đề
            if (!sr[3] && !sr[4]) return null;
            
            const targetRowNumber = index + 2;
            const dt = parseFloat(sr[5]) || 0;
            const gia = parseGia(sr[8]);
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
            const srSystemId = sr[37] || '';
            const srId = sr[3] || '';

            const poolRow = poolRows.find(pr => {
              const prSystemId = pr[72] || '';
              const prId = pr[55] || '';
              return (srSystemId && prSystemId === srSystemId) || 
                     (srId && prId === srId) ||
                     (srSystemId && prId === srSystemId);
            });

            const poolImgs = [];
            if (poolRow) {
              for (let c = 40; c <= 54; c++) {
                if (poolRow[c]) poolImgs.push(poolRow[c]);
              }
              for (let c = 83; c <= 92; c++) {
                if (poolRow[c]) poolImgs.push(poolRow[c]);
              }
            }

            const sourcePublicImgs = [
              sr[20], sr[21], sr[22], sr[23], sr[24],
              sr[25], sr[26], sr[27], sr[28], sr[29],
              sr[41], sr[42], sr[43], sr[44], sr[45]
            ].filter(Boolean);

            const allImgs = poolRow ? [
              ...poolImgs,
              ...sourcePublicImgs
            ] : sourcePublicImgs;
            const uniqueImgs = [...new Set(allImgs)];

            const p = {
              temp_id: index + 1,
              id: sr[3] || '',
              cu_phap: sr[1] || '',
              t: sr[4] || '',
              dt: sr[5] || '',
              tang: sr[6] || '',
              mat: sr[7] || '',
              gia: gia,
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
              m: cleanConsecutiveNewlines(sr[19] || ''),
              imgs: uniqueImgs,
              system_id: sr[37] || (index + 1).toString(),
              so_pn: sr[32] || '-',
              img_mat_tien: sr[38] || '',
              ten_duong: sr[34] || '',
              
              original_row_data: sr,
              source_row_index: targetRowNumber
            };
            p.dai_nha = getDaiNha(p);

            if (poolRow) {
              p.raw_ten_dau_chu = poolRow[75] || '';
              p.raw_dt_dau_chu = poolRow[74] || '';
              p.raw_link_fb = poolRow[76] || '';
              p.raw_noi_dung_chinh = String(poolRow[9] || '').replace(/\r\n|\r|\n/g, ' ');
              p.raw_mo_ta_chi_tiet = cleanConsecutiveNewlines(poolRow[10] || '');
              p.raw_sodo1 = poolRow[27] || '';
              p.raw_sodo2 = poolRow[28] || '';
              p.raw_sodo3 = poolRow[80] || '';
              p.raw_sodo4 = poolRow[81] || '';
              p.raw_sodo5 = poolRow[82] || '';
              p.raw_so_nha = poolRow[6] || '';
              p.raw_ten_duong = poolRow[5] || '';
              p.raw_dt_thuc_te = poolRow[13] || '';
              p.raw_dt_tren_so = poolRow[14] || '';
              p.raw_gia_chao = poolRow[11] || poolRow[58] || '';
              p.raw_so_tang = poolRow[15] || '';
              p.raw_mat_tien = poolRow[16] || '';
              p.raw_duong_truoc_nha = poolRow[60] || '';
              p.raw_do_rong_hem = poolRow[61] || '';
              p.raw_so_pn = poolRow[64] || '';
              p.raw_so_wc = poolRow[65] || '';
              p.raw_tieu_de_public = poolRow[56] || '';
              p.raw_mo_ta_public = poolRow[57] || '';
              p.raw_phan_loai = poolRow[7] || '';
              p.pool_row_index = poolRows.indexOf(poolRow) + 2;
              p.pool_row_data = poolRow;
            } else {
              p.raw_ten_dau_chu = '';
              p.raw_dt_dau_chu = '';
              p.raw_link_fb = '';
              p.raw_noi_dung_chinh = '';
              p.raw_mo_ta_chi_tiet = '';
              p.raw_sodo1 = '';
              p.raw_sodo2 = '';
              p.raw_sodo3 = '';
              p.raw_sodo4 = '';
              p.raw_sodo5 = '';
              p.raw_so_nha = '';
              p.raw_ten_duong = p.ten_duong || '';
              p.raw_dt_thuc_te = p.dt || '';
              p.raw_dt_tren_so = p.dt || '';
              p.raw_gia_chao = p.gia || '';
              p.raw_so_tang = p.tang || '';
              p.raw_mat_tien = p.mat || '';
              p.raw_duong_truoc_nha = p.duong_truoc_nha || '';
              p.raw_do_rong_hem = p.rong_hem || '';
              p.raw_so_pn = p.so_pn || '';
              p.raw_so_wc = '';
              p.raw_tieu_de_public = '';
              p.raw_mo_ta_public = '';
              p.raw_phan_loai = '';
              p.pool_row_index = null;
              p.pool_row_data = null;
            }

            return p;
          })
          .filter(Boolean);

        this.isSecureLoaded = true;
        this.DATA = fullList;
        this.isDataLoaded = true;
        this.emit('rawDataLoaded', fullList);
      } catch (err) {
        console.error("Error loading secure admin data, falling back to public:", err);
        this.loadPublicDataFallback();
      }
    } else {
      if (this.isSecureLoaded) {
        console.log("Secure admin data already loaded, skipping public fallback.");
        return;
      }
      if (this.isDataLoaded) {
        console.log("Data already loaded, skipping public reload.");
        return;
      }
      this.loadPublicDataFallback();
    }
  },

  loadPublicDataFallback() {
    this.emit('dataLoading', 'public');
    const SHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0';

    window.__gsCallback = (response) => {
      try {
        const rows = response.table.rows;
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
            
            const p = {
              temp_id: index + 1,
              id: cv(r.c[0]),
              cu_phap: '',
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
                cv(r.c[22]), cv(r.c[23]), cv(r.c[24]), cv(r.c[25]), cv(r.c[26]),
                cv(r.c[38]), cv(r.c[39]), cv(r.c[40]), cv(r.c[41]), cv(r.c[42])
              ].filter(Boolean),
              system_id: cv(r.c[34]) || (index + 1).toString(),
              so_pn: cv(r.c[29]) || '-',
              img_mat_tien: cv(r.c[35]) || ''
            };
            p.dai_nha = getDaiNha(p);
            return p;
          });

        this.DATA = fullList;
        this.isDataLoaded = true;
        this.emit('rawDataLoaded', fullList);
        this.emit('publicDataLoaded');
      } catch (e) {
        this.emit('dataLoadError', 'Lỗi parse dữ liệu: ' + e.message);
      }
    };

    const s = document.createElement('script');
    s.id = '_gs';
    s.src = `https://docs.google.com/spreadsheets/d/${SHEET_ID}/gviz/tq?tqx=out:json;responseHandler:__gsCallback`;
    s.onerror = () => this.emit('dataLoadError', 'Không kết nối được Google Sheets. Kiểm tra SHEET_ID và quyền truy cập.');
    document.head.appendChild(s);
  }
};

// Map global getters/setters to window object for compatibility
Object.defineProperty(window, 'DATA', {
  get() { return LegoState.DATA; },
  set(val) { LegoState.DATA = val; }
});
Object.defineProperty(window, 'POOL_ROWS', {
  get() { return LegoState.POOL_ROWS; },
  set(val) { LegoState.POOL_ROWS = val; }
});
Object.defineProperty(window, 'isAdmin', {
  get() { return LegoState.isAdmin; },
  set(val) { 
    const changed = LegoState.isAdmin !== val;
    LegoState.isAdmin = val;
    if (changed) {
      LegoState.emit('authStatusChanged', { isAdmin: LegoState.isAdmin, isTokenValid: LegoState.isTokenValid });
    }
  }
});
Object.defineProperty(window, 'isTokenValid', {
  get() { return LegoState.isTokenValid; },
  set(val) {
    const changed = LegoState.isTokenValid !== val;
    LegoState.isTokenValid = val;
    if (changed) {
      LegoState.emit('authStatusChanged', { isAdmin: LegoState.isAdmin, isTokenValid: LegoState.isTokenValid });
    }
  }
});
Object.defineProperty(window, 'gCodeClient', {
  get() { return LegoState.gCodeClient; },
  set(val) { LegoState.gCodeClient = val; }
});
Object.defineProperty(window, 'isSecureLoaded', {
  get() { return LegoState.isSecureLoaded; },
  set(val) { LegoState.isSecureLoaded = val; }
});
Object.defineProperty(window, 'isDataLoaded', {
  get() { return LegoState.isDataLoaded; },
  set(val) { LegoState.isDataLoaded = val; }
});
Object.defineProperty(window, 'secureLoadAttempted', {
  get() { return LegoState.secureLoadAttempted; },
  set(val) { LegoState.secureLoadAttempted = val; }
});
Object.defineProperty(window, 'tokenResolvers', {
  get() { return LegoState.tokenResolvers; },
  set(val) { LegoState.tokenResolvers = val; }
});

// Initialize State
LegoState.init();

// Export to window
window.LegoState = LegoState;

// Keep old references intact for compatibility
window.initGoogleAuth = () => LegoState.initGoogleAuth();
window.handleGoogleLoginClick = () => LegoState.handleGoogleLoginClick();
window.autoLoginOrSilentRefresh = () => LegoState.autoLoginOrSilentRefresh();
window.ensureValidGoogleToken = () => LegoState.ensureValidGoogleToken();
window.loadData = () => LegoState.loadData();
window.loadPublicDataFallback = () => LegoState.loadPublicDataFallback();
