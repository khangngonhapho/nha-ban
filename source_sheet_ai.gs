// ==========================================
// SOURCE SHEET AI SEO - TOOL VIẾT TIÊU ĐỀ BDS (<85 KÝ TỰ)
// Hỗ trợ viết Tiêu đề BDS trực tiếp trên sheet Source bằng GPT-4o-mini
// ==========================================

// 0. CẤU HÌNH API KEY (Sử dụng API Key OpenAI hiện tại)
var OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"; // Điền OpenAI API Key của bạn vào đây

/**
 * Tạo Menu khi mở file Source (BDS_KhangNgo_Source)
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 AI SEO Tools')
      .addItem('Tự động viết Tiêu đề BDS (<85 ký tự) cho dòng chọn', 'batchGenerateTieuDeBdsAI')
      .addToUi();
}

/**
 * Xử lý hàng loạt các dòng đang được bôi đen (Active Range) trên sheet Source
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
  
  SpreadsheetApp.getActiveSpreadsheet().toast('Đã hoàn thành viết Tiêu đề BDS!', 'Hoàn tất');
  SpreadsheetApp.getUi().alert("✅ Đã dùng AI viết thành công " + successCount + " Tiêu đề BDS dưới 85 ký tự!");
}

/**
 * Hàm gọi OpenAI API
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
