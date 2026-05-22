---
id: US-022
status: ready
date: 2026-05-22
size: S
---

# US-022: Khang Ngô AI Apps Script (Lưu trữ và tài liệu hóa Custom Script trên sheet Source)

## User story
**As an** *Admin / PO*  
**I want** *lưu trữ và tài liệu hóa đoạn mã Apps Script custom mang tên "Khang Ngô AI" chạy trực tiếp trên Google Sheet Source*  
**So that** *tôi có thể dễ dàng quản lý mã nguồn, khôi phục khi cần thiết, và tích hợp các công cụ AI hỗ trợ viết tin đăng, giải mã địa chỉ và chuẩn hóa tên đường một cách tập trung*  

## Acceptance
- [x] Tạo file User Story `US-022_khangngo_ai_custom_script.md` riêng biệt trong thư mục `docs/stories/_inbox/`.
- [x] Thay thế khóa API OpenAI bằng placeholder `sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` để vượt qua cơ chế GitHub Push Protection mà vẫn giữ cấu trúc mã nguồn nguyên vẹn.
- [x] Tài liệu hóa đầy đủ hướng dẫn cài đặt và các tính năng có trong custom script:
  - **Tự động viết tin đăng (vào cột bên phải)**: Đọc thông tin thô, giải mã địa chỉ/diện tích và gọi GPT-4o-mini sinh tin đăng chuyên nghiệp dưới 88 ký tự tiêu đề kèm mô tả thoáng.
  - **Gộp địa chỉ & tên đường**: Giải mã mã số nhà từ ID và ghép với tên đường từ cột tieu_de để tạo địa chỉ đầy đủ.
  - **Xuất tên đường ra 1 cột**: Trích xuất tên đường sạch từ cột tieu_de.

## Solution

Dưới đây là toàn bộ mã nguồn Apps Script custom `"🤖 KHANG NGÔ AI"` chạy trên Google Sheet `Source` (BDS_KhangNgo_Source):

```javascript
/**
 * ==========================================
 * HƯỚNG DẪN CÀI ĐẶT
 * ==========================================
 * 1. Trên Google Sheet, chọn Tiện ích mở rộng (Extensions) -> Apps Script.
 * 2. Xóa hết code cũ, dán toàn bộ đoạn code này vào.
 * 3. Bấm Lưu (biểu tượng đĩa mềm). Tắt tab Apps Script.
 * 4. Tải lại (F5) trang Google Sheet.
 * 5. Lúc này trên thanh Menu của Google Sheet sẽ xuất hiện menu "🤖 KHANG NGÔ AI".
 * 6. Bôi đen (chọn) các ô chứa thông tin thô, bấm menu "🤖 KHANG NGÔ AI" -> "Tự động viết tin đăng".
 * 7. AI sẽ xử lý và điền kết quả vào cột NGAY BÊN PHẢI của cột bạn vừa chọn.
 */

const OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"; // Điền OpenAI API Key của bạn vào đây

/**
 * Hàm tạo Menu khi mở Sheet
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 KHANG NGÔ AI')
    .addItem('Tự động viết tin đăng (vào cột bên phải)', 'processSelectedCells')

    .addSeparator() // Mới ver2: Tạo dấu gạch ngang phân cách
    .addItem('Gộp địa chỉ & tên đường', 'processAddressAndStreet') // Mới ver2: Lệnh gọi hàm gộp
    .addItem('Xuất tên đường ra 1 cột', 'processOnlyStreetName') // Mới: Lệnh xuất tên đường

    .addToUi();
}

/**
 * Hàm xử lý khi người dùng quét chọn nhiều ô và bấm nút
 */
function processSelectedCells() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  const numRows = range.getNumRows();
  const numCols = range.getNumColumns();
  
  if (numCols > 1) {
    SpreadsheetApp.getUi().alert("Vui lòng chỉ quét chọn 1 cột chứa nội dung thô!");
    return;
  }
  
  const values = range.getValues();
  const startRow = range.getRow();
  const col = range.getColumn();
  
  // Hiển thị thông báo đang chạy
  SpreadsheetApp.getActiveSpreadsheet().toast("Đang nhờ AI phân tích và viết tin...", "Vui lòng đợi", -1);
  
  let successCount = 0;

  for (let i = 0; i < numRows; i++) {
    const rawData = values[i][0];
    if (!rawData || String(rawData).trim() === "") continue;
    
    // Gọi AI sinh nội dung
    const aiResult = callOpenAI(String(rawData));
    
    // Viết kết quả vào ô ngay bên phải (Cột hiện tại + 1)
    sheet.getRange(startRow + i, col + 1).setValue(aiResult);
    successCount++;
  }
  
  SpreadsheetApp.getActiveSpreadsheet().toast(`Đã viết xong ${successCount} tin đăng!`, "Hoàn tất", 5);
}

/**
 * Hàm kết nối API của OpenAI
 */
function callOpenAI(rawData) {
  // 📝 HỆ THỐNG PROMPT (Đã tối ưu theo chuẩn Khang Ngô Nhà Phố)
  const systemPrompt = `Bạn là một chuyên gia môi giới bất động sản tại TP.HCM.
Nhiệm vụ của bạn là nhận thông tin thô của một căn nhà từ đầu chủ và viết lại thành 01 tin đăng chuyên nghiệp duy nhất.

🚨 CÁC QUY TẮC BẮT BUỘC (LUẬT THÉP):

NHIỆM VỤ 1: GIẢI MÃ CÚ PHÁP DỮ LIỆU THÔ
- Địa chỉ: Chuỗi số đứng trước tên đường là địa chỉ nhà (Dấu "." tương ứng dấu "/"). Ví dụ: "306.33.8 Nguyễn Thị Minh Khai" -> "306/33/8 Nguyễn Thị Minh Khai".
- Diện tích (Quy tắc số lớn): Nếu có dạng "Số nhỏ/Số lớn" (ví dụ 33/39), luôn lấy số lớn là Diện tích sử dụng để đăng tin.
- Kích thước (Quy tắc số lớn): Nếu ngang/dài có 2 thông số (ví dụ ngang 3.6/3.8), luôn lấy số lớn (3.8m).
- Thứ tự suy luận dữ liệu nếu không có nhãn: [Địa chỉ] - [Tên đường] - [Diện tích] - [Số tầng] - [Ngang] - [Dài] - [Giá].
- Ký hiệu kết cấu cần hiểu: BTCT (Bê tông cốt thép), ST (Sân thượng), CHDV (Căn hộ dịch vụ), HXH (Hẻm xe hơi).

NHIỆM VỤ 2: TRA CỨU TIỆN ÍCH & ĐỊA GIỚI
- Nếu thông tin thô có Phường mới, bắt buộc dùng Phường mới. Nếu không, hãy TỰ ĐỘNG CẬP NHẬT Phường theo quy định sáp nhập địa giới hành chính mới nhất tại TP.HCM.
- Dựa vào tên đường và quận, TỰ ĐỘNG liệt kê các tiện ích có thật trong bán kính 1km (Nêu tên riêng cụ thể của: Tòa nhà văn phòng, Ngân hàng, Bệnh viện, Trường học, Công viên... quanh đó).

NHIỆM VỤ 3: CẤU TRÚC TIN ĐĂNG (BẮT BUỘC THEO ĐÚNG FORMAT SAU)
1. Tiêu đề (Dưới 88 ký tự):
- Bắt đầu bằng: "🚘 HXH" (nếu có yếu tố hẻm xe hơi).
- Cấu trúc: [Tên đường - Quận - Diện tích - Ưu điểm nổi bật - giá].
- Ưu điểm nhấn mạnh: Kết cấu nhiều tầng (>=4 tầng), Nội thất mới, Số phòng ngủ (ghi tắt là PN).
- Kết thúc bằng dấu gạch ngang và giá (Ví dụ: - 9.9 tỷ).

2. Nội dung mô tả (Sử dụng dòng trống chứa ký tự tàng hình "ㅤㅤㅤ" giữa các phần để tạo độ thoáng):
- Vị trí: Quận, Phường (mới). Mô tả hẻm (Ví dụ: "Hẻm Xe Hơi 5m", "Hẻm rộng thoáng") kèm cụm từ "gần mặt tiền".
ㅤㅤㅤ
- Kết cấu: Diện tích (ví dụ 32M²), (axb)m (chỉ ghi nếu ngang >= 3.5m, với a là ngang, b là dài, lấy số tròn hoặc phẩy 1 số). Luôn ghi "Kết cấu x tầng BTCT", chi tiết các tầng/phòng.
ㅤㅤㅤ
- Kết nối & Tiện ích: Các trục đường huyết mạch cắt ngang, tên riêng các tiện ích xung quanh đã tra cứu. Tập trung khách mua ở hoặc vừa ở vừa cho thuê nếu có CHDV.
ㅤㅤㅤ
- Pháp lý: Sổ hồng riêng, hoàn công đầy đủ.

⚠️ LƯU Ý QUAN TRỌNG:
- Trả về NỘI DUNG TIN ĐĂNG trực tiếp, không chào hỏi, không giải thích, không thừa thãi.
- Dùng dấu gạch ngang (-) để liệt kê ý.
- Văn phong ngắn gọn, súc tích, cực kỳ chuyên nghiệp.`;

  const payload = {
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "system",
        "content": systemPrompt
      },
      {
        "role": "user",
        "content": rawData
      }
    ],
    "temperature": 0.3
  };

  const options = {
    "method": "post",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + OPENAI_API_KEY
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  try {
    const response = UrlFetchApp.fetch("https://api.openai.com/v1/chat/completions", options);
    const json = JSON.parse(response.getContentText());
    
    if (json.choices && json.choices.length > 0) {
      return json.choices[0].message.content.trim();
    } else {
      return "Lỗi AI: " + (json.error ? json.error.message : "Không nhận được phản hồi");
    }
  } catch (e) {
    return "Lỗi kết nối API: " + e.message;
  }
}

// --- BẮT ĐẦU PHẦN CHÈN MỚI bổ sung (Ver2) ---

function processAddressAndStreet() {
  var ui = SpreadsheetApp.getUi();
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  // 1. Hỏi người dùng cột mục tiêu
  var response = ui.prompt('Nhập tên cột để chèn dữ liệu (Ví dụ: AJ):');
  if (response.getSelectedButton() != ui.Button.OK) return;
  var targetColumnLetter = response.getResponseText().toUpperCase();
  
  if (!targetColumnLetter.match(/^[A-Z]+$/)) {
    ui.alert('Tên cột không hợp lệ!');
    return;
  }

  var data = sheet.getDataRange().getValues();
  var headers = data[1];
  
  // 2. Tìm vị trí cột "id" và "tieu_de"
  var idIdx = headers.indexOf('id');
  var tieuDeIdx = headers.indexOf('tieu_de');
  
  if (idIdx === -1 || tieuDeIdx === -1) {
    ui.alert('Không tìm thấy cột "id" hoặc "tieu_de". Hãy đảm bảo tiêu đề nằm ở HÀNG 2 và viết đúng chữ thường.');
    return;
  }

  var results = [];
  // CHỈNH SỬA TẠI ĐÂY: Vòng lặp bắt đầu từ hàng 3 (index là 2) để bỏ qua hàng tiêu đề
  for (var i = 2; i < data.length; i++) {
    var rawId = data[i][idIdx].toString();
    var rawTieuDe = data[i][tieuDeIdx].toString();
    
    if (!rawId) {
      results.push([""]);
      continue;
    }

    // Logic giải mã ID
    var cleanId = rawId.replace(/[WU]/gi, ''); // Xóa W và U tàng hình
    var lastI = cleanId.lastIndexOf('I');
    var houseNumberPart = "";
    
    if (lastI !== -1) {
      var numbersOnly = cleanId.substring(0, lastI);
      houseNumberPart = decodeNumbers(numbersOnly);
    }

    // Lấy tên đường từ tieu_de
    var streetName = extractStreetName(rawTieuDe);
    
    // Gộp kết quả
    var finalAddress = (houseNumberPart + " " + streetName).trim();
    results.push([finalAddress]);
  }

  // 3. Ghi dữ liệu vào cột chỉ định: Bắt đầu ghi từ hàng 3 (Range hàng 3, cột đích)
  var targetColIndex = columnLetterToIndex(targetColumnLetter);
  sheet.getRange(3, targetColIndex, results.length, 1).setValues(results);
  
  ui.alert('Đã hoàn thành gộp dữ liệu vào cột ' + targetColumnLetter);
}

// Hàm phụ 1: Chuyển ký tự ID sang số nhà (Giữ nguyên chữ thường, S=6, I=.)
function decodeNumbers(str) {
  var map = {
    'M': '1', 'H': '2', 'B': '3', 'A': '4', 'N': '5',
    'S': '6', 'Z': '7', 'T': '8', 'C': '9', 'O': '0', '0': '0', 'I': '.'
  };
  
  return str.split('').map(function(char) {
    // Nếu là chữ viết thường (từ a đến z), giữ nguyên không thay đổi
    if (char >= 'a' && char <= 'z') {
      return char;
    }
    // Ngược lại nếu là chữ hoa hoặc số, tra bảng mã
    return map[char.toUpperCase()] || char;
  }).join('');
}

// Hàm phụ 2: Tách tên đường từ tieu_de và làm sạch các từ khóa thừa
function extractStreetName(tieuDe) {
  // 1. Danh sách các từ cần loại bỏ (không phân biệt hoa thường)
  var filterWords = [
    "Bán nhà", "HXH", "CHDV", "Hot", "Hẻm ô tô", 
    "Hẻm xe hơi", "Mặt tiền", "Cần bán", "Gấp"
  ];
  
  // 2. Tách phần tên đường (trước con số diện tích)
  var streetPart = tieuDe;
  var match = tieuDe.match(/\s\d{2,}/);
  if (match) {
    streetPart = tieuDe.substring(0, match.index).trim();
  }

  // 3. Loại bỏ các từ khóa thừa ở đầu chuỗi
  // Tạo Regex để tìm và thay thế các từ trong danh sách ở đầu câu
  var pattern = new RegExp("^(" + filterWords.join("|") + ")\\s*", "gi");
  
  // Chạy vòng lặp để xóa sạch nếu người dùng ghi nhiều từ khóa (vd: "Bán nhà HXH...")
  var cleanedStreet = streetPart;
  while (pattern.test(cleanedStreet)) {
    cleanedStreet = cleanedStreet.replace(pattern, "").trim();
  }

  return cleanedStreet;
}

// Hàm phụ 3: Chuyển chữ cái cột (A, B, AJ...) thành số thứ tự
function columnLetterToIndex(letter) {
  var column = 0;
  for (var i = 0; i < letter.length; i++) {
    column += (letter.charCodeAt(i) - 64) * Math.pow(26, letter.length - i - 1);
  }
  return column;
}

// Hàm mới: Chỉ trích xuất tên đường và ghi vào cột được chọn
function processOnlyStreetName() {
  var ui = SpreadsheetApp.getUi();
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  var response = ui.prompt('Nhập tên cột để xuất TÊN ĐƯỜNG (Ví dụ: AK):');
  if (response.getSelectedButton() != ui.Button.OK) return;
  var targetColumnLetter = response.getResponseText().toUpperCase();
  
  if (!targetColumnLetter.match(/^[A-Z]+$/)) {
    ui.alert('Tên cột không hợp lệ!');
    return;
  }

  var data = sheet.getDataRange().getValues();
  var headers = data[1]; // Vẫn lấy tiêu đề ở hàng 2
  var tieuDeIdx = headers.indexOf('tieu_de');
  
  if (tieuDeIdx === -1) {
    ui.alert('Không tìm thấy cột "tieu_de" ở hàng 2.');
    return;
  }

  var results = [];
  // Chạy từ hàng 3 (index 2)
  for (var i = 2; i < data.length; i++) {
    var rawTieuDe = data[i][tieuDeIdx] ? data[i][tieuDeIdx].toString() : "";
    
    // Sử dụng lại hàm extractStreetName đã có để lấy tên đường sạch
    var streetName = extractStreetName(rawTieuDe);
    results.push([streetName]);
  }

  var targetColIndex = columnLetterToIndex(targetColumnLetter);
  sheet.getRange(3, targetColIndex, results.length, 1).setValues(results);
  
  ui.alert('Đã xuất xong TÊN ĐƯỜNG vào cột ' + targetColumnLetter);
}
// --- KẾT THÚC PHẦN CHÈN BỔ SUNG VER2 MỚI ---
```
