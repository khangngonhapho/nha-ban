const fs = require('fs');
const path = require('path');

const SHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0';

module.exports = async (req, res) => {
  const urlObj = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = urlObj.pathname;

  // 1. Endpoint exchange authorization code for tokens
  if (pathname === '/api/auth/token') {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method Not Allowed' });
    }

    let body = {};
    try {
      body = req.body;
      if (typeof body === 'string') body = JSON.parse(body);
    } catch (e) {}

    if (!body || !body.code) {
      try {
        const buffers = [];
        for await (const chunk of req) {
          buffers.push(chunk);
        }
        const data = Buffer.concat(buffers).toString();
        body = JSON.parse(data);
      } catch (e) {
        return res.status(400).json({ error: 'Bad Request: Missing JSON body' });
      }
    }

    const { code, redirect_uri } = body;
    if (!code) {
      return res.status(400).json({ error: 'Bad Request: Missing authorization code' });
    }

    const CLIENT_ID = '1088195961071-25r6rpvsfmoudokb75u0m2ugu8na0v0.apps.googleusercontent.com';
    const CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;

    if (!CLIENT_SECRET) {
      return res.status(500).json({ error: 'Server configuration error: GOOGLE_CLIENT_SECRET environment variable is missing' });
    }

    try {
      const response = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          code,
          client_id: CLIENT_ID,
          client_secret: CLIENT_SECRET,
          redirect_uri: redirect_uri || 'postmessage',
          grant_type: 'authorization_code'
        }).toString()
      });

      const tokenData = await response.json();
      if (!response.ok) {
        return res.status(response.status).json(tokenData);
      }

      return res.status(200).json(tokenData);
    } catch (err) {
      console.error('Error exchanging code for token:', err);
      return res.status(500).json({ error: 'Internal Server Error during token exchange' });
    }
  }

  // 2. Endpoint refresh access token using refresh_token
  if (pathname === '/api/auth/refresh') {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method Not Allowed' });
    }

    let body = {};
    try {
      body = req.body;
      if (typeof body === 'string') body = JSON.parse(body);
    } catch (e) {}

    if (!body || !body.refresh_token) {
      try {
        const buffers = [];
        for await (const chunk of req) {
          buffers.push(chunk);
        }
        const data = Buffer.concat(buffers).toString();
        body = JSON.parse(data);
      } catch (e) {
        return res.status(400).json({ error: 'Bad Request: Missing JSON body' });
      }
    }

    const { refresh_token } = body;
    if (!refresh_token) {
      return res.status(400).json({ error: 'Bad Request: Missing refresh token' });
    }

    const CLIENT_ID = '1088195961071-25r6rpvsfmoudokb75u0m2ugu8na0v0.apps.googleusercontent.com';
    const CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET;

    if (!CLIENT_SECRET) {
      return res.status(500).json({ error: 'Server configuration error: GOOGLE_CLIENT_SECRET environment variable is missing' });
    }

    try {
      const response = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          client_id: CLIENT_ID,
          client_secret: CLIENT_SECRET,
          refresh_token,
          grant_type: 'refresh_token'
        }).toString()
      });

      const tokenData = await response.json();
      if (!response.ok) {
        return res.status(response.status).json(tokenData);
      }

      return res.status(200).json(tokenData);
    } catch (err) {
      console.error('Error refreshing token:', err);
      return res.status(500).json({ error: 'Internal Server Error during token refresh' });
    }
  }

  // Xử lý secure API endpoint trung gian lấy ảnh mặt tiền
  if (pathname === '/api/get-facade-images') {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Unauthorized: Missing or invalid token' });
    }

    const token = authHeader.split(' ')[1];
    const PRIVATE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE';
    const range = 'Source!D2:AM';
    const url = `https://sheets.googleapis.com/v4/spreadsheets/${PRIVATE_SHEET_ID}/values/${encodeURIComponent(range)}`;

    try {
      const sheetsResponse = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!sheetsResponse.ok) {
        return res.status(sheetsResponse.status).json({ error: `Google API returned status ${sheetsResponse.status}` });
      }

      const data = await sheetsResponse.json();
      return res.status(200).json(data);
    } catch (err) {
      console.error('Error fetching facade images in serverless function:', err);
      return res.status(500).json({ error: 'Internal Server Error fetching Google Sheets API' });
    }
  }

  let html = '';
  try {
    html = fs.readFileSync(path.join(process.cwd(), 'index.html'), 'utf8');
  } catch (err) {
    console.error('Error reading index.html:', err);
    return res.status(500).send('Internal Server Error: Missing index.html');
  }

  const s = req.query.s;
  if (s) {
    try {
      const sheetUrl = `https://docs.google.com/spreadsheets/d/${SHEET_ID}/gviz/tq?tqx=out:json`;
      const response = await fetch(sheetUrl);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const text = await response.text();
      const startIdx = text.indexOf('(') + 1;
      const endIdx = text.lastIndexOf(')');
      if (startIdx <= 0 || endIdx <= 0) throw new Error('Invalid JSONP format from Google Sheets');
      
      const jsonStr = text.substring(startIdx, endIdx);
      const data = JSON.parse(jsonStr);
      const rows = data.table.rows;
      
      const cv = (cell) => cell ? (cell.v ?? cell.f ?? '') : '';
      const fullList = rows
        .filter(r => r.c[0] && r.c[0].v)
        .map((r, index) => {
          return {
            id: cv(r.c[0]),
            t: cv(r.c[1]),
            dt: cv(r.c[2]),
            tang: cv(r.c[3]),
            gia: cv(r.c[5]),
            phuong: cv(r.c[7]),
            duong_truoc_nha: cv(r.c[10]),
            imgs: [
              cv(r.c[17]), cv(r.c[18]), cv(r.c[19]), cv(r.c[20]), cv(r.c[21]), 
              cv(r.c[22]), cv(r.c[23]), cv(r.c[24]), cv(r.c[25]), cv(r.c[26])
            ].filter(Boolean),
            system_id: cv(r.c[34]) || (index + 1).toString()
          };
        });

      // Support single share id
      const tk = s.split(',')[0].trim(); // Get first id if multiple comma-separated
      let house = null;
      if (tk.startsWith('SYS-')) {
        house = fullList.find(h => h.system_id === tk);
      } else if (/^\d+$/.test(tk)) {
        const idx = parseInt(tk, 10) - 1;
        house = fullList[idx];
      } else {
        house = fullList.find(h => String(h.id).toLowerCase() === tk.toLowerCase());
      }

      if (house) {
        const cleanTitle = house.t || 'Khang Ngô Nhà Phố';
        const cleanDesc = `#${house.id} · Diện tích: ${house.dt}m², ${house.tang} tầng, Đường ${house.duong_truoc_nha}, P.${house.phuong}. Giá bán: ${house.gia} tỷ VND. Liên hệ ngay!`;
        let cleanImg = house.imgs[0] || 'https://khangngonhapho.github.io/nha-ban/avatarKhangNgo.jpg';
        
        if (cleanImg.includes('drive.google.com')) {
          const m1 = cleanImg.match(/drive\.google\.com\/file\/d\/([^/?\s]+)/);
          if (m1) {
            cleanImg = `https://drive.google.com/thumbnail?id=${m1[1]}&sz=w800`;
          } else {
            const m2 = cleanImg.match(/[?&]id=([^&\s]+)/);
            if (m2) {
              cleanImg = `https://drive.google.com/thumbnail?id=${m2[1]}&sz=w800`;
            }
          }
        }

        html = html.replace(/<title>[^<]*<\/title>/i, `<title>${cleanTitle}</title>`);
        html = html.replace(/<meta[^>]*property="og:title"[^>]*content="[^"]*"/i, `<meta property="og:title" content="${cleanTitle}"`);
        html = html.replace(/<meta[^>]*property="og:description"[^>]*content="[^"]*"/i, `<meta property="og:description" content="${cleanDesc}"`);
        html = html.replace(/<meta[^>]*property="og:image"[^>]*content="[^"]*"/i, `<meta property="og:image" content="${cleanImg}"`);
      }
    } catch (err) {
      console.error('Error in serverless dynamic meta injection:', err);
      // Fallback gracefully to original html
    }
  }

  // GIẢI MÃ THAM SỐ C VÀ TIÊM ĐỘNG TIÊU ĐỀ TÙY CHỈNH (US-033 SERVER-SIDE)
  const c = req.query.c;
  if (c) {
    try {
      let safeToken = c.replace(/ /g, '+');
      // Khôi phục padding = cho Base64URL nếu bị thiếu
      while (safeToken.length % 4) {
        safeToken += '=';
      }
      const decoded = Buffer.from(safeToken, 'base64').toString('utf8');
      const parts = decoded.split("|").map(p => p.trim());
      const customPageTitle = parts[2] || "";
      if (customPageTitle) {
        html = html.replace(/<title>[^<]*<\/title>/i, `<title>${customPageTitle}</title>`);
        html = html.replace(/<meta[^>]*property="og:title"[^>]*content="[^"]*"/i, `<meta property="og:title" content="${customPageTitle}"`);
      } else {
        // Chỉ ghi đè nếu chưa bị thay đổi bởi căn nhà (giữ nguyên tiêu đề mặc định giỏ hàng nếu không có s)
        if (!req.query.s) {
          html = html.replace(/<title>[^<]*<\/title>/i, `<title>Giỏ hàng độc quyền - Khang Ngô Nhà Phố</title>`);
          html = html.replace(/<meta[^>]*property="og:title"[^>]*content="[^"]*"/i, `<meta property="og:title" content="Giỏ Hàng Độc Quyền - Khang Ngô Nhà Phố"`);
        }
      }
    } catch (e) {
      console.error('Error decoding c parameter in serverless:', e);
    }
  }

  res.status(200).setHeader('Content-Type', 'text/html; charset=utf-8').send(html);
};
