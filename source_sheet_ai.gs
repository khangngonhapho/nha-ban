// ==========================================
// UNIFIED KHANG NGÔ AI - SOURCE SHEET CUSTOM SCRIPT
// Tích hợp đầy đủ tính năng cũ và mới hỗ trợ tối ưu SEO và tiện ích dữ liệu
// ==========================================

// 0. CẤU HÌNH API KEY (Thay thế bằng OpenAI API Key thực tế của bạn)
var OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"; // Điền OpenAI API Key của bạn vào đây

// Tự động tối ưu bảo mật: Ưu tiên lấy API Key từ Script Properties (Cài đặt -> Thuộc tính dự án) để tránh lộ key trên Git
if (typeof PropertiesService !== 'undefined') {
  var savedKey = PropertiesService.getScriptProperties().getProperty('OPENAI_API_KEY');
  if (savedKey && savedKey.trim().indexOf('sk-') === 0) {
    OPENAI_API_KEY = savedKey.trim();
  }
}

/**
 * Hàm tạo Menu khi mở Sheet Source
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 KHANG NGÔ AI')
    .addItem('Tự động viết tin đăng (vào cột bên phải)', 'processSelectedCells')
    .addItem('Tự động viết Tiêu đề BDS (<85 ký tự)', 'batchGenerateTieuDeBdsAI')
    .addSeparator() // Phân cách nhóm tiện ích dữ liệu
    .addItem('Gộp địa chỉ & tên đường', 'processAddressAndStreet')
    .addItem('Xuất tên đường ra 1 cột', 'processOnlyStreetName')
    .addSeparator()
    .addItem('Di cư ảnh Cloudinary từ Pool (hàng loạt)', 'migrateSourceImages')
    .addToUi();
}

// ==========================================
// TÍNH NĂNG 1: TỰ ĐỘNG VIẾT TIN ĐĂNG (VÀO CỘT BÊN PHẢI)
// ==========================================

/**
 * Hàm xử lý khi người dùng quét chọn nhiều ô và bấm nút
 */
function processSelectedCells() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var range = sheet.getActiveRange();
  var numRows = range.getNumRows();
  var numCols = range.getNumColumns();
  
  if (numCols > 1) {
    SpreadsheetApp.getUi().alert("Vui lòng chỉ quét chọn 1 cột chứa nội dung thô!");
    return;
  }
  
  var values = range.getValues();
  var startRow = range.getRow();
  var col = range.getColumn();
  
  // Hiển thị thông báo đang chạy
  SpreadsheetApp.getActiveSpreadsheet().toast("Đang nhờ AI phân tích và viết tin...", "Vui lòng đợi", -1);
  
  var successCount = 0;

  for (var i = 0; i < numRows; i++) {
    var rawData = values[i][0];
    if (!rawData || String(rawData).trim() === "") continue;
    
    // Gọi AI sinh nội dung
    var aiResult = callOpenAI(String(rawData));
    
    // Viết kết quả vào ô ngay bên phải (Cột hiện tại + 1)
    sheet.getRange(startRow + i, col + 1).setValue(aiResult);
    successCount++;
  }
  
  SpreadsheetApp.getActiveSpreadsheet().toast("Đã viết xong " + successCount + " tin đăng!", "Hoàn tất", 5);
}

/**
 * Hàm kết nối API của OpenAI phục vụ Viết tin đăng
 */
function callOpenAI(rawData) {
  var systemPrompt = "Bạn là một chuyên gia môi giới bất động sản tại TP.HCM.\n" +
                     "Nhiệm vụ của bạn là nhận thông tin thô của một căn nhà từ đầu chủ và viết lại thành 01 tin đăng chuyên nghiệp duy nhất.\n\n" +
                     "🚨 CÁC QUY TẮC BẮT BUỘC (LUẬT THÉP):\n\n" +
                     "NHIỆM VỤ 1: GIẢI MÃ CÚ PHÁP DỮ LIỆU THÔ\n" +
                     "- Địa chỉ: Chuỗi số đứng trước tên đường là địa chỉ nhà (Dấu \".\" tương ứng dấu \"/\"). Ví dụ: \"306.33.8 Nguyễn Thị Minh Khai\" -> \"306/33/8 Nguyễn Thị Minh Khai\".\n" +
                     "- Diện tích (Quy tắc số lớn): Nếu có dạng \"Số nhỏ/Số lớn\" (ví dụ 33/39), luôn lấy số lớn là Diện tích sử dụng để đăng tin.\n" +
                     "- Kích thước (Quy tắc số lớn): Nếu ngang/dài có 2 thông số (ví dụ ngang 3.6/3.8), luôn lấy số lớn (3.8m).\n" +
                     "- Thứ tự suy luận dữ liệu nếu không có nhãn: [Địa chỉ] - [Tên đường] - [Diện tích] - [Số tầng] - [Ngang] - [Dài] - [Giá].\n" +
                     "- Ký hiệu kết cấu cần hiểu: BTCT (Bê tông cốt thép), ST (Sân thượng), CHDV (Căn hộ dịch vụ), HXH (Hẻm xe hơi).\n\n" +
                     "NHIỆM VỤ 2: TRA CỨU TIỆN ÍCH & ĐỊA GIỚI\n" +
                     "- Nếu thông tin thô có Phường mới, bắt buộc dùng Phường mới. Nếu không, hãy TỰ ĐỘNG CẬP NHẬT Phường theo quy định sáp nhập địa giới hành chính mới nhất tại TP.HCM.\n" +
                     "- Dựa vào tên đường và quận, TỰ ĐỘNG liệt kê các tiện ích có thật trong bán kính 1km (Nêu tên riêng cụ thể của: Tòa nhà văn phòng, Ngân hàng, Bệnh viện, Trường học, Công viên... quanh đó).\n\n" +
                     "NHIỆM VỤ 3: CẤU TRÚC TIN ĐĂNG (BẮT BUỘC THEO ĐÚNG FORMAT SAU)\n" +
                     "1. Tiêu đề (Dưới 88 ký tự):\n" +
                     "- Bắt đầu bằng: \"🚘 HXH\" (nếu có yếu tố hẻm xe hơi).\n" +
                     "- Cấu trúc: [Tên đường - Quận - Diện tích - Ưu điểm nổi bật - giá].\n" +
                     "- Ưu điểm nhấn mạnh: Kết cấu nhiều tầng (>=4 tầng), Nội thất mới, Số phòng ngủ (ghi tắt là PN).\n" +
                     "- Kết thúc bằng dấu gạch ngang và giá (Ví dụ: - 9.9 tỷ).\n\n" +
                     "2. Nội dung mô tả (Sử dụng dòng trống chứa ký tự tàng hình \"ㅤㅤㅤ\" giữa các phần để tạo độ thoáng):\n" +
                     "- Vị trí: Quận, Phường (mới). Mô tả hẻm (Ví dụ: \"Hẻm Xe Hơi 5m\", \"Hẻm rộng thoáng\") kèm cụm từ \"gần mặt tiền\".\n" +
                     "ㅤㅤㅤ\n" +
                     "- Kết cấu: Diện tích (ví dụ 32M²), (axb)m (chỉ ghi nếu ngang >= 3.5m, với a là ngang, b là dài, lấy số tròn hoặc phẩy 1 số). Luôn ghi \"Kết cấu x tầng BTCT\", chi tiết các tầng/phòng.\n" +
                     "ㅤㅤㅤ\n" +
                     "- Kết nối & Tiện ích: Các trục đường huyết mạch cắt ngang, tên riêng các tiện ích xung quanh đã tra cứu. Tập trung khách mua ở hoặc vừa ở vừa cho thuê nếu có CHDV.\n" +
                     "ㅤㅤㅤ\n" +
                     "- Pháp lý: Sổ hồng riêng, hoàn công đầy đủ.\n\n" +
                     "⚠️ LƯU Ý QUAN TRỌNG:\n" +
                     "- Trả về NỘI DUNG TIN ĐĂNG trực tiếp, không chào hỏi, không giải thích, không thừa thãi.\n" +
                     "- Dùng dấu gạch ngang (-) để liệt kê ý.\n" +
                     "- Văn phong ngắn gọn, súc tích, cực kỳ chuyên nghiệp.";

  var payload = {
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "system", "content": systemPrompt},
      {"role": "user", "content": rawData}
    ],
    "temperature": 0.3
  };

  var options = {
    "method": "post",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + OPENAI_API_KEY
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  try {
    var response = UrlFetchApp.fetch("https://api.openai.com/v1/chat/completions", options);
    var json = JSON.parse(response.getContentText());
    
    if (json.choices && json.choices.length > 0) {
      return json.choices[0].message.content.trim();
    } else {
      return "Lỗi AI: " + (json.error ? json.error.message : "Không nhận được phản hồi");
    }
  } catch (e) {
    return "Lỗi kết nối API: " + e.message;
  }
}

// ==========================================
// TÍNH NĂNG 2: TỰ ĐỘNG VIẾT TIÊU ĐỀ BDS (<85 KÝ TỰ)
// ==========================================

/**
 * Xử lý hàng loạt các dòng đang được bôi đen (Active Range) trên sheet Source để viết tiêu đề dưới 85 ký tự
 */
function batchGenerateTieuDeBdsAI() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var range = sheet.getActiveRange();
  var startRow = range.getRow();
  var numRows = range.getNumRows();
  
  if (startRow <= 1) {
    SpreadsheetApp.getUi().alert("Vui lòng bôi đen các dòng dữ liệu (từ dòng 2 trở đi) để chạy AI viết Tiêu đề!");
    return;
  }
  
  SpreadsheetApp.getActiveSpreadsheet().toast('Đang gọi AI sinh Tiêu đề tối ưu...', 'Vui lòng đợi', -1);
  
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  function getIdx(name) { return headers.indexOf(name); }
  
  // Ánh xạ cột trên sheet Source theo đúng schema thực tế
  var cols = {
    tieuDePublic: getIdx("tieu_de"),       // Cột E (index 4)
    dienTich: getIdx("dien_tich"),         // Cột F (index 5)
    soTang: getIdx("so_tang"),             // Cột G (index 6)
    matTien: getIdx("mat_tien"),           // Cột H (index 7)
    gia: getIdx("gia"),                    // Cột I (index 8)
    quan: getIdx("quan"),                  // Cột J (index 9)
    phuong: getIdx("phuong"),              // Cột K (index 10)
    loaiHinh: getIdx("loai_hinh"),         // Cột L (index 11)
    huongNha: getIdx("huong_nha"),         // Cột M (index 12)
    duongTruocNha: getIdx("duong_truoc_nha"), // Cột N (Phân loại Hẻm) (index 13)
    doRongHem: getIdx("do_rong_hem"),      // Cột O (Đường trước nhà m) (index 14)
    moTa: getIdx("moTa"),                  // Cột T (Mô tả Public) (index 19)
    soPn: getIdx("so_pn"),                 // Cột AG (index 32)
    tenDuong: getIdx("ten_duong"),         // Cột AI (index 34)
    tieuDeBds: getIdx("Tiêu đề BDS")        // Cột AN (Cột thứ 40, index 39)
  };
  
  // Trực quan hóa fallback nếu getIdx viết thường không ra
  if (cols.tieuDeBds === -1) cols.tieuDeBds = getIdx("tieu_de_bds");
  if (cols.moTa === -1) cols.moTa = getIdx("mo_ta");
  
  if (cols.tieuDeBds === -1) {
    SpreadsheetApp.getUi().alert("Lỗi: Không tìm thấy cột 'Tiêu đề BDS' (Cột AN) trên sheet Source. Vui lòng thêm cột AN trước!");
    return;
  }
  
  var dataRange = sheet.getRange(startRow, 1, numRows, sheet.getLastColumn());
  var data = dataRange.getValues();
  var successCount = 0;
  
  var systemPrompt = "Bạn là AI chuyên viết tiêu đề BDS tối ưu chuẩn SEO cho trang batdongsan.com.vn.\n" +
                     "Nhiệm vụ: Nhận thông tin nhà và sinh ra duy nhất một Tiêu đề BDS cực kỳ thu hút, KHÔNG QUÁ 85 KÝ TỰ.\n\n" +
                     "🚨 QUY TẮC RÀNG BUỘC CỦA TIÊU ĐỀ BDS:\n" +
                     "1. GIỚI HẠN: Tiêu đề phải dưới 85 ký tự (an toàn nhất là từ 70 - 80 ký tự).\n" +
                     "2. CÚ PHÁP: `[HXH] [Tên đường] - [Diện tích]m2 - [1 hoặc 2 ưu điểm ngắn] - [Giá] tỷ [Quận]`\n" +
                     "3. ĐIỀU KIỆN TIỀN TỐ HXH (RẤT QUAN TRỌNG):\n" +
                     "   - Chỉ thêm chữ `HXH ` đứng trước tên đường (Ví dụ: `HXH Đường CMT8`) nếu hẻm rộng >= 4.0m HOẶC phân loại hẻm có chứa chữ \"xe hơi\", \"ô tô\", \"oto\".\n" +
                     "   - Nếu nhà là Mặt tiền hoặc hẻm dưới 4.0m và không thuộc phân loại trên, TUYỆT ĐỐI KHÔNG thêm chữ `HXH ` mà chỉ để tên đường thông thường (Ví dụ: `Đường CMT8`).\n" +
                     "4. ĐỊA DANH QUẬN: Chỉ viết tắt quận ở cuối tiêu đề (Ví dụ: `Q.3`, `Q.10`, `Q.PN`, `Q.TB`). Tuyệt đối KHÔNG đưa tên Phường vào tiêu đề.\n" +
                     "5. ƯU ĐIỂM: Trích xuất các ưu điểm siêu ngắn từ mô tả, ví dụ: Ngang rộng (nếu ngang >= 4.5m), Cao tầng (nếu >= 4 tầng), 3PN/4PN (nếu >= 3 phòng), Full nội thất, Gần Hadocentrosa, v.v.\n\n" +
                     "TRẢ VỀ ĐÚNG FORMAT JSON DƯỚI ĐÂY, KHÔNG CHỨA BẤT KỲ VĂN BẢN NÀO KHÁC:\n" +
                     "{\n" +
                     "  \"tieuDeBds\": \"Nội dung tiêu đề dưới 85 ký tự\"\n" +
                     "}";
  
  for (var i = 0; i < data.length; i++) {
    var rowData = data[i];
    
    // Đọc các giá trị dữ liệu từ dòng
    var tenDuong = rowData[cols.tenDuong] || "";
    var dt = rowData[cols.dienTich] || "";
    var gia = rowData[cols.gia] || "";
    var quan = rowData[cols.quan] || "";
    var phuong = rowData[cols.phuong] || "";
    var loaiHinh = rowData[cols.loaiHinh] || "";
    var phanLoaiHem = rowData[cols.duongTruocNha] || "";
    var doRongHem = rowData[cols.doRongHem] || "";
    var soTang = rowData[cols.soTang] || "";
    var matTien = rowData[cols.matTien] || "";
    var soPn = rowData[cols.soPn] || "";
    var moTaChiTiet = rowData[cols.moTa] || rowData[cols.tieuDePublic] || "";
    
    var userPrompt = "THÔNG TIN CĂN NHÀ:\n" +
                     "- Đường: " + tenDuong + " | Phường: " + phuong + " | Quận: " + quan + "\n" +
                     "- Diện tích: " + dt + "m2 | Chiều ngang: " + matTien + "m | Kết cấu: " + soTang + " tầng, " + soPn + " PN\n" +
                     "- Loại hình: " + loaiHinh + " | Phân loại hẻm: " + phanLoaiHem + " (Rộng: " + doRongHem + "m)\n" +
                     "- Giá: " + gia + " tỷ\n" +
                     "- Mô tả tóm tắt: " + moTaChiTiet;
    
    var resultObj = callOpenAI_Source(systemPrompt, userPrompt);
    
    if (resultObj && resultObj.tieuDeBds) {
      // Ghi kết quả trực tiếp vào cột AN (Tiêu đề BDS)
      sheet.getRange(startRow + i, cols.tieuDeBds + 1).setValue(resultObj.tieuDeBds.trim());
      successCount++;
    }
  }
  
  SpreadsheetApp.getActiveSpreadsheet().toast('Đã hoàn thành viết Tiêu đề BDS!', 'Hoần tất');
  SpreadsheetApp.getUi().alert("✅ Đã dùng AI viết thành công " + successCount + " Tiêu đề BDS dưới 85 ký tự!");
}

/**
 * Hàm gọi OpenAI API phục vụ Viết Tiêu đề BDS
 */
function callOpenAI_Source(systemPrompt, userPrompt) {
  if (!OPENAI_API_KEY) return null;
  
  var payload = {
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "system", "content": systemPrompt},
      {"role": "user", "content": userPrompt}
    ],
    "temperature": 0.3,
    "response_format": { "type": "json_object" }
  };
  
  var options = {
    "method": "post",
    "headers": {
      "Authorization": "Bearer " + OPENAI_API_KEY,
      "Content-Type": "application/json"
    },
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };
  
  try {
    var response = UrlFetchApp.fetch("https://api.openai.com/v1/chat/completions", options);
    var json = JSON.parse(response.getContentText());
    if (json.choices && json.choices.length > 0) {
      return JSON.parse(json.choices[0].message.content.trim());
    }
  } catch (e) {
    console.error("Lỗi gọi OpenAI API từ Source:", e);
  }
  return null;
}

// ==========================================
// TÍNH NĂNG 3: TIỆN ÍCH DỮ LIỆU ĐỊA CHỈ & TÊN ĐƯỜNG
// ==========================================

/**
 * Giải mã số nhà và tách tên đường từ cột tieu_de, sau đó gộp lại ghi vào cột đích
 */
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
  // Vòng lặp bắt đầu từ hàng 3 (index là 2) để bỏ qua hàng tiêu đề
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

/**
 * Chỉ trích xuất tên đường sạch từ tieu_de và ghi vào cột được chọn
 */
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

// ==========================================
// HÀM PHỤ TRỢ CHUNG (UTILITIES)
// ==========================================

/**
 * Chuyển ký tự ID sang số nhà (Giữ nguyên chữ thường, S=6, I=.)
 */
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

/**
 * Tách tên đường từ tieu_de và làm sạch các từ khóa thừa
 */
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
  var pattern = new RegExp("^(" + filterWords.join("|") + ")\\s*", "gi");
  
  var cleanedStreet = streetPart;
  while (pattern.test(cleanedStreet)) {
    cleanedStreet = cleanedStreet.replace(pattern, "").trim();
  }

  return cleanedStreet;
}

/**
 * Chuyển chữ cái cột (A, B, AJ...) thành số thứ tự (1-indexed)
 */
function columnLetterToIndex(letter) {
  var column = 0;
  for (var i = 0; i < letter.length; i++) {
    column += (letter.charCodeAt(i) - 64) * Math.pow(26, letter.length - i - 1);
  }
  return column;
}

/**
 * Tự động di cư hình ảnh đã qua xử lý Cloudinary từ Pool sang Source (Public) sheet (US-046.2)
 * Chạy trực tiếp từ trang quản trị Source.
 * Chỉ cập nhật các dòng có liên kết hình ảnh gốc Thien Khoi hoặc trống,
 * bảo toàn nguyên vẹn 100% nội dung đã biên tập (Tiêu đề, Mô tả, Giá Public) của Admin.
 */
function migrateSourceImages() {
  var POOL_FILE_ID = "1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw"; // ID File Pool BDS
  
  var ui = SpreadsheetApp.getUi();
  var response = ui.alert(
    "🚀 Di cư Ảnh Cloudinary từ Pool sang Source",
    "Hệ thống sẽ kết nối sang file Pool BDS, tìm ảnh Cloudinary tương ứng bằng System ID để cập nhật đè sang Source sheet hiện tại (Chỉ đè các ô chứa ảnh gốc Thien Khoi hoặc trống, BẢO TOÀN NGUYÊN VẸN Tiêu đề, Mô tả, Giá Public đã biên tập).\n\nBạn có chắc chắn muốn chạy tiến trình di cư hàng loạt này không?",
    ui.ButtonSet.YES_NO
  );
  
  if (response !== ui.Button.YES) {
    return;
  }
  
  SpreadsheetApp.getActiveSpreadsheet().toast('Đang kết nối sang file Pool BDS để lấy dữ liệu ảnh...', 'Vui lòng đợi', -1);
  
  try {
    var activeSS = SpreadsheetApp.getActiveSpreadsheet();
    var sourceSheet = activeSS.getSheetByName("Public") 
                   || activeSS.getSheetByName("Source") 
                   || activeSS.getSheets()[0];
                   
    var poolSpreadsheet = SpreadsheetApp.openById(POOL_FILE_ID);
    var poolSheet = poolSpreadsheet.getSheetByName("Pool") || poolSpreadsheet.getSheets()[0];
    
    var poolData = poolSheet.getDataRange().getValues();
    var sourceData = sourceSheet.getDataRange().getValues();
    
    if (poolData.length < 2 || sourceData.length < 2) {
      ui.alert("Lỗi: Dữ liệu của một trong hai Sheet trống rỗng!");
      return;
    }
    
    // 1. Tìm hàng chứa tiêu đề của Source một cách động (thông thường là Hàng 2 hoặc Hàng 1)
    var sourceHeaderIdx = -1;
    for (var r = 0; r < Math.min(sourceData.length, 5); r++) {
      var row = sourceData[r];
      var hasId = false;
      var hasTieuDe = false;
      for (var c = 0; c < row.length; c++) {
        var val = row[c].toString().trim().toLowerCase();
        if (val === "id" || val === "mã khang ngô (id)" || val === "ma_kn") hasId = true;
        if (val === "tieu_de" || val === "tiêu đề public" || val === "tieu_de_public") hasTieuDe = true;
      }
      if (hasId || hasTieuDe) {
        sourceHeaderIdx = r;
        break;
      }
    }
    if (sourceHeaderIdx === -1) {
      sourceHeaderIdx = sourceData.length > 1 ? 1 : 0;
    }
    var sourceHeaders = sourceData[sourceHeaderIdx];
    
    // 2. Tìm hàng chứa tiêu đề của Pool một cách động
    var poolHeaderIdx = -1;
    for (var r = 0; r < Math.min(poolData.length, 5); r++) {
      var row = poolData[r];
      var hasMaHang = false;
      for (var c = 0; c < row.length; c++) {
        var val = row[c].toString().trim().toLowerCase();
        if (val === "mã hàng" || val === "ma_hang" || val === "system id" || val === "system_id") {
          hasMaHang = true;
          break;
        }
      }
      if (hasMaHang) {
        poolHeaderIdx = r;
        break;
      }
    }
    if (poolHeaderIdx === -1) poolHeaderIdx = 0;
    var poolHeaders = poolData[poolHeaderIdx];
    
    // Hàm tìm chỉ mục cột động, loại bỏ khoảng trắng, dấu gạch dưới và không phân biệt chữ hoa thường
    function findColumnIndex(headers, possibleNames) {
      for (var i = 0; i < headers.length; i++) {
        var hClean = headers[i].toString().trim().toLowerCase()
                       .replace(/\s+/g, '')
                       .replace(/_/g, '');
        for (var j = 0; j < possibleNames.length; j++) {
          var pClean = possibleNames[j].toLowerCase()
                         .replace(/\s+/g, '')
                         .replace(/_/g, '');
          if (hClean === pClean) {
            return i;
          }
        }
      }
      return -1;
    }
    
    // Tìm cột System ID ở cả 2 sheet để khớp nối
    var poolSysIdIdx = findColumnIndex(poolHeaders, ["System ID", "system_id", "sys_id"]);
    var sourceSysIdIdx = findColumnIndex(sourceHeaders, ["System ID", "system_id", "sys_id"]);
    
    if (poolSysIdIdx === -1) {
      ui.alert("Lỗi: Không tìm thấy cột 'System ID' ở tab Pool!");
      return;
    }
    if (sourceSysIdIdx === -1) {
      // Fallback về cột AI (index 34) nếu không quét ra
      sourceSysIdIdx = 34;
    }
    
    // Ánh xạ các cột ảnh tương ứng giữa Source và Pool
    var IMAGE_HEADERS = [
      { source: ["anh_1", "anh1"], pool: ["Ảnh 1", "anh_1", "anh1"] },
      { source: ["anh_2", "anh2"], pool: ["Ảnh 2", "anh_2", "anh2"] },
      { source: ["anh_3", "anh3"], pool: ["Ảnh 3", "anh_3", "anh3"] },
      { source: ["anh_4", "anh4"], pool: ["Ảnh 4", "anh_4", "anh4"] },
      { source: ["anh_5", "anh5"], pool: ["Ảnh 5", "anh_5", "anh5"] },
      { source: ["anh_6", "anh6"], pool: ["Ảnh 6", "anh_6", "anh6"] },
      { source: ["anh_7", "anh7"], pool: ["Ảnh 7", "anh_7", "anh7"] },
      { source: ["anh_8", "anh8"], pool: ["Ảnh 8", "anh_8", "anh8"] },
      { source: ["anh_9", "anh9"], pool: ["Ảnh 9", "anh_9", "anh9"] },
      { source: ["anh_10", "anh10"], pool: ["Ảnh 10", "anh_10", "anh10"] }
    ];
    
    var sourceColIndices = [];
    var poolColIndices = [];
    for (var k = 0; k < IMAGE_HEADERS.length; k++) {
      sourceColIndices.push(findColumnIndex(sourceHeaders, IMAGE_HEADERS[k].source));
      poolColIndices.push(findColumnIndex(poolHeaders, IMAGE_HEADERS[k].pool));
    }
    
    // Tạo Map dữ liệu Pool theo System ID để tăng tốc O(N)
    var poolMap = {};
    for (var i = poolHeaderIdx + 1; i < poolData.length; i++) {
      var sysId = poolData[i][poolSysIdIdx];
      if (sysId) {
        poolMap[sysId.toString().trim().toUpperCase()] = poolData[i];
      }
    }
    
    // Xác định dải cột ảnh để tối ưu hóa việc ghi hàng loạt theo từng dòng
    var minImgCol = 999;
    var maxImgCol = -1;
    for (var k = 0; k < IMAGE_HEADERS.length; k++) {
      var sCol = sourceColIndices[k];
      if (sCol !== -1) {
        if (sCol < minImgCol) minImgCol = sCol;
        if (sCol > maxImgCol) maxImgCol = sCol;
      }
    }
    
    var updateCount = 0;
    
    // Quét từng dòng bên Source (Dữ liệu bắt đầu từ dòng ngay sau hàng tiêu đề)
    for (var j = sourceHeaderIdx + 1; j < sourceData.length; j++) {
      var sysIdSource = sourceData[j][sourceSysIdIdx];
      if (!sysIdSource) continue;
      sysIdSource = sysIdSource.toString().trim().toUpperCase();
      
      if (poolMap[sysIdSource]) {
        var poolRow = poolMap[sysIdSource];
        var rowNeedsUpdate = false;
        
        // Quét các cột ảnh để phát hiện link gốc Thien Khoi / tk-assets hoặc rỗng
        for (var k = 0; k < IMAGE_HEADERS.length; k++) {
          var sCol = sourceColIndices[k];
          var pCol = poolColIndices[k];
          
          if (sCol !== -1 && pCol !== -1 && sCol < sourceHeaders.length && pCol < poolHeaders.length) {
            var sVal = sourceData[j][sCol].toString().trim();
            var pVal = poolRow[pCol].toString().trim();
            
            // Nhận diện liên kết ảnh cũ cần được di cư (Thien Khoi, tk-assets, hoặc spms2)
            var isOldImage = sVal.toLowerCase().indexOf("thienkhoi") !== -1 
                          || sVal.toLowerCase().indexOf("tk-assets") !== -1 
                          || sVal.toLowerCase().indexOf("spms2") !== -1;
            
            if (sVal !== pVal && (isOldImage || sVal === "")) {
              // Cập nhật giá trị trong bộ nhớ
              sourceData[j][sCol] = pVal;
              rowNeedsUpdate = true;
            }
          }
        }
        
        // Nếu dòng này cần cập nhật, ghi đè duy nhất cụm cột ảnh của dòng này lên Sheet
        if (rowNeedsUpdate && minImgCol !== 999 && maxImgCol !== -1) {
          var imgRowSegment = [];
          for (var c = minImgCol; c <= maxImgCol; c++) {
            imgRowSegment.push(sourceData[j][c]);
          }
          // Ghi đè cụm cột ảnh trong 1 lệnh duy nhất cho dòng hiện tại (tránh dịch vụ lỗi - bảng tính)
          sourceSheet.getRange(j + 1, minImgCol + 1, 1, imgRowSegment.length).setValues([imgRowSegment]);
          updateCount++;
        }
      }
    }
    
    SpreadsheetApp.getActiveSpreadsheet().toast('Đã hoàn tất di cư ảnh!', 'Thành công');
    ui.alert("✅ HOÀN TẤT DI CƯ!\n\nĐã đồng bộ ảnh Cloudinary thành công cho " + updateCount + " căn trên sheet Source.\nToàn bộ tiêu đề, mô tả và giá public đã được bảo toàn nguyên vẹn.");
    
  } catch (err) {
    SpreadsheetApp.getActiveSpreadsheet().toast('Gặp lỗi khi di cư ảnh', 'Thất bại');
    ui.alert("❌ Lỗi xảy ra: " + err.message);
  }
}

