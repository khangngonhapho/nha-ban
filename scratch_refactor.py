import json

with open(r'd:\LHTBrain\01_PROJECTS\BDS-KhangNgo\pool_backend_v3.gs', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Part 1: line 1 to 736 (index 0 to 735)
part1 = "".join(lines[0:736])

# Part 2: line 875 to 937 (index 874 to 936)
part2 = "".join(lines[874:937])

new_ai_logic = """
// -----------------------------------------------------
// KHANG NGÔ AI TOOL - HỆ THỐNG GỌI AI HỢP NHẤT (DRY)
// -----------------------------------------------------
var OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxEXXf4A";

/**
 * Hàm gọi OpenAI API dùng chung
 * @param {string} systemPrompt 
 * @param {string} userPrompt 
 * @returns {object|null} JSON object trả về từ API
 */
function callOpenAI_Unified(systemPrompt, userPrompt) {
  if (!OPENAI_API_KEY || OPENAI_API_KEY.includes("xxxxxxxx")) return null;
  
  var payload = {
    "model": "gpt-4o-mini", // Model tối ưu chi phí và thông minh
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
    console.error("Lỗi gọi OpenAI API:", e);
  }
  return null;
}

/**
 * Xử lý hàng loạt các dòng đang được bôi đen (Active Range)
 * Gộp chung việc tra Phường Cũ và viết Tiêu đề + Mô tả vào 1 hàm duy nhất.
 */
function batchGenerateContentAndWard() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var range = sheet.getActiveRange();
  var startRow = range.getRow();
  var numRows = range.getNumRows();
  
  if (startRow <= 1) {
    SpreadsheetApp.getUi().alert("Vui lòng bôi đen các dòng dữ liệu (từ dòng 2 trở đi) để chạy AI.");
    return;
  }
  
  SpreadsheetApp.getActiveSpreadsheet().toast('Đang nhờ AI phân tích dữ liệu...', 'Vui lòng đợi', -1);
  
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  function getIdx(name) { return headers.indexOf(name); }
  
  var cols = {
    soNha: getIdx("Ngõ/Số nhà"), duong: getIdx("Đường"), phuong: getIdx("Phường"), quan: getIdx("Quận"),
    dt: getIdx("DT Thực tế"), ngang: getIdx("Mặt Tiền"), tang: getIdx("Số Tầng"), gia: getIdx("Giá Public"),
    phongNgu: getIdx("Số phòng ngủ"), wc: getIdx("Số nhà vệ sinh"),
    hem: getIdx("Phân loại Hẻm"), rongHem: getIdx("Đường trước nhà (m)"),
    moTaGoc: getIdx("Mô tả chi tiết"), noiDungChinh: getIdx("Nội dung chính"),
    phuongCuOut: getIdx("Phường cũ (AI)"), tieuDeOut: getIdx("Tiêu đề Public"), moTaOut: getIdx("Mô tả Public")
  };
  
  if (cols.tieuDeOut === -1 || cols.moTaOut === -1 || cols.phuongCuOut === -1) {
    SpreadsheetApp.getUi().alert("Không tìm thấy đủ các cột: Tiêu đề Public, Mô tả Public, Phường cũ (AI).");
    return;
  }
  
  var dataRange = sheet.getRange(startRow, 1, numRows, sheet.getLastColumn());
  var data = dataRange.getValues();
  var successCount = 0;
  
  // Prompt Đóng vai cố định
  var systemPrompt = "Bạn đóng vai một Chuyên gia môi giới nhà phố 15 năm kinh nghiệm tại trung tâm TP.HCM.\\nNhiệm vụ của bạn là nhận thông tin của 1 căn nhà và sinh ra bài đăng chuyên nghiệp, đồng thời tìm ra 'Phường cũ' của địa chỉ nhà trước khi sáp nhập hành chính (nếu có).\\n\\n🚨 CÁC QUY TẮC BẮT BUỘC:\\n1. Tiêu đề: Không giới hạn số lượng ký tự. Cấu trúc: [Tên đường - Phường - Quận - Diện tích - Ưu điểm nổi bật - Giá]. Kèm dấu '-' trước giá. TUYỆT ĐỐI KHÔNG đưa số nhà thật vào tiêu đề. TUYỆT ĐỐI KHÔNG tự động chèn tiền tố '🚘 HXH - ' vào đầu. Tại phần 'Ưu điểm nổi bật', dùng ngôn từ mạnh mẽ nêu bật các Điểm Bán Hàng Độc Nhất (USP).\\n2. Mô tả: Trình bày gọn gàng, cách nhau bằng 1 dòng trống.\\n   - Vị trí: Quận, Phường (mới). Đặc điểm hẻm... TUYỆT ĐỐI KHÔNG ghi số nhà thật.\\n   - Kết cấu: ...\\n   - Kết nối & Tiện ích: ...\\n   - Pháp lý: ...\\n3. Phường cũ: Suy luận tên Phường gốc của căn nhà dựa vào tên đường, địa chỉ trước đợt sáp nhập hành chính. Trả về trống nếu không đổi hoặc không chắc chắn.\\n\\nTRẢ VỀ ĐÚNG FORMAT JSON DƯỚI ĐÂY, KHÔNG ĐƯỢC CHỨA BẤT KỲ VĂN BẢN NÀO KHÁC BÊN NGOÀI:\\n{\\n  \\\"tieuDe\\\": \\\"Nội dung tiêu đề\\\",\\n  \\\"moTa\\\": \\\"Nội dung mô tả\\\",\\n  \\\"phuongCu\\\": \\\"Tên phường cũ\\\"\\n}";
  
  for (var i = 0; i < data.length; i++) {
    var rowData = data[i];
    
    // Nếu cả 3 trường đều ĐÃ CÓ data thì bỏ qua dòng này
    if (rowData[cols.tieuDeOut] && rowData[cols.moTaOut] && rowData[cols.phuongCuOut]) {
      continue;
    }
    
    // Xử lý Giá
    var giaGoc = rowData[cols.gia] || 0;
    var giaTy = parseFloat(giaGoc);
    if (!isNaN(giaTy) && giaTy > 100) giaTy = giaTy / 1000;
    var giaFormat = (giaTy > 0) ? giaTy + " tỷ" : "";
    
    // Xử lý Tiền tố (Chỉ gán nếu Mặt tiền)
    var loaiHem = (rowData[cols.hem] || "").toString().toLowerCase().trim();
    var tienTo = "";
    if (loaiHem.includes("mặt tiền")) {
      tienTo = "Mặt tiền - ";
    }
    
    var userPrompt = "THÔNG TIN CĂN NHÀ:\\n" +
      "- Địa chỉ: " + (rowData[cols.soNha]||"") + " " + (rowData[cols.duong]||"") + ", Phường " + (rowData[cols.phuong]||"") + ", Quận " + (rowData[cols.quan]||"") + "\\n" +
      "- Diện tích: " + (rowData[cols.dt]||"") + "m2\\n" +
      "- Ngang: " + (rowData[cols.ngang]||"") + "m\\n" +
      "- Kết cấu: " + (rowData[cols.tang]||"") + " tầng, " + (rowData[cols.phongNgu]||"") + " PN, " + (rowData[cols.wc]||"") + " WC\\n" +
      "- Hẻm: " + (rowData[cols.hem]||"") + " (Rộng: " + (rowData[cols.rongHem]||"") + "m)\\n" +
      "- Giá: " + giaFormat + "\\n" +
      "- Nội dung chính: " + (rowData[cols.noiDungChinh]||"") + "\\n" +
      "- Mô tả gốc từ đầu chủ: " + (rowData[cols.moTaGoc]||"") + "\\n\\n" +
      "LƯU Ý: Nếu nhà là Mặt tiền, BẮT BUỘC chèn cụm '" + tienTo + "' vào đầu Tiêu đề.";
      
    var resultObj = callOpenAI_Unified(systemPrompt, userPrompt);
    
    if (resultObj) {
      if (resultObj.tieuDe && !rowData[cols.tieuDeOut]) sheet.getRange(startRow + i, cols.tieuDeOut + 1).setValue(resultObj.tieuDe);
      if (resultObj.moTa && !rowData[cols.moTaOut]) sheet.getRange(startRow + i, cols.moTaOut + 1).setValue(resultObj.moTa);
      if (resultObj.phuongCu && !rowData[cols.phuongCuOut]) sheet.getRange(startRow + i, cols.phuongCuOut + 1).setValue(resultObj.phuongCu);
      successCount++;
    }
  }
  
  SpreadsheetApp.getUi().alert("✅ Đã xử lý xong Content AI & Phường cũ cho " + successCount + " dòng!");
}
"""

with open(r'd:\LHTBrain\01_PROJECTS\BDS-KhangNgo\pool_backend_v3.gs', 'w', encoding='utf-8') as f:
    f.write(part1)
    f.write(part2)
    f.write(new_ai_logic)
