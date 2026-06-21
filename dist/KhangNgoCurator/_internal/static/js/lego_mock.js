/**
 * Lego Frontend - Mock API & Interceptor Module (lego_mock.js)
 * Intercepts Google Sheets APIs and Google OAuth token exchanges for local/offline testing.
 */
(function() {
  const urlParams = new URLSearchParams(window.location.search);
  const mockParam = urlParams.get('mock');
  if (mockParam === 'true') {
    localStorage.setItem('isMockMode', 'true');
    localStorage.setItem('isAdminSession', 'true');
  } else if (mockParam === 'false') {
    localStorage.removeItem('isMockMode');
    localStorage.removeItem('isAdminSession');
  }

  if (localStorage.getItem('isMockMode') === 'true') {
    console.log("⚡ [Mock Mode] Active: Intercepting Google Sheets APIs.");
    window.isMockMode = true;
    
    // Ensure mock credentials exist so login is bypassed
    if (!localStorage.getItem('g_access_token')) {
      localStorage.setItem('g_access_token', 'mock_google_oauth_token');
      localStorage.setItem('g_token_expiry', (Date.now() + 3600 * 1000).toString());
    }
    
    const originalFetch = window.fetch;
    window.fetch = async function(url, options = {}) {
      const urlStr = String(url);
      if (urlStr.includes('sheets.googleapis.com')) {
        const method = (options.method || 'GET').toUpperCase();
        console.log(`[Mock Sheets API] Intercepted ${method} ${urlStr}`);
        
        if (method === 'GET') {
          if (urlStr.includes('Source')) {
            const mockSourceValues = [
              ["Hàng", "Cú pháp", "ID", "SystemID", "Tiêu đề", "Diện tích", "Số tầng", "Mặt tiền", "Giá", "Quận", "Phường", "Loại hình", "Hướng", "Đường trước nhà", "Rộng hẻm", "Tình trạng", "Đánh giá", "Ngủ tầng trệt", "CHDV", "Mô tả", "Ảnh 1", "Ảnh 2", "Ảnh 3", "Ảnh 4", "Ảnh 5", "Ảnh 6", "Ảnh 7", "Ảnh 8", "Ảnh 9", "Ảnh 10", "Ảnh 11", "Ảnh 12", "Ảnh 13", "Ảnh 14", "Ảnh 15", "Ảnh 16", "Ảnh 17", "SystemID_Col", "Mặt tiền Col"],
              ["1", "CP", "2001", "SYS-1001", "Căn Cách Mạng Tháng Tám Quận 3 VIP", "100", "4", "5", "8.5", "Q3", "Phường 11", "Mặt tiền", "Đông Nam", "15", "0", "Bình thường", "Hàng Ngon", "Không", "Không", "Mô tả chi tiết căn CMT8 Quận 3 siêu đẹp...", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "SYS-1001", "SYS-1001", "https://res.cloudinary.com/demo/image/upload/sample.jpg"],
              ["2", "CP", "2002", "SYS-1002", "Căn Ba Tháng Hai Quận 10 Thơm", "80", "3", "4", "12.0", "Q10", "Phường 12", "Hẻm xe hơi", "Tây Nam", "6", "6", "Bình thường", "Hàng Ngon", "Không", "Không", "Nhà đẹp hẻm nhựa 6m Ba Tháng Hai Q10...", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "SYS-1002", "SYS-1002", "https://res.cloudinary.com/demo/image/upload/sample.jpg"]
            ];
            return new Response(JSON.stringify({ values: mockSourceValues }), {
              status: 200,
              headers: { 'Content-Type': 'application/json' }
            });
          } else if (urlStr.includes('Pool')) {
            const mockPoolValues = [
              ["NoName", "", "", "", "", "Cách Mạng Tháng Tám", "123", "", "", "Nội dung chính Cách Mạng Tháng Tám", "Mô tả chi tiết CMT8 Q3 VIP", "6.5", "", "100", "", "", "", "", "", "", "", "", "", "", "", "", "", "https://res.cloudinary.com/demo/image/upload/sodo1_123.jpg", "https://res.cloudinary.com/demo/image/upload/sodo2_123.jpg", "https://res.cloudinary.com/demo/image/upload/mat_tien_123.jpg", "", "", "", "", "", "", "", "", "", "https://res.cloudinary.com/demo/image/upload/interior_1.jpg", "", "", "", "", "", "", "2001", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "SYS-1001"],
              ["NoName", "", "", "", "", "Ba Tháng Hai", "456", "", "", "Nội dung chính Ba Tháng Hai", "Mô tả chi tiết Ba Tháng Hai", "11.5", "", "80", "", "", "", "", "", "", "", "", "", "", "", "", "", "https://res.cloudinary.com/demo/image/upload/sodo1_456.jpg", "https://res.cloudinary.com/demo/image/upload/sodo2_456.jpg", "https://res.cloudinary.com/demo/image/upload/mat_tien_456.jpg", "", "", "", "", "", "", "", "", "", "https://res.cloudinary.com/demo/image/upload/interior_2.jpg", "", "", "", "", "", "", "2002", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "SYS-1002"]
            ];
            return new Response(JSON.stringify({ values: mockPoolValues }), {
              status: 200,
              headers: { 'Content-Type': 'application/json' }
            });
          }
        } else if (method === 'PUT' || method === 'POST') {
          console.log("[Mock Sheets API] Simulated successfully writing to Google Sheets!");
          if (typeof window.showToast === 'function') {
            window.showToast("Mock Save: Đã mô phỏng lưu thành công vào Sheets!", "success");
          }
          return new Response(JSON.stringify({ spreadsheetId: "mock-sheet", updatedCells: 1 }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
          });
        }
      }
      if (urlStr.includes('/api/auth/')) {
        console.log(`[Mock Sheets API] Mocking Auth endpoint: ${urlStr}`);
        return new Response(JSON.stringify({
          access_token: 'mock_google_oauth_token',
          expires_in: 3600,
          refresh_token: 'mock_refresh_token'
        }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        });
      }
      return originalFetch.apply(this, arguments);
    };
  }
})();
