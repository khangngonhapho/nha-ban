const fs = require('fs');
const path = require('path');

const SHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0';

module.exports = async (req, res) => {
  let html = '';
  try {
    html = fs.readFileSync(path.join(process.cwd(), 'index.html'), 'utf8');
  } catch (err) {
    console.error('Error reading index.html:', err);
    return res.status(500).send('Internal Server Error: Missing index.html');
  }

  const s = req.query.s;
  if (!s) {
    return res.status(200).setHeader('Content-Type', 'text/html; charset=utf-8').send(html);
  }

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

  res.status(200).setHeader('Content-Type', 'text/html; charset=utf-8').send(html);
};
