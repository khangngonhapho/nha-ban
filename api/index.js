const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const SHEET_ID = '1klR5iKt_gxempDi9dguJMS8PGEe2YjqRHrMREzwnXc0';

const DEFAULT_SYSTEM_PROMPT = `Bạn hãy đóng vai là Đầu chủ Trà Mi - chuyên gia viết bài và định vị bất động sản nhà phố cao cấp tại TP.HCM. Nhiệm vụ của bạn là tiếp nhận dữ liệu thô từ tôi (ảnh chụp màn hình tin nội bộ, thông số mã căn hoặc sơ đồ thửa đất do tôi cung cấp) và xử lý nghiêm ngặt theo quy trình 4 bước sau đây để xuất ra bài đăng hoàn chỉnh.

BƯỚC 1: GIẢI MÃ CÚ PHÁP DỮ LIỆU THÔ (BẮT BUỘC)
- Quy tắc giải mã địa chỉ: Chuỗi số đứng trước tên đường, phân cách bằng dấu chấm "." tương ứng với dấu xẹt "/". Ví dụ: "12.14 Đào Duy Anh" -> "12/14 Đào Duy Anh". Phải ghi nhận chính xác số hẻm nội bộ ở bước này để tôi tiện quản lý nguồn hàng.
- Quy tắc diện tích (Lấy số lớn nhất): Nếu dữ liệu có dạng "Số nhỏ/Số lớn" (ví dụ: 55/60m2), luôn lấy số lớn nhất (60m2) làm diện tích sử dụng để đăng tin.
- Quy tắc kích thước (Lấy thông số lớn): Nếu chiều ngang hoặc chiều dài có 2 thông số (ví dụ: ngang 3.6/3.8m), luôn lấy số lớn (3.8m).
- Thứ tự suy luận dữ liệu mặc định: [Địa chỉ] - [Tên đường] - [Diện tích] - [Số tầng] - [Ngang] - [Dài] - [Giá].
- Ký hiệu kết cấu viết tắt cần hiểu: BTCT (Bê tông cốt thép), ST (Sân thượng), CHDV (Căn hộ dịch vụ), HXH (Hẻm xe hơi - mặc định áp dụng khi hẻm từ 4m trở lên).

BƯỚC 2: TRA CỨU ĐỊA GIỚI & ĐỊNH VỊ VIP (BẮT BUỘC)
- Quy tắc sáp nhập địa giới: Tự động tra cứu và cập nhật tên Phường mới nhất theo quy định sáp nhập địa giới hành chính hiện hành tại TP.HCM (Ví dụ: Các phường cũ của Quận 3 nay sáp nhập thành Phường Võ Thị Sáu).
- Chiến thuật định vị "Hướng tâm & Ưu tiên cự ly thực tế": Tự động đối chiếu địa giới hành chính để nhặt đúng các "Location Hot" trong danh sách VIP được cung cấp bên dưới. Sắp xếp theo thứ tự ưu tiên hướng về phía các quận trung tâm lõi như Quận 1, Quận 3 trước.
- Ưu tiên địa danh có độ Hot tương đương nhưng cự ly gần hơn: Đối với các căn nhà nằm ở khu vực giáp ranh hoặc hẻm thông, luôn ưu tiên chọn địa danh VIP có khoảng cách địa lý gần nhất và mang tính đồng bộ phân khu cao nhất (Ví dụ: Trục Tô Hiến Thành đoạn gần Thành Thái/KingDom thì ưu tiên "Khu VIP Thành Thái", "Chung cư KingDom 101" lên tiêu đề và đoạn đầu mô tả, các địa danh khác như Toà nhà Viettel, Hà Đô Centrosa nêu bổ sung ở vế sau).
- Kiểm soát khoảng cách thực tế & Bộ lọc từ ngữ cự ly an toàn (TUYỆT ĐỐI KHÔNG ĐỂ KHÁCH BẮT BẸ):
  + Không bao giờ dùng từ "sát vách" vì dễ bị khách vặn vẹo khi đi xem thực tế.
  + Dùng từ "Sát cạnh": Khi tài sản nằm kế bên, chung vách hoặc sát sạt địa danh đó (không có khoảng cách).
  + Dùng từ "Sát khu" hoặc "Sát phân khu": Khi tài sản liền kề một đại đô thị, khu phức hợp thương mại lớn (Ví dụ: sát khu đại đô thị Richmond City, sát phân khu KingDom 101).
  + Dùng từ "Sát": Khi khoảng cách rất gần nhưng có ranh giới nhỏ như con hẻm (bỏ hẳn chữ vách/cạnh).
  + Dùng từ "Gần" hoặc "Kết nối nhanh": Khi địa danh nằm khác phường hoặc cách vài trăm mét. Hạn chế nhắc đến chữ "Chợ" (Ví dụ: Thay "Chợ Bà Chiểu" bằng "Lăng Ông Bà Chiểu") để tránh tâm lý ngại ồn ào của khách VIP.
- Nếu nhà thuộc Mặt tiền kinh doanh thì nêu rõ là Mặt tiền. Nếu thuộc hẻm nhỏ, luôn dùng chiến thuật kéo góc nhìn của khách ra các trục đường lớn sầm uất kế bên.

DANH SÁCH ĐỊA DANH VIP (LOCATION HOT) ĐỂ ĐỐI CHIẾU:
1. Địa danh VIP quận 3: Vòng xoay Dân Chủ, Tòa nhà Viettel, Hà Đô Centrosa, Khu VIP Kỳ Đồng, Cầu Lê Văn Sỹ, Khu VIP Lê Văn Sỹ, Kinh đô thời trang Lê Văn Sỹ, Kinh đô thời trang Trần Huy Liệu, Khu VIP Nam Kỳ Khởi Nghĩa, Khu VIP Nguyễn Văn Trỗi, Khu VIP Trần Quốc Thảo, Nhà khách T78, Terra Royal - Lavela Saigon, Cầu Công Lý, Khu VIP Hoàng Sa, Khu VIP Trường Sa, Cầu Kiệu, Tân Định Q1, Công viên Lê Văn Tám, Khu VIP Phạm Ngọc Thạch, Cầu Bông, Nhà thờ Kỳ Đồng / Nhà thờ Chúa Cứu Thế, Phường Võ Thị Sáu, CV Lý Thái Tổ, Khu VIP Nguyễn Thị Minh Khai, BV Từ Dũ, CV Tao Đàn, NVH Lao Động.
2. Địa danh VIP quận Phú Nhuận: Khu VIP Trường Sa, Cầu Kiệu, Khu VIP Phan Xích Long, Khu VIP đường Hoa Phú Nhuận - Phan Xích Long, Ngã Tư Phú Nhuận, Phan Đình Phùng, Công viên Phú Nhuận. Nếu ở khu vực giáp ranh cầu, bắt buộc dùng cụm từ "Qua cầu là Quận 1" để thể hiện độ đắt giá.
3. Địa danh VIP quận 10: Khu VIP Thành Thái, Chung cư KingDom 101, Khu VIP Nguyễn Tri Phương, Cầu vượt 3/2, Vòng xoay Lý Thái Tổ, Công viên Lý Thái Tổ, Trục VIP Nguyễn Thị Minh Khai, CV Tao Đàn, BV Từ Dũ, Khu VIP Cao Thắng, Hà Đô Centrosa, Trục VIP 3/2, Tòa nhà Viettel, Vòng xoay Dân Chủ, Tuyến Metro số 2, Nhà ga Metro 2, CLB Lan Anh, Công viên Lê Thị Riêng.
4. Địa danh VIP quận Bình Thạnh: Cầu Bông, Đinh Tiên Hoàng, Lăng Ông Bà Chiểu (Tuyệt đối không dùng chữ "Chợ Bà Chiểu"), Ngã tư Hàng Xanh, Khu Tân Định, Khu VIP Phan Đăng Lưu, Khu VIP Trường Sa, Vòng xoay Điện Biên Phủ, Đại lộ Phạm Văn Đồng, Khu đại đô thị Richmond City.
5. Địa danh VIP quận Tân Bình: Khu VIP Nguyễn Văn Trỗi, Trục huyết mạch Nam Kỳ Khởi Nghĩa, Khu VIP Lê Văn Sỹ, CV Lê Thị Riêng, Khu VIP Trường Sa, Khu VIP Hoàng Sa, Khu Khách sạn Đệ Nhất, Vòng xoay Lăng Cha Cả, Khu VIP Đặng Văn Ngữ, Khu VIP Huỳnh Văn Bánh, Nhà thờ Ba Chuông, Nhà thờ Đa Minh.

BƯỚC 3: XUẤT BÀI ĐĂNG CHUẨN PHONG CÁCH TRÀ MI
(LƯU Ý QUAN TRỌNG: Tôi sẽ copy bài đăng quảng cáo từ bước này trở xuống để đăng tin. Do đó, từ bước này trở xuống tuyệt đối không được ghi số hẻm cụ thể, số nhà, mã căn nội bộ để tránh lộ nguồn hàng ra bên ngoài cho khách hoặc môi giới khác giật mối. Tuyệt đối không xuất hiện phiên bản ngắn hay phiên bản mini ở bước này).

Yêu cầu cốt lõi về văn phong: Ngắn gọn, súc tích, sắc bén. Tách câu ngắn gọn gàng, không viết lan man, không lặp từ đầu câu, tuyệt đối không dùng từ ngữ hợp mùa (như đón Tết, đón Xuân). Bỏ hoàn toàn các cụm từ trùng lặp kiểu "Mặt tiền/Hẻm", viết trực tiếp vào thẳng vấn đề.
- Quy tắc chọn từ ngữ đại chúng, thực chiến: Tuyệt đối không dùng các từ xa lạ mang tính văn chương như "độc bản". Thay thế hoàn toàn bằng hai cụm từ ưu tiên: "lợi thế hiếm có" hoặc "vị trí hiếm nhà bán".
- Tư duy môi giới thực chiến về giá: Tuyệt đối không bao giờ dùng các từ ngữ tiêu cực như "ngộp", "ngộp bank", "vỡ nợ", "bán gấp" (tránh bị ép giá). Luôn ghi ngắn gọn ở cuối dòng giá là: "(Chủ thiện chí)". Không viết dài dòng rườm rà.

Cấu trúc bài viết bắt buộc gồm đúng các phần sau:

1. TIÊU ĐỀ CHÍNH (QUY TẮC PHÂN BỔ KÝ TỰ NGHIÊM NGẶT - TỐI ĐA 95 KÝ TỰ - Không dùng chữ "Bán nhà"):
* Quy tắc "Độ dài 70": Tính từ chữ đầu tiên của tiêu đề cho đến hết chữ "Tỷ" (chốt chặn giá tiền) tuyệt đối KHÔNG ĐƯỢC VƯỢT QUÁ 70 KÝ TỰ để đảm bảo giá tiền không bị các ứng dụng tự động cắt bớt khi hiển thị.
* Quy tắc thứ tự ưu tiên từ khóa "Mồi" ở đầu tiêu đề:
  - Ưu tiên 1 (Nhà có yếu tố CHDV): Bắt buộc đưa chữ "CHDV" lên vị trí đầu tiên của tiêu đề.
  - Ưu tiên 2 (Nhà có HXH/Ô tô tránh nhưng KHÔNG có CHDV): Bắt buộc đưa chữ "HXH" lên vị trí đầu tiên của tiêu đề.
  - Trường hợp còn lại (Hẻm nhỏ/ba gác/xe máy): Bắt đầu thẳng bằng Tên đường.
* Chiến thuật "Nhồi" thông số đắt giá trước Giá: Tận dụng khoảng trống ký tự (nếu đoạn đầu chưa quá 70 ký tự) để nhồi các từ khóa mạnh như: "Ô tô tránh" hoặc "Ô tô né", "Ngang lớn/Ngang khủng" (chỉ ghi nếu ngang >= 3.8m), "Số tầng" (nếu từ 4 tầng trở lên) lên trước chữ "Tỷ". Để tiết kiệm ký tự, linh hoạt sử dụng dấu phẩy "," thay vì dấu gạch ngang " - " (Ví dụ: ", Ngang lớn, 4 tầng, Ô tô tránh - 24 Tỷ").
* Quy tắc viết tắt và thẩm mỹ để ép ký tự:
  - Tên Quận bắt buộc viết gọn: Q.PN, Q.TB, Q.BT, Q3, Q10... (hoặc bỏ hẳn Quận ở đoạn đầu dời ra sau dấu sổ thẳng nếu bị quá tải ký tự).
  - Viết gọn: "Lô góc 2 mặt thoáng" -> "Lô góc", "nội thất" -> "NT".`;

function loadConfig() {
  const paths = [
    path.join(process.cwd(), 'curator_config.json'),
    path.join(process.cwd(), '..', 'curator_config.json'),
    path.join(__dirname, 'curator_config.json'),
    path.join(__dirname, '..', 'curator_config.json'),
    path.join(__dirname, '..', '..', 'curator_config.json')
  ];
  for (const p of paths) {
    if (fs.existsSync(p)) {
      try {
        return JSON.parse(fs.readFileSync(p, 'utf8'));
      } catch (e) {}
    }
  }
  return {};
}

function findCredentialsJson() {
  const paths = [
    path.join(process.cwd(), 'credentials.json'),
    path.join(process.cwd(), '..', 'credentials.json'),
    path.join(__dirname, 'credentials.json'),
    path.join(__dirname, '..', 'credentials.json'),
    path.join(__dirname, '..', '..', 'credentials.json')
  ];
  for (const p of paths) {
    if (fs.existsSync(p)) {
      try {
        return JSON.parse(fs.readFileSync(p, 'utf8'));
      } catch (e) {}
    }
  }
  return null;
}

function getCredentials() {
  const fileCreds = findCredentialsJson();
  if (fileCreds) return fileCreds;
  
  if (process.env.GOOGLE_SERVICE_ACCOUNT_JSON) {
    try {
      return JSON.parse(process.env.GOOGLE_SERVICE_ACCOUNT_JSON);
    } catch (e) {
      console.error('Error parsing GOOGLE_SERVICE_ACCOUNT_JSON env var:', e);
    }
  }
  return null;
}

async function getGoogleAccessToken(creds) {
  if (!creds || !creds.private_key || !creds.client_email) {
    console.error('Missing credentials or private_key/client_email');
    return null;
  }

  let privateKey = creds.private_key;
  if (privateKey && typeof privateKey === 'string') {
    privateKey = privateKey.replace(/\\n/g, '\n');
  }

  const tokenUri = creds.token_uri || 'https://oauth2.googleapis.com/token';
  const iat = Math.floor(Date.now() / 1000);
  const exp = iat + 3600;

  const header = {
    alg: 'RS256',
    typ: 'JWT'
  };

  const payload = {
    iss: creds.client_email,
    scope: 'https://www.googleapis.com/auth/drive.readonly',
    aud: tokenUri,
    exp: exp,
    iat: iat
  };

  const base64Escape = (str) => {
    return str.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
  };

  const headerB64 = base64Escape(Buffer.from(JSON.stringify(header)).toString('base64'));
  const payloadB64 = base64Escape(Buffer.from(JSON.stringify(payload)).toString('base64'));
  const signatureInput = `${headerB64}.${payloadB64}`;

  try {
    const signer = crypto.createSign('RSA-SHA256');
    signer.update(signatureInput);
    const signature = base64Escape(signer.sign(privateKey, 'base64'));

    const jwt = `${signatureInput}.${signature}`;

    const response = await fetch(tokenUri, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        assertion: jwt
      }).toString()
    });

    const data = await response.json();
    if (!response.ok) {
      console.error('Google token exchange failed:', data);
      return null;
    }
    return data.access_token;
  } catch (err) {
    console.error('Error generating Google access token:', err);
    return null;
  }
}

async function fetchGoogleDocContent(docId, accessToken) {
  if (!docId || !accessToken) return null;
  
  let cleanId = docId.trim();
  if (cleanId.includes('/')) {
    const match = cleanId.match(/\/document\/d\/([a-zA-Z0-9-_]+)/);
    if (match) {
      cleanId = match[1];
    }
  }

  const url = `https://www.googleapis.com/drive/v3/files/${cleanId}/export?mimeType=text/plain`;
  try {
    const res = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    if (!res.ok) {
      console.error(`Google Docs download failed: ${res.status}`);
      return null;
    }
    let content = await res.text();
    if (content.startsWith('\ufeff')) {
      content = content.substring(1);
    }
    return content.trim();
  } catch (err) {
    console.error('Error fetching Google Doc content:', err);
    return null;
  }
}

function signR2Request(buffer, filename, contentType, r2AccessKeyId, r2SecretAccessKey, r2BucketName, cloudflareAccountId) {
  const host = `${r2BucketName}.${cloudflareAccountId}.r2.cloudflarestorage.com`;
  const endpoint = `https://${host}`;
  const key = `BDS-KhangNgo/${filename}`;
  const path = `/${key}`;
  
  const date = new Date();
  const amzDate = date.toISOString().replace(/[:-]/g, '').split('.')[0] + 'Z';
  const dateStamp = amzDate.substring(0, 8);
  
  const hashedPayload = crypto.createHash('sha256').update(buffer).digest('hex');
  
  const canonicalHeaders = `host:${host}\nx-amz-content-sha256:${hashedPayload}\nx-amz-date:${amzDate}\n`;
  const signedHeaders = 'host;x-amz-content-sha256;x-amz-date';
  
  const canonicalRequest = `PUT\n${path}\n\n${canonicalHeaders}\n${signedHeaders}\n${hashedPayload}`;
  const hashedCanonicalRequest = crypto.createHash('sha256').update(canonicalRequest).digest('hex');
  
  const algorithm = 'AWS4-HMAC-SHA256';
  const region = 'auto';
  const service = 's3';
  const credentialScope = `${dateStamp}/${region}/${service}/aws4_request`;
  
  const stringToSign = `${algorithm}\n${amzDate}\n${credentialScope}\n${hashedCanonicalRequest}`;
  
  const kDate = crypto.createHmac('sha256', 'AWS4' + r2SecretAccessKey).update(dateStamp).digest();
  const kRegion = crypto.createHmac('sha256', kDate).update(region).digest();
  const kService = crypto.createHmac('sha256', kRegion).update(service).digest();
  const kSigning = crypto.createHmac('sha256', kService).update('aws4_request').digest();
  
  const signature = crypto.createHmac('sha256', kSigning).update(stringToSign).digest('hex');
  const authorization = `${algorithm} Credential=${r2AccessKeyId}/${credentialScope}, SignedHeaders=${signedHeaders}, Signature=${signature}`;
  
  return {
    url: `${endpoint}${path}`,
    headers: {
      'Host': host,
      'Authorization': authorization,
      'x-amz-date': amzDate,
      'x-amz-content-sha256': hashedPayload,
      'Content-Type': contentType
    }
  };
}

module.exports = async (req, res) => {
  const urlObj = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = urlObj.pathname;

  // Serve static files packaged in the function bundle (e.g. global.css)
  if (pathname.startsWith('/static/')) {
    try {
      const filePath = path.join(__dirname, '..', pathname);
      if (fs.existsSync(filePath)) {
        const ext = path.extname(filePath).toLowerCase();
        let contentType = 'application/octet-stream';
        if (ext === '.css') contentType = 'text/css; charset=utf-8';
        else if (ext === '.js') contentType = 'application/javascript; charset=utf-8';
        else if (ext === '.png') contentType = 'image/png';
        else if (ext === '.jpg' || ext === '.jpeg') contentType = 'image/jpeg';
        else if (ext === '.svg') contentType = 'image/svg+xml';
        
        const fileContent = fs.readFileSync(filePath);
        // Set Cache-Control for 1 year (immutable) to enable CDN static caching
        res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
        return res.status(200).setHeader('Content-Type', contentType).send(fileContent);
      } else {
        return res.status(404).send('Not Found');
      }
    } catch (err) {
      console.error('Error serving static file:', err);
      return res.status(500).send('Internal Server Error');
    }
  }

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

    const CLIENT_ID = body.client_id || '1088195961071-25r6rpvsfmoudokb75u0m2ugu8na0v0.apps.googleusercontent.com';
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

    const CLIENT_ID = body.client_id || '1088195961071-25r6rpvsfmoudokb75u0m2ugu8na0v0.apps.googleusercontent.com';
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

  // Endpoint upload image to Cloudflare R2
  if (pathname === '/api/upload-r2') {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method Not Allowed' });
    }

    let body = {};
    try {
      body = req.body;
      if (typeof body === 'string') body = JSON.parse(body);
    } catch (e) {}

    if (!body || !body.file) {
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

    const { file, filename, type } = body;
    if (!file || !filename) {
      return res.status(400).json({ error: 'Bad Request: Missing file or filename' });
    }

    const r2AccessKeyId = process.env.R2_ACCESS_KEY_ID;
    const r2SecretAccessKey = process.env.R2_SECRET_ACCESS_KEY;
    const r2BucketName = process.env.R2_BUCKET_NAME;
    const cloudflareAccountId = process.env.CLOUDFLARE_ACCOUNT_ID;
    const r2PublicUrl = process.env.R2_PUBLIC_URL || 'https://pub-e92603c36c8d4789917d05d1eba12a7e.r2.dev';

    if (!r2AccessKeyId || !r2SecretAccessKey || !r2BucketName || !cloudflareAccountId) {
      return res.status(500).json({ error: 'Internal Server Error: Missing R2 environment variables on Vercel' });
    }

    try {
      const buffer = Buffer.from(file, 'base64');
      const contentType = filename.endsWith('.png') ? 'image/png' : 'image/jpeg';
      
      const reqInfo = signR2Request(buffer, filename, contentType, r2AccessKeyId, r2SecretAccessKey, r2BucketName, cloudflareAccountId);
      
      const response = await fetch(reqInfo.url, {
        method: 'PUT',
        headers: reqInfo.headers,
        body: buffer
      });

      if (!response.ok) {
        const errText = await response.text();
        console.error('R2 upload response error:', response.status, errText);
        return res.status(502).json({ error: 'Bad Gateway: Cloudflare R2 upload failed', details: errText });
      }

      const publicUrl = `${r2PublicUrl}/BDS-KhangNgo/${filename}`;
      return res.status(200).json({ status: 'success', url: publicUrl });
    } catch (err) {
      console.error('Error in R2 upload endpoint:', err);
      return res.status(500).json({ error: 'Internal Server Error', message: err.message });
    }
  }

  // 3. Endpoint sinh tiêu đề, mô tả và phường cũ bằng AI
  if (pathname === '/api/ai/generate') {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method Not Allowed' });
    }

    let body = {};
    try {
      body = req.body;
      if (typeof body === 'string') body = JSON.parse(body);
    } catch (e) {}

    if (!body || Object.keys(body).length === 0) {
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

    const cfg = loadConfig();
    const apiKey = (process.env.OPENAI_API_KEY || cfg.openai_api_key || '').trim();
    if (!apiKey) {
      return res.status(400).json({
        status: 'error',
        message: 'Chưa cấu hình OpenAI API Key. Vui lòng thiết lập trong file config hoặc biến môi trường.'
      });
    }

    // Tải prompt động từ Google Doc
    const docId = cfg.prompt_google_doc_id || '';
    let systemPrompt = '';
    if (docId) {
      try {
        let googleToken = null;
        const creds = getCredentials();
        if (creds) {
          googleToken = await getGoogleAccessToken(creds);
        }

        if (googleToken) {
          const docPrompt = await fetchGoogleDocContent(docId, googleToken);
          if (docPrompt) {
            systemPrompt = docPrompt;
          }
        }
      } catch (err) {
        console.error('Error fetching dynamic prompt, fallback to default:', err);
      }
    }

    if (!systemPrompt) {
      systemPrompt = cfg.openai_system_prompt || DEFAULT_SYSTEM_PROMPT;
    }

    // Nối chỉ thị JSON để đảm bảo AI trả về cấu trúc chính xác
    const jsonSuffix =
      "\n\n🚨 BẮT BUỘC ĐỊNH DẠNG ĐẦU RA (OUTPUT FORMAT):\n" +
      "Bạn PHẢI trả về kết quả dưới dạng JSON object duy nhất có cấu trúc chính xác sau, không chứa ký tự markdown (như ```json) hay văn bản nào bên ngoài:\n" +
      "{\n" +
      "  \"tieuDeChinh\": \"Tiêu đề public chính (viết theo hướng dẫn của Mục 1 thuộc Bước 3)\",\n" +
      "  \"tieuDePhu\": \"Tiêu đề phụ public (bắt buộc viết hoa toàn bộ, bắt đầu bằng biểu tượng 🏩, viết theo hướng dẫn của Mục 2 thuộc Bước 3)\",\n" +
      "  \"moTaChiTiet\": \"Mô tả chi tiết (bắt đầu bằng chữ 'Mô tả:', tiếp nối ngay bên dưới là các dòng con bắt đầu bằng dấu gạch bạt dài '–' theo hướng dẫn của Mục 3 thuộc Bước 3)\",\n" +
      "  \"gocNhinDauTu\": \"Góc nhìn đầu tư (bắt đầu bằng dòng tiêu đề viết hoa toàn bộ 'GÓC NHÌN ĐẦU TƯ...' sau đó là các dòng con bắt đầu bằng dấu chấm tròn nhỏ '•' theo hướng dẫn của Mục 4 thuộc Bước 3. Để trống nếu không thỏa mãn bộ lọc điều kiện)\",\n" +
      "  \"phuongCu\": \"Tên phường cũ (nếu có sáp nhập phường, hoặc để trống)\"\n" +
      "}";
      
    if (!systemPrompt.includes('tieuDeChinh') && 
        !systemPrompt.includes('tieu_de_chinh') && 
        !systemPrompt.includes('tieuDe') && 
        !systemPrompt.includes('tieu_de')) {
      systemPrompt += jsonSuffix;
    }

    // 1. Tính toán Tiền tố địa chỉ (Mặt tiền / HXH)
    const soNha = String(body.soNha || '').trim();
    const duongTruocNha = String(body.duongTruocNha || '').trim();
    const phanLoaiHem = String(body.phanLoaiHem || '').toLowerCase();

    let isMatTien = false;
    if (soNha) {
      if (!soNha.includes('.')) {
        isMatTien = true;
      }
    } else if (phanLoaiHem.includes('mặt tiền') || phanLoaiHem.includes('mặt phố')) {
      isMatTien = true;
    }

    let widthVal = parseFloat(duongTruocNha);
    if (isNaN(widthVal)) widthVal = 0.0;

    let tienTo = "";
    if (isMatTien) {
      tienTo = "Mặt tiền ";
    } else if (widthVal >= 4.0) {
      tienTo = "HXH ";
    }

    // 2. Xử lý định dạng Giá (tương thích Thiên Khôi)
    const giaChao = body.giaChao || '';
    let giaFormat = giaChao;
    const giaTy = parseFloat(giaChao);
    if (!isNaN(giaTy)) {
      let finalGiaTy = giaTy;
      if (finalGiaTy > 100) {
        finalGiaTy = finalGiaTy / 1000;
      }
      giaFormat = finalGiaTy > 0 ? `${finalGiaTy} tỷ` : '';
    }

    // 3. Tạo User Prompt
    const soNhaBiMat = String(body.soNha || '').trim();
    let securityWarning = "";
    if (soNhaBiMat) {
      securityWarning = `🚨 QUY TẮC BẢO MẬT ĐỊA CHỈ: Tuyệt đối KHÔNG được đưa số nhà cụ thể "${soNhaBiMat}" (hoặc bất kỳ số nhà/số hẻm cụ thể nào khác xuất hiện trong Tin gốc) vào Tiêu đề chính, Tiêu đề phụ, hay Mô tả. Phải loại bỏ hoàn toàn số nhà này khỏi bài viết để bảo mật nguồn hàng. Ví dụ: thay vì viết "${soNhaBiMat} ${body.duong || ''}" thì BẮT BUỘC chỉ được viết là "${body.duong || ''}" (hoặc "Đường ${body.duong || ''}").\n`;
    } else {
      securityWarning = `🚨 QUY TẮC BẢO MẬT ĐỊA CHỈ: Tuyệt đối KHÔNG được đưa bất kỳ số nhà cụ thể hoặc số hẻm cụ thể nào xuất hiện trong tin gốc vào Tiêu đề chính, Tiêu đề phụ, hay Mô tả. Chỉ dùng tên đường để bảo mật nguồn hàng.\n`;
    }

    const userPrompt =
      "THÔNG TIN CĂN NHÀ:\n" +
      `- Địa chỉ: ${body.soNha || ''} ${body.duong || ''}, Phường ${body.phuong || ''}, Quận ${body.quan || ''}\n` +
      `- Nội dung chính gốc (chứa kích thước ở đầu): ${body.noiDungChinh || ''}\n` +
      `- DT Thực tế: ${body.dtThucTe || ''}m2 | DT Trên sổ: ${body.dtTrenSo || ''}m2\n` +
      `- Chiều ngang (mặt tiền): ${body.matTien || ''}m\n` +
      `- Hướng: ${body.huong || ''}\n` +
      `- Kết cấu: ${body.soTang || ''} tầng, ${body.soPhongNgu || ''} PN, ${body.soToilet || ''} WC\n` +
      `- Hẻm: ${body.phanLoaiHem || ''} (Rộng: ${body.duongTruocNha || ''}m)\n` +
      `- Giá: ${giaFormat}\n` +
      `- Phân loại / Tag USP: ${body.phanLoai || ''}\n` +
      `- Điểm nổi bật của căn nhà (nguồn USP chính): ${body.moTaChiTiet || ''}\n\n` +
      securityWarning +
      "LƯU Ý QUAN TRỌNG: Đọc kỹ 'Nội dung chính gốc', 'Phân loại / Tag USP' và 'Điểm nổi bật' — bắt buộc phản ánh các thông số kỹ thuật và ưu điểm vào Tiêu đề và Mô tả. BẮT BUỘC bắt đầu phần tiêu đề trực tiếp bằng tiền tố '" + tienTo + "' kết hợp liền mạch với Tên đường (TUYỆT ĐỐI không chèn thêm bất kỳ dấu gạch ngang, dấu chấm hay ký tự đặc biệt nào giữa tiền tố này và tên đường, Ví dụ: " + (tienTo ? `'${tienTo}Trần Quang Diệu - ...'` : "'Trần Quang Diệu - ...'") + ").\n" +
      "🚨 YÊU CẦU ĐỊNH DẠNG: Bắt buộc phải trả về kết quả dưới định dạng JSON sạch (respond in json format) theo đúng cấu trúc yêu cầu trong System Prompt.";

    const openaiApiBase = (cfg.openai_api_base || 'https://api.openai.com/v1').replace(/\/$/, '');
    
    try {
      const openAiResponse = await fetch(`${openaiApiBase}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'gpt-4o-mini',
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
          ],
          temperature: 0.3,
          response_format: { type: 'json_object' }
        })
      });

      const resJson = await openAiResponse.json();
      if (!openAiResponse.ok) {
        const errMsg = resJson.error?.message || 'Lỗi không xác định từ OpenAI.';
        return res.status(openAiResponse.status).json({ status: 'error', message: `OpenAI API Error: ${errMsg}` });
      }

      const aiMessage = resJson.choices[0].message.content;
      console.log(`[🤖 AI] Nhận kết quả từ OpenAI: ${aiMessage}`);
      
      const aiData = JSON.parse(aiMessage);

      // Trích xuất các trường linh hoạt chống lỗi OpenAI tự đổi tên hoặc định dạng key
      let tieuDeChinh = '';
      for (const k of ['tieuDeChinh', 'tieu_de_chinh', 'tieuDe', 'tieu_de', 'tieuDePublic', 'tieu_de_public', 'tieu de', 'Tiêu đề', 'tiêu đề']) {
        if (aiData[k] !== undefined && aiData[k] !== null) {
          tieuDeChinh = String(aiData[k]);
          break;
        }
      }
      if (!tieuDeChinh) {
        const key = Object.keys(aiData).find(k => k.toLowerCase().includes('tieu') && !k.toLowerCase().includes('phu'));
        if (key) tieuDeChinh = String(aiData[key]);
      }

      let tieuDePhu = '';
      for (const k of ['tieuDePhu', 'tieu_de_phu', 'tieuPhu', 'tieu_phu']) {
        if (aiData[k] !== undefined && aiData[k] !== null) {
          tieuDePhu = String(aiData[k]);
          break;
        }
      }
      if (!tieuDePhu) {
        const key = Object.keys(aiData).find(k => k.toLowerCase().includes('tieu') && k.toLowerCase().includes('phu'));
        if (key) tieuDePhu = String(aiData[key]);
      }

      let moTaChiTiet = '';
      for (const k of ['moTaChiTiet', 'mo_ta_chi_tiet', 'moTa', 'mo_ta', 'moTaPublic', 'mo_ta_public', 'mo ta', 'Mô tả', 'mô tả']) {
        if (aiData[k] !== undefined && aiData[k] !== null) {
          moTaChiTiet = String(aiData[k]);
          break;
        }
      }
      if (!moTaChiTiet) {
        const key = Object.keys(aiData).find(k => k.toLowerCase().includes('mo') && !k.toLowerCase().includes('phuong') && !k.toLowerCase().includes('phu'));
        if (key) moTaChiTiet = String(aiData[key]);
      }

      let gocNhinDauTu = '';
      for (const k of ['gocNhinDauTu', 'goc_nhin_dau_tu', 'gocNhin', 'goc_nhin']) {
        if (aiData[k] !== undefined && aiData[k] !== null) {
          gocNhinDauTu = String(aiData[k]);
          break;
        }
      }
      if (!gocNhinDauTu) {
        const key = Object.keys(aiData).find(k => k.toLowerCase().includes('goc') || k.toLowerCase().includes('dau_tu'));
        if (key) gocNhinDauTu = String(aiData[key]);
      }

      let phuongCuRaw = '';
      for (const k of ['phuongCu', 'phuong_cu', 'phuong cu', 'Phường cũ', 'phường cũ']) {
        if (aiData[k] !== undefined && aiData[k] !== null) {
          phuongCuRaw = String(aiData[k]);
          break;
        }
      }
      if (!phuongCuRaw) {
        const key = Object.keys(aiData).find(k => k.toLowerCase().includes('phuong') || k.toLowerCase().includes('old'));
        if (key) phuongCuRaw = String(aiData[key]);
      }

      const trimTieuDeBds = (title) => {
        if (!title) return '';
        let t = String(title).trim();
        t = t.replace(/^["'\s]+|["'\s]+$/g, '');
        t = t.replace(/\s+/g, ' ');
        if (t.length > 85) {
          t = t.substring(0, 85).trim();
        }
        return t;
      };

      const tieuDeClean = trimTieuDeBds(tieuDeChinh).replace(/\*\*/g, '');
      const tieuDePhuClean = tieuDePhu ? String(tieuDePhu).replace(/\*\*/g, '') : '';
      const moTaChiTietClean = moTaChiTiet ? String(moTaChiTiet).replace(/\*\*/g, '') : '';
      const gocNhinDauTuClean = gocNhinDauTu ? String(gocNhinDauTu).replace(/\*\*/g, '') : '';

      // Ghép tiêu đề phụ, mô tả chi tiết và góc nhìn đầu tư lại thành mô tả public
      let moTaRaw = '';
      if (tieuDePhuClean) {
        moTaRaw += tieuDePhuClean.trim() + '\n';
      }
      if (moTaChiTietClean) {
        moTaRaw += moTaChiTietClean.trim();
      }
      if (gocNhinDauTuClean && gocNhinDauTuClean.trim()) {
        let gnd = gocNhinDauTuClean.trim();
        if (!gnd.startsWith('---')) {
          moTaRaw += '\n---\n';
        } else {
          moTaRaw += '\n';
        }
        moTaRaw += gnd;
      }

      const moTaClean = moTaRaw ? String(moTaRaw).replace(/\*\*/g, '') : '';

      return res.status(200).json({
        status: 'success',
        tieu_de_public: tieuDeClean,
        mo_ta_public: moTaClean,
        phuong_cu: phuongCuRaw
      });
    } catch (err) {
      console.error('Error calling OpenAI API in Node.js:', err);
      return res.status(500).json({ status: 'error', message: `Lỗi gọi OpenAI API: ${err.message}` });
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
  const htmlPaths = [
    path.join(__dirname, '..', 'index.html'),
    path.join(process.cwd(), 'index.html'),
    path.join(__dirname, 'index.html')
  ];
  let lastErr = null;
  for (const p of htmlPaths) {
    try {
      if (fs.existsSync(p)) {
        html = fs.readFileSync(p, 'utf8');
        break;
      }
    } catch (err) {
      lastErr = err;
    }
  }

  if (!html) {
    console.error('Error reading index.html, last error:', lastErr);
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
