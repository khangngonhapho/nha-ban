// ==========================================
// THIEN KHOI BĐS CRAWLER - BACKEND v3
// Hỗ trợ Tự động Mã hóa ID & Trigger Đẩy sang Public
//
// [Latest Update / User Story]
// - US-151: Tự động dò tìm dòng header và vị trí cột trên sheet Source khi đồng bộ (Cập nhật ngày 2026-07-17)
// - US-147: Loại bỏ bước gọi AI tự động trong luồng background worker di cư ảnh (Cập nhật ngày 2026-07-14)
// ==========================================

const PUBLIC_FILE_ID = "1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE"; // File BDS_KhangNgo_Source
const PUBLIC_TAB_NAME = "Source"; // Tên tab Source

// 1. XỬ LÝ GET REQUEST (Tránh lỗi CORS & Lấy danh sách ID + Địa chỉ để Extension quét)
function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  if (!sheet) {
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": "Sheet không tồn tại"})).setMimeType(ContentService.MimeType.JSON);
  }
  
  var lastRow = sheet.getLastRow();
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  
  // Tính năng mới: Lấy full data của 1 mã hàng cụ thể để hiển thị lại UI trên Extension
  if (e.parameter && e.parameter.id) {
    var searchId = e.parameter.id.toString().trim();
    if (lastRow >= 2) {
      var allData = sheet.getRange(2, 1, lastRow - 1, headers.length).getValues();
      for (var i = 0; i < allData.length; i++) {
        if (allData[i][0].toString().trim() === searchId) {
           // Đóng gói thành object JSON có key là tên cột
           var rowObj = {};
           for (var j = 0; j < headers.length; j++) {
             rowObj[headers[j]] = allData[i][j];
           }
           return ContentService.createTextOutput(JSON.stringify({"status": "success", "data": rowObj})).setMimeType(ContentService.MimeType.JSON);
        }
      }
    }
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": "Not found"})).setMimeType(ContentService.MimeType.JSON);
  }
  
  var maHangs = [];
  
  if (lastRow >= 2) {
    var data = sheet.getRange(2, 1, lastRow - 1, 6).getValues();
    maHangs = data.map(function(row) { 
      var id = row[0].toString().trim();
      var duong = row[4].toString().trim();
      var ngo = row[5].toString().trim();
      var address = (ngo + " " + duong).replace(/\s+/g, ' ').trim().toLowerCase();
      
      return { id: id, address: address };
    }).filter(function(v) { 
      return v.id !== ""; 
    });
  }
  
  return ContentService.createTextOutput(JSON.stringify({"status": "success", "data": maHangs}))
    .setMimeType(ContentService.MimeType.JSON);
}

// 2. XỬ LÝ POST REQUEST (Lưu dữ liệu, Tự động Hash ID)
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    
    // Đảm bảo có headers
    createHeaders(sheet);
    
    var data = JSON.parse(e.postData.contents);
    var maHangMoi = (data.maHang || "").toString().trim();
    
    // Check trùng lặp
    // Dời check trùng lặp xuống dưới để xây dựng rowData trước
    
    // Sinh Mã Khang Ngô tự động
    var maKhangNgo = generateKhangNgoId(data.ngoSoNha || "", data.duong || "");
    
    var imagesTD = data.imagesTD || [];
    var images = data.images || [];
    
    // Xử lý Hình Thửa Đất (giữ nguyên gốc)
    var sodoImgs = [imagesTD[0] || "", imagesTD[1] || ""];

    // Xử lý Hình Nội Dung (ndSelections) từ Extension V13
    var matTienImg = data.ndMatTienImg || "";
    var hemImgs = data.ndHemImgs || [];
    var hemPublicIndices = data.ndHemPublicIndices || "";
    var noithatPublicIndices = data.ndNoithatPublicIndices || "";
    
    // Tự động phân loại nếu là mặt tiền
    var diaChi = (data.ngoSoNha || "").toString();
    var isHem = diaChi.includes(".");
    var phanLoaiHemDau = isHem ? "" : "Mặt tiền đường";
    
    var duongTruocNhaScraped = data.duongTruocNha || "";
    var widthScraped = parseFloat(duongTruocNhaScraped);
    if (isHem && !isNaN(widthScraped) && widthScraped < 3.5) {
       phanLoaiHemDau = "Hẻm ba gác";
    }

    // Công thức Hình Nhận Diện trỏ thẳng về ô "Hình Mặt Tiền" (Cột AD) của chính dòng đó
    var nextRow = sheet.getLastRow() + 1;
    var hinhNhanDien = '=IMAGE(AD' + nextRow + ')';

    var rowData = [
      data.maHang || "", hinhNhanDien, data.tinh || "", data.quan || "", data.phuong || "", data.duong || "", data.ngoSoNha || "", data.phanLoai || "", data.namXayDung || "",
      (data.noiDungChinh || "").replace(/\r\n|\r|\n/g, ' '), data.moTaChiTiet || "", data.giaChao || "", data.giaChot || "", data.dtThucTe || "", data.dtTrenSo || "", data.soTang || "",
      data.matTien || "", data.huong || "", data.chuNha || "", data.dienThoai1 || "", data.dienThoai2 || "", data.loaiHopDong || "", data.soNgayKy || "",
      data.ngayBatDau || "", data.ngayKetThuc || "", data.nguoiKy || "", data.trangThai || "",
      sodoImgs[0] || "", sodoImgs[1] || "",
      // Hình Mặt Tiền và 10 Hình Hẻm
      matTienImg,
      hemImgs[0] || "", hemImgs[1] || "", hemImgs[2] || "", hemImgs[3] || "", hemImgs[4] || "",
      hemImgs[5] || "", hemImgs[6] || "", hemImgs[7] || "", hemImgs[8] || "", hemImgs[9] || "",
      images[0] || "", images[1] || "", images[2] || "", images[3] || "", images[4] || "", images[5] || "", images[6] || "", images[7] || "",
      images[8] || "", images[9] || "", images[10]|| "", images[11]|| "", images[12]|| "", images[13]|| "", images[14]|| "",
      // BẮT ĐẦU CÁC CỘT "COOKED" (Từ cột AR trở đi)
      maKhangNgo,         // Mã Khang Ngô
      "",                 // Tiêu đề Public (Admin tự điền)
      "",                 // Mô tả Public (Admin tự điền)
      data.giaChao || "", // Giá Public (Mặc định lấy giá chào)
      phanLoaiHemDau,     // Phân loại Hẻm
      duongTruocNhaScraped, // Đường trước nhà (m)
      "Bình thường",      // Tình trạng nhà
      noithatPublicIndices, // Ảnh Public (VD: 1,3,5)
      hemPublicIndices,   // Ảnh Hẻm Public (VD: 1,2)
      data.soPhongNgu || "", // Số phòng ngủ
      data.soToilet || "",   // Số nhà vệ sinh
      "",                    // Phường cũ (AI)
      "",                    // Đánh giá (Admin)
      "",                    // Ngủ trệt (Admin)
      "",                    // CHDV (Admin)
      false,                 // Duyệt Public (Checkbox)
      "Chờ duyệt",           // Trạng thái Public
      "SYS-" + Date.now().toString(36).toUpperCase() + "-" + Math.floor(Math.random() * 1000).toString(36).toUpperCase(), // System ID (Tuyệt đối không trùng)
      data.sourceUrl || "",  // Link gốc
      data.dtDauChu || "",   // Điện thoại Đầu Chủ
      data.tenDauChu || "",  // Tên Đầu Chủ (Hợp đồng)
      data.linkFb || "",     // Điểm Facebook
      Utilities.formatDate(new Date(), "GMT+7", "dd/MM/yyyy HH:mm:ss"), // Last Crawl
      ""                     // Last Sync (sẽ được ghi khi Admin đẩy sang Source)
    ];
    
    var isUpdateMode = data.isUpdate === true;
    var foundRowIndex = -1;
    
    if (maHangMoi !== "") {
      var lastRow = sheet.getLastRow();
      if (lastRow >= 2) {
        var existData = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
        for (var i = 0; i < existData.length; i++) {
          if (existData[i][0].toString().trim() === maHangMoi) {
            foundRowIndex = i + 2;
            break;
          }
        }
      }
    }

    if (foundRowIndex > -1) {
      if (isUpdateMode) {
        var numCols = rowData.length;
        var headers = sheet.getRange(1, 1, 1, numCols).getValues()[0];
        var oldRowData = sheet.getRange(foundRowIndex, 1, 1, numCols).getValues()[0];
        
        var colsToKeep = ["Tiêu đề Public", "Mô tả Public", "Giá Public", "Phường cũ (AI)", "Đánh giá (Admin)", "Ngủ trệt (Admin)", "CHDV (Admin)", "System ID", "Trạng thái Public", "Duyệt Public"];
        
        var hasNewImages = (matTienImg !== "" || hemImgs.length > 0 || hemPublicIndices !== "" || noithatPublicIndices !== "");
        var imgCols = [
          "Hình Mặt Tiền", "Hình Hẻm 1", "Hình Hẻm 2", "Hình Hẻm 3", "Hình Hẻm 4", "Hình Hẻm 5", 
          "Hình Hẻm 6", "Hình Hẻm 7", "Hình Hẻm 8", "Hình Hẻm 9", "Hình Hẻm 10",
          "Ảnh 1", "Ảnh 2", "Ảnh 3", "Ảnh 4", "Ảnh 5", "Ảnh 6", "Ảnh 7", "Ảnh 8",
          "Ảnh 9", "Ảnh 10", "Ảnh 11", "Ảnh 12", "Ảnh 13", "Ảnh 14", "Ảnh 15",
          "Ảnh Public (VD: 1,3,5)", "Ảnh Hẻm Public (VD: 1,2)", "Hình Nhận Diện"
        ];
        
        var finalRowData = [];
        for (var c = 0; c < headers.length; c++) {
           var hName = headers[c];
           var newVal = (c < rowData.length) ? rowData[c] : "";
           
           if (colsToKeep.includes(hName)) {
              finalRowData.push(oldRowData[c]);
           } else if (!hasNewImages && imgCols.includes(hName)) {
              finalRowData.push(oldRowData[c]);
           } else {
              if (hName === "Hình Nhận Diện") {
                 finalRowData.push(""); // Bỏ trống để không bị lỗi setValues
              } else {
                 finalRowData.push(newVal);
              }
           }
        }
        
        for (var k = 0; k < finalRowData.length; k++) {
            var cellVal = finalRowData[k];
            if (cellVal === undefined || cellVal === null) {
                finalRowData[k] = "";
            } else if (typeof cellVal === 'string') {
                // Escape các string bắt đầu bằng =, +, - để setValues không bị crash do hiểu nhầm là formula lỗi
                if (cellVal.startsWith('=') && !cellVal.startsWith('=IMAGE')) {
                    finalRowData[k] = "'" + cellVal;
                } else if (cellVal.startsWith('+') || cellVal.startsWith('-')) {
                    finalRowData[k] = "'" + cellVal;
                }
            }
        }
        
        try {
            sheet.getRange(foundRowIndex, 1, 1, finalRowData.length).setValues([finalRowData]);
            
            // Ghi lại công thức bằng setFormula riêng để né lỗi Service error của setValues
            sheet.getRange(foundRowIndex, 2).setFormula('=IMAGE(AD' + foundRowIndex + ')');
        } catch (setErr) {
            // Fallback siêu hạng: Nếu setValues theo mảng bị crash, thử ghi từng ô một
            var errorLogs = [];
            for (var c = 0; c < finalRowData.length; c++) {
                try {
                    if (headers[c] === "Hình Nhận Diện") {
                        sheet.getRange(foundRowIndex, c + 1).setFormula('=IMAGE(AD' + foundRowIndex + ')');
                    } else {
                        sheet.getRange(foundRowIndex, c + 1).setValue(finalRowData[c]);
                    }
                } catch (cellErr) {
                    errorLogs.push("Cột " + (c+1) + " (" + headers[c] + "): " + cellErr.message);
                }
            }
            if (errorLogs.length > 0) {
                return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": "Lỗi Update: " + errorLogs.join(" | ")})).setMimeType(ContentService.MimeType.JSON);
            }
        }
        return ContentService.createTextOutput(JSON.stringify({"status": "success"})).setMimeType(ContentService.MimeType.JSON);
      } else {
        return ContentService.createTextOutput(JSON.stringify({"status": "duplicate", "message": "Trùng lặp!"})).setMimeType(ContentService.MimeType.JSON);
      }
    }
    
    for (var k = 0; k < rowData.length; k++) {
        var cellVal = rowData[k];
        if (cellVal === undefined || cellVal === null) {
            rowData[k] = "";
        } else if (typeof cellVal === 'string') {
            if (cellVal.startsWith('=') && !cellVal.startsWith('=IMAGE')) {
                rowData[k] = "'" + cellVal;
            } else if (cellVal.startsWith('+') || cellVal.startsWith('-')) {
                rowData[k] = "'" + cellVal;
            }
        }
    }

    try {
        sheet.appendRow(rowData);
    } catch (appendErr) {
        return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": "Lỗi appendRow: " + appendErr.message})).setMimeType(ContentService.MimeType.JSON);
    }
    
    // Set format Checkbox cho cột "Duyệt Public"
    // Tự động quét để tìm đúng cột "Duyệt Public" đề phòng thứ tự thay đổi
    var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    var checkColIndex = headers.indexOf("Duyệt Public") + 1;
    if (checkColIndex > 0) {
      try {
        sheet.getRange(sheet.getLastRow(), checkColIndex).insertCheckboxes();
      } catch (ignored) {
        // Lỗi "This operation is not allowed on cells in typed columns"
        // Nghĩa là user đã set sẵn định dạng Checkbox cho cả cột rồi, nên không cần insert nữa
      }
    }
    
    return ContentService.createTextOutput(JSON.stringify({"status": "success"})).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": error.toString()})).setMimeType(ContentService.MimeType.JSON);
  }
}

// 3. TRIGGER ONEDIT: Xử lý khi Admin bấm Checkbox Duyệt
// (LƯU Ý: Đổi tên thành onAdminReview để cài đặt Installable Trigger, tránh lỗi quyền truy cập file khác)
function onAdminReview(e) {
  var sheet = e.source.getActiveSheet();
  var range = e.range;
  var col = range.getColumn();
  var row = range.getRow();
  
  if (row <= 1) return;
  
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var checkColIndex = headers.indexOf("Duyệt Public") + 1;
  var statusColIndex = headers.indexOf("Trạng thái Public") + 1;
  var widthColIndex = headers.indexOf("Đường trước nhà (m)") + 1;
  var typeColIndex = headers.indexOf("Phân loại Hẻm") + 1;
  var lastSyncColIndex = headers.indexOf("Last Sync") + 1;
  
  // A. TỰ ĐỘNG PHÂN LOẠI HẺM KHI NHẬP ĐỘ RỘNG
  if (col === widthColIndex) {
    var width = parseFloat(range.getValue());
    if (!isNaN(width) && width < 3.5) {
      var currentType = sheet.getRange(row, typeColIndex).getValue();
      if (!currentType || currentType === "") {
        sheet.getRange(row, typeColIndex).setValue("Hẻm ba gác");
      }
    }
    return; // Không làm gì thêm ở hàm Edit này
  }
  
  // B. XỬ LÝ ĐỒNG BỘ PUBLIC
  if (col === checkColIndex && range.getValue() === true) {
    var statusCell = sheet.getRange(row, statusColIndex);
    
    // Nếu chưa cấu hình ID file public thì báo lỗi
    if (PUBLIC_FILE_ID === "ĐIỀN_ID_FILE_PUBLIC_CỦA_BẠN_VÀO_ĐÂY") {
      statusCell.setValue("Lỗi: Chưa cấu hình PUBLIC_FILE_ID");
      range.setValue(false); // Bỏ tick
      return;
    }
    
    statusCell.setValue("Đang đồng bộ...");
    
    try {
      var publicSpreadsheet = SpreadsheetApp.openById(PUBLIC_FILE_ID);
      var publicSheet = publicSpreadsheet.getSheetByName(PUBLIC_TAB_NAME) || publicSpreadsheet.getSheets()[0];
      
      var rowData = sheet.getRange(row, 1, 1, headers.length).getValues()[0];
      
      // Hàm tiện ích lấy value bằng tên cột
      function getVal(colName) {
        var idx = headers.indexOf(colName);
        return idx !== -1 ? rowData[idx] : "";
      }
      
      // Xử lý Quận
      function formatQuan(q) {
        if (!q) return "";
        var qLower = q.toLowerCase();
        if (qLower.includes("quận 3")) return "3";
        if (qLower.includes("quận 10")) return "10";
        if (qLower.includes("phú nhuận")) return "PN";
        if (qLower.includes("tân bình")) return "TB";
        return q;
      }
      
      // Xử lý Giá (Thiên Khôi lưu giá theo đơn vị triệu, VD 6900 = 6.9 tỷ)
      function formatGia(g) {
        if (!g) return "";
        var val = parseFloat(g.toString().replace(/,/g, ''));
        if (isNaN(val)) return g;
        if (val > 100) {
          return val / 1000;
        }
        return val;
      }
      
      // Xử lý Loại Hình (Hẻm / Mặt tiền)
      var diaChi = getVal("Ngõ/Số nhà");
      if (diaChi !== undefined && diaChi !== null) {
          diaChi = diaChi.toString();
      } else {
          diaChi = "";
      }
      var loaiHinh = diaChi.includes(".") ? "Hẻm" : "Mặt tiền";
      
      var finalImages = [];
      
      var anhDuocChon = getVal("Ảnh Public (VD: 1,3,5)").toString().replace(/\s/g, '');
      var anhHemDuocChon = getVal("Ảnh Hẻm Public (VD: 1,2)").toString().replace(/\s/g, '');
      
      if (anhDuocChon === "") {
        statusCell.setValue("Lỗi: Bạn chưa chọn Ảnh Nội thất an toàn!");
        range.setValue(false); // Bỏ tick
        return;
      }

      var noithatIndices = anhDuocChon.split(',');
      
      // 1. Ưu tiên Hình nền (Hình nội thất đầu tiên được chọn) đưa lên số 1
      var firstNoithatIdx = parseInt(noithatIndices[0]);
      if (!isNaN(firstNoithatIdx) && firstNoithatIdx >= 1 && firstNoithatIdx <= 15) {
         var coverImgUrl = getVal("Ảnh " + firstNoithatIdx);
         if (coverImgUrl) finalImages.push(coverImgUrl);
      }

      // 2. Tới Hình Hẻm
      var maxHem = 2; // Giới hạn đúng 2 ảnh Hẻm
      if (anhHemDuocChon !== "") {
        var hemIndices = anhHemDuocChon.split(',');
        var addedHem = 0;
        for (var i = 0; i < hemIndices.length && addedHem < maxHem; i++) {
          var hemIdx = parseInt(hemIndices[i]);
          if (!isNaN(hemIdx) && hemIdx >= 1 && hemIdx <= 10) {
            var hemUrl = getVal("Hình Hẻm " + hemIdx);
            if (hemUrl) {
              finalImages.push(hemUrl);
              addedHem++;
            }
          }
        }
      } else {
        // Lấy ngẫu nhiên tối đa 2 tấm hình hẻm nếu không chọn cụ thể
        var availableHem = [];
        for (var i = 1; i <= 10; i++) {
          var hemUrl = getVal("Hình Hẻm " + i);
          if (hemUrl) availableHem.push(hemUrl);
        }
        for (var i = availableHem.length - 1; i > 0; i--) {
          var j = Math.floor(Math.random() * (i + 1));
          var temp = availableHem[i];
          availableHem[i] = availableHem[j];
          availableHem[j] = temp;
        }
        for (var i = 0; i < Math.min(maxHem, availableHem.length); i++) {
          finalImages.push(availableHem[i]);
        }
      }

      // 3. Tới phần còn lại của Hình Nội thất
      for (var i = 1; i < noithatIndices.length; i++) {
        var imgIdx = parseInt(noithatIndices[i]);
        if (!isNaN(imgIdx) && imgIdx >= 1 && imgIdx <= 15) {
          var imgUrl = getVal("Ảnh " + imgIdx);
          if (imgUrl) finalImages.push(imgUrl);
        }
      }
      
      // Đảm bảo đủ 10 slot ảnh cho Public
      while (finalImages.length < 10) finalImages.push("");
      
      var soNha = getVal("Ngõ/Số nhà");
      var tenDuong = getVal("Đường");
      var tenQuan = getVal("Quận");
      var phuongCu = getVal("Phường cũ (AI)"); // Bây giờ lấy từ cột do người dùng bấm nút AI sinh ra
      
      // Xử lý Cú pháp (Lấy từ Nội dung chính, cắt ngay sau thông tin Quận, trước số tiền tỷ thứ 2)
      var noiDungChinh = getVal("Nội dung chính") ? getVal("Nội dung chính").toString() : "";
      var cuPhap = noiDungChinh;
      // Dùng Regex lấy mọi thứ từ đầu cho đến "Quận [Tên quận]", hỗ trợ toàn bộ quận chữ (Phú Nhuận, Tân Bình...) và quận số
      var matchCuPhap = noiDungChinh.match(/^(.*?Quận\s+[A-Za-zÀ-ỹ0-9\s]+?)\s+[\d\.]+(?:-[\d\.]+)?\s*tỷ/i);
      if (matchCuPhap) {
          cuPhap = matchCuPhap[1].trim();
      }

      // MAPPING VÀO FILE SOURCE THEO ĐÚNG SCHEMA MỚI 39 CỘT
      var publicRowData = [
        "",                          // 0: Hinh_mat_tien (Cột A) - Bỏ trống để ghi formula sau
        cuPhap,                      // 1: Cu_phap (Cột B)
        "",                          // 2: Note (Cột C)
        getVal("Mã Khang Ngô (ID)"), // 3: id (Cột D)
        getVal("Tiêu đề Public"),    // 4: tieu_de (Cột E)
        getVal("DT Thực tế"),        // 5: dien_tich (Cột F)
        getVal("Số Tầng"),           // 6: so_tang (Cột G)
        getVal("Mặt Tiền"),          // 7: mat_tien (Cột H)
        formatGia(getVal("Giá Public")), // 8: gia (Cột I)
        formatQuan(getVal("Quận")),  // 9: quan (Cột J)
        getVal("Phường"),            // 10: phuong (Cột K)
        loaiHinh,                    // 11: loai_hinh (Cột L)
        getVal("Hướng"),             // 12: huong_nha (Cột M)
        getVal("Phân loại Hẻm"),     // 13: duong_truoc_nha (Cột N)
        getVal("Đường trước nhà (m)"), // 14: do_rong_hem (Cột O)
        getVal("Tình trạng nhà"),    // 15: tinh_trang_nha (Cột P)
        getVal("Đánh giá (Admin)"),  // 16: danh_gia (Cột Q)
        getVal("Ngủ trệt (Admin)"),  // 17: ngu_tang_tret (Cột R)
        getVal("CHDV (Admin)"),      // 18: chdv (Cột S)
        getVal("Mô tả Public"),      // 19: mo_ta (Cột T)
        finalImages[0],              // 20: anh_1 (Cột U)
        finalImages[1],              // 21: anh_2 (Cột V)
        finalImages[2],              // 22: anh_3 (Cột W)
        finalImages[3],              // 23: anh_4 (Cột X)
        finalImages[4],              // 24: anh_5 (Cột Y)
        finalImages[5],              // 25: anh_6 (Cột Z)
        finalImages[6],              // 26: anh_7 (Cột AA)
        finalImages[7],              // 27: anh_8 (Cột AB)
        finalImages[8],              // 28: anh_9 (Cột AC)
        finalImages[9],              // 29: anh_10 (Cột AD)
        new Date(),                  // 30: Last updated (Cột AE)
        phuongCu,                    // 31: phuong_cu (Cột AF)
        getVal("Số phòng ngủ"),      // 32: so_pn (Cột AG)
        getVal("Số nhà vệ sinh"),    // 33: so_wc (Cột AH)
        tenDuong,                    // 34: ten_duong (Cột AI)
        "",                          // 35: gio_dang (Cột AJ)
        "",                          // 36: trang_thai (Cột AK)
        getVal("System ID"),         // 37: System ID (Cột AL)
        getVal("Hình Mặt Tiền"),     // 38: Link Hình Mặt Tiền gốc (Cột AM)
        "",                          // 39: Tiêu đề BDS (Cột AN) - Rỗng mặc định để Admin tự biên tập hoặc dùng AI SEO
        false,                       // 40: Đăng BDS (Cột AO) - Checkbox mặc định là false
        finalImages[10] || "",       // 41: Ảnh 11 (Cột AP)
        finalImages[11] || "",       // 42: Ảnh 12 (Cột AQ)
        finalImages[12] || "",       // 43: Ảnh 13 (Cột AR)
        finalImages[13] || "",       // 44: Ảnh 14 (Cột AS)
        finalImages[14] || "",       // 45: Ảnh 15 (Cột AT)
        getVal("JSON_UI") || "",     // 46: JSON_UI (Cột AU)
        getVal("DT Trên sổ"),        // 47: DT Trên sổ (Cột AV)
        (function() {
          var imagesAdminJsonStr = getVal("Images_Admin_JSON") || "";
          var imagesPublicJsonStr = "[]";
          if (imagesAdminJsonStr) {
            try {
              var imagesAdmin = JSON.parse(imagesAdminJsonStr);
              var publicUrls = imagesAdmin
                .filter(function(img) {
                  return img && img.is_hidden !== 1 && ["facade", "diagram", "deleted"].indexOf(img.role) === -1;
                })
                .map(function(img) {
                  return img.r2_url || img.image_url;
                });
              imagesPublicJsonStr = JSON.stringify(publicUrls);
            } catch(e) {
              // fallback
            }
          }
          return imagesPublicJsonStr;
        })()                         // 48: Images_Public_JSON (Cột AW)
      ];
      
      var publicHeaders = [];
      var headerRowIdx = 1; // mặc định dòng 1
      var maxSearchRows = Math.min(10, lastRowPublic);
      for (var r = 1; r <= maxSearchRows; r++) {
        var rowVals = publicSheet.getRange(r, 1, 1, publicSheet.getLastColumn()).getValues()[0];
        if (rowVals.indexOf("System ID") !== -1 || rowVals.indexOf("id") !== -1 || rowVals.indexOf("Cu_phap") !== -1) {
          publicHeaders = rowVals;
          headerRowIdx = r;
          break;
        }
      }
      
      if (publicHeaders.length === 0 && lastRowPublic > 0) {
        publicHeaders = publicSheet.getRange(1, 1, 1, publicSheet.getLastColumn()).getValues()[0];
      }

      var sysIdColIdx = publicHeaders.indexOf("System ID") + 1;
      if (sysIdColIdx === 0) sysIdColIdx = 38; // Fallback cột AL
      
      var startDataRow = headerRowIdx + 1;
      var numDataRows = lastRowPublic - headerRowIdx;
      
      var systemId = getVal("System ID");
      var foundRow = -1;
      
      if (systemId && systemId.toString().trim() !== "" && numDataRows >= 1) {
        var systemIds = publicSheet.getRange(startDataRow, sysIdColIdx, numDataRows, 1).getValues();
        for (var i = 0; i < systemIds.length; i++) {
          if (systemIds[i][0] && systemIds[i][0].toString().trim() === systemId.toString().trim()) {
            foundRow = i + startDataRow;
            break;
          }
        }
      }
      
      if (foundRow > -1) {
        // Kiểm tra xem có yêu cầu Force Overwrite hay không (Admin xóa ngày Last Sync trên Pool)
        var lastSyncVal = lastSyncColIndex > 0 ? sheet.getRange(row, lastSyncColIndex).getValue() : "";
        
        if (lastSyncVal === "" || !lastSyncVal) {
          // --- CHẾ ĐỘ CƯỠNG BỨC ĐỒNG BỘ ĐÈ (FORCE OVERWRITE) ---
          publicSheet.getRange(foundRow, 1, 1, publicRowData.length).setValues([publicRowData]);
        } else {
          // --- CHẾ ĐỘ ĐỒNG BỘ MỘT PHẦN (SMART MERGE) ---
          var existingRowData = publicSheet.getRange(foundRow, 1, 1, publicRowData.length).getValues()[0];
          
          // Danh sách các cột được bảo vệ (index 0-indexed của publicRowData):
          var protectedIndices = [1, 2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 39, 40, 47];
          
          var mergedRowData = [];
          for (var c = 0; c < publicRowData.length; c++) {
            if (protectedIndices.indexOf(c) !== -1) {
              // Cột được bảo vệ: Giữ nguyên nếu ở Source đang có dữ liệu và khác rỗng
              var existVal = existingRowData[c];
              if (existVal !== undefined && existVal !== null && existVal.toString().trim() !== "") {
                mergedRowData.push(existVal);
              } else {
                mergedRowData.push(publicRowData[c]);
              }
            } else {
              // Các cột thô khác: luôn cập nhật mới từ Pool
              mergedRowData.push(publicRowData[c]);
            }
          }
          
          publicSheet.getRange(foundRow, 1, 1, mergedRowData.length).setValues([mergedRowData]);
        }
      } else {
        // --- CHẾ ĐỘ ĐỒNG BỘ LẦN ĐẦU (FIRST SYNC) ---
        var insertRow = lastRowPublic + 1;
        var minDataRow = headerRowIdx + 1;
        if (insertRow < minDataRow) {
          insertRow = minDataRow;
        }
        publicSheet.getRange(insertRow, 1, 1, publicRowData.length).setValues([publicRowData]);
        foundRow = insertRow;
      }
      
      var imgColIdx = publicHeaders.indexOf("Hình_mat_tien") + 1;
      if (imgColIdx === 0) imgColIdx = 1;
      
      var origImgColIdx = publicHeaders.indexOf("Hình Mặt Tiền") + 1;
      if (origImgColIdx === 0) origImgColIdx = 39;
      
      var origImgLetter = getColumnLetter(origImgColIdx);
      publicSheet.getRange(foundRow, imgColIdx).setFormula('=IMAGE(' + origImgLetter + foundRow + ')');
      
      var dangBdsColIdx = publicHeaders.indexOf("Đăng BDS") + 1;
      if (dangBdsColIdx === 0) dangBdsColIdx = 41;
      
      try {
        publicSheet.getRange(foundRow, dangBdsColIdx).insertCheckboxes();
      } catch (e) {}
      
      statusCell.setValue("Đã đồng bộ");
      
      // Update Last Sync on the Pool sheet
      if (lastSyncColIndex > 0) {
        sheet.getRange(row, lastSyncColIndex).setValue(Utilities.formatDate(new Date(), "GMT+7", "dd/MM/yyyy HH:mm:ss"));
      }
      
    } catch (err) {
      statusCell.setValue("Lỗi: " + err.message);
      range.setValue(false);
    }
  }
}

// -----------------------------------------------------
// CÁC HÀM TIỆN ÍCH HỖ TRỢ
// -----------------------------------------------------

function createHeaders(sheet) {
  var headers = [
    "Mã Hàng", "Hình Nhận Diện", "Tỉnh", "Quận", "Phường", "Đường", "Ngõ/Số nhà", "Phân loại",
    "Năm xây dựng", "Nội dung chính", "Mô tả chi tiết", "Giá chào", "Giá chốt",
    "DT Thực tế", "DT Trên sổ", "Số Tầng", "Mặt Tiền", "Hướng", "Tên Chủ Nhà",
    "Điện thoại 1", "Điện thoại 2", "Loại Hợp đồng", "Số ngày ký", "Ngày bắt đầu",
    "Ngày kết thúc", "Người ký", "Trạng thái",
    "Sơ đồ thửa đất 1", "Sơ đồ thửa đất 2",
    "Hình Mặt Tiền",
    "Hình Hẻm 1", "Hình Hẻm 2", "Hình Hẻm 3", "Hình Hẻm 4", "Hình Hẻm 5", 
    "Hình Hẻm 6", "Hình Hẻm 7", "Hình Hẻm 8", "Hình Hẻm 9", "Hình Hẻm 10",
    "Ảnh 1", "Ảnh 2", "Ảnh 3", "Ảnh 4", "Ảnh 5", "Ảnh 6", "Ảnh 7", "Ảnh 8",
    "Ảnh 9", "Ảnh 10", "Ảnh 11", "Ảnh 12", "Ảnh 13", "Ảnh 14", "Ảnh 15",
    "Mã Khang Ngô (ID)", "Tiêu đề Public", "Mô tả Public", "Giá Public", 
    "Phân loại Hẻm", "Đường trước nhà (m)", "Tình trạng nhà", "Ảnh Public (VD: 1,3,5)", "Ảnh Hẻm Public (VD: 1,2)",
    "Số phòng ngủ", "Số nhà vệ sinh", "Phường cũ (AI)",
    "Đánh giá (Admin)", "Ngủ trệt (Admin)", "CHDV (Admin)",
    "Duyệt Public", "Trạng thái Public", "System ID", "Link Gốc",
    "Điện thoại Đầu Chủ", "Tên Đầu Chủ (Hợp đồng)", "Điểm Facebook",
    "Last Crawl", "Last Sync"
  ];
  
  var maxCols = sheet.getMaxColumns();
  if (headers.length > maxCols) {
    sheet.insertColumnsAfter(maxCols, headers.length - maxCols);
  }
  
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
}

// ==========================================
// TÍCH HỢP AI TÌM PHƯỜNG CŨ BẰNG NÚT BẤM (CUSTOM MENU)
// ==========================================

function onOpen() {
  var ui = SpreadsheetApp.getUi();
  
  // Gộp chung tất cả các Menu vào một chỗ để không bị ghi đè bởi file khác
  ui.createMenu('🤖 AI Tools')
      .addItem('Tự động viết Content & tra Phường cũ', 'batchGenerateContentAndWard')
      .addSeparator()
      .addItem('Chỉ đồng bộ Tiêu đề sang Source (hàng loạt)', 'batchSyncTitleToSource')
      .addItem('Đồng bộ System ID sang Source', 'syncSystemIdToSource')
      .addItem('Gen lại Mã Khang Ngô (dòng chọn)', 'batchRegenerateKhangNgoId')
      .addToUi();
}

function syncSystemIdToSource() {
  var poolSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Pool");
  var sourceSpreadsheet = SpreadsheetApp.openById(PUBLIC_FILE_ID);
  var sourceSheet = sourceSpreadsheet.getSheetByName(PUBLIC_TAB_NAME);
  
  if (!poolSheet || !sourceSheet) {
    SpreadsheetApp.getUi().alert("Không tìm thấy sheet Pool hoặc Source (tab: " + PUBLIC_TAB_NAME + ")!");
    return;
  }
  
  var poolData = poolSheet.getDataRange().getValues();
  var poolHeaders = poolData[0];
  
  var idPoolCol = poolHeaders.indexOf("Mã Khang Ngô (ID)");
  var sysIdPoolCol = poolHeaders.indexOf("System ID");
  
  if (idPoolCol === -1 || sysIdPoolCol === -1) {
    SpreadsheetApp.getUi().alert("Lỗi: Không tìm thấy cột 'Mã Khang Ngô (ID)' hoặc 'System ID' trong Pool!");
    return;
  }
  
  // 1. Tạo bản đồ Mapping từ Pool
  var idMap = {};
  for (var i = 1; i < poolData.length; i++) {
    var maKN = poolData[i][idPoolCol];
    var sysId = poolData[i][sysIdPoolCol];
    if (maKN && sysId) {
      idMap[maKN.toString().trim()] = sysId.toString().trim();
    }
  }
  
  var lastRowPublic = sourceSheet.getLastRow();
  
  // Tìm header động trên Source
  var sourceHeaders = [];
  var headerRowIdx = 1;
  var maxSearchRows = Math.min(10, lastRowPublic);
  for (var r = 1; r <= maxSearchRows; r++) {
    var rowVals = sourceSheet.getRange(r, 1, 1, sourceSheet.getLastColumn()).getValues()[0];
    if (rowVals.indexOf("System ID") !== -1 || rowVals.indexOf("id") !== -1 || rowVals.indexOf("Cu_phap") !== -1) {
      sourceHeaders = rowVals;
      headerRowIdx = r;
      break;
    }
  }
  if (sourceHeaders.length === 0) {
    sourceHeaders = sourceSheet.getRange(1, 1, 1, sourceSheet.getLastColumn()).getValues()[0];
  }
  
  var idSourceColIdx = sourceHeaders.indexOf("id") + 1;
  if (idSourceColIdx === 0) idSourceColIdx = 4; // Fallback cột D
  
  var sysIdSourceColIdx = sourceHeaders.indexOf("System ID") + 1;
  if (sysIdSourceColIdx === 0) sysIdSourceColIdx = 38; // Fallback cột AL (38)
  
  var sourceData = sourceSheet.getDataRange().getValues();
  var updateCount = 0;
  
  for (var j = headerRowIdx; j < sourceData.length; j++) {
    var maKNSource = sourceData[j][idSourceColIdx - 1];
    var currentSysIdSource = sourceData[j][sysIdSourceColIdx - 1];
    
    if (maKNSource) {
      maKNSource = maKNSource.toString().trim();
      var matchingSysId = idMap[maKNSource];
      
      // Nếu tìm thấy map và ô System ID bên Source đang trống
      if (matchingSysId && (!currentSysIdSource || currentSysIdSource.toString().trim() === "")) {
        sourceSheet.getRange(j + 1, sysIdSourceColIdx).setValue(matchingSysId);
        updateCount++;
      }
    }
  }
  
  SpreadsheetApp.getUi().alert("✅ Đã quét và đồng bộ thành công " + updateCount + " System ID từ Pool sang Source!");
}

function getColumnLetter(columnNumber) {
  var temp, letter = '';
  while (columnNumber > 0) {
    temp = (columnNumber - 1) % 26;
    letter = String.fromCharCode(65 + temp) + letter;
    columnNumber = (columnNumber - temp - 1) / 26;
  }
  return letter;
}

/**
 * US-030: Chỉ đồng bộ cột "Tiêu đề Public" sang cột "tieu_de" (Cột E) bên Source hàng loạt theo dòng chọn.
 * Giúp Admin cập nhật nhanh tiêu đề chuẩn SEO mới mà không ảnh hưởng tới ảnh, mô tả hay pháp lý.
 */
function batchSyncTitleToSource() {
  var poolSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Pool") || SpreadsheetApp.getActiveSheet();
  var range = poolSheet.getActiveRange();
  var startRow = range.getRow();
  var numRows = range.getNumRows();
  
  if (startRow <= 1) {
    SpreadsheetApp.getUi().alert("Vui lòng bôi đen các dòng dữ liệu (từ dòng 2 trở đi) cần đồng bộ Tiêu đề!");
    return;
  }
  
  if (PUBLIC_FILE_ID === "ĐIỀN_ID_FILE_PUBLIC_CỦA_BẠN_VÀO_ĐÂY" || PUBLIC_FILE_ID.indexOf("xxxxxxxx") !== -1) {
    SpreadsheetApp.getUi().alert("Lỗi: Chưa cấu hình PUBLIC_FILE_ID thực tế!");
    return;
  }
  
  SpreadsheetApp.getActiveSpreadsheet().toast('Đang đồng bộ hàng loạt tiêu đề...', 'Vui lòng đợi', -1);
  
  var headers = poolSheet.getRange(1, 1, 1, poolSheet.getLastColumn()).getValues()[0];
  var sysIdPoolCol = headers.indexOf("System ID");
  var tieuDePoolCol = headers.indexOf("Tiêu đề Public");
  
  if (sysIdPoolCol === -1 || tieuDePoolCol === -1) {
    SpreadsheetApp.getUi().alert("Lỗi: Không tìm thấy cột 'System ID' hoặc 'Tiêu đề Public' trong Pool!");
    return;
  }
  
  var data = poolSheet.getRange(startRow, 1, numRows, poolSheet.getLastColumn()).getValues();
  
  try {
    var sourceSpreadsheet = SpreadsheetApp.openById(PUBLIC_FILE_ID);
    var sourceSheet = sourceSpreadsheet.getSheetByName(PUBLIC_TAB_NAME) || sourceSpreadsheet.getSheets()[0];
    var lastRowPublic = sourceSheet.getLastRow();
    
    if (lastRowPublic < 2) {
      SpreadsheetApp.getUi().alert("File Source hiện tại trống rỗng hoặc không có dữ liệu!");
      return;
    }
    
    // Tìm header động trên Source
    var sourceHeaders = [];
    var headerRowIdx = 1;
    var maxSearchRows = Math.min(10, lastRowPublic);
    for (var r = 1; r <= maxSearchRows; r++) {
      var rowVals = sourceSheet.getRange(r, 1, 1, sourceSheet.getLastColumn()).getValues()[0];
      if (rowVals.indexOf("System ID") !== -1 || rowVals.indexOf("id") !== -1 || rowVals.indexOf("Cu_phap") !== -1) {
        sourceHeaders = rowVals;
        headerRowIdx = r;
        break;
      }
    }
    if (sourceHeaders.length === 0) {
      sourceHeaders = sourceSheet.getRange(1, 1, 1, sourceSheet.getLastColumn()).getValues()[0];
    }
    
    var sysIdSourceColIdx = sourceHeaders.indexOf("System ID") + 1;
    if (sysIdSourceColIdx === 0) sysIdSourceColIdx = 38;
    
    var tieuDeSourceColIdx = sourceHeaders.indexOf("tieu_de") + 1;
    if (tieuDeSourceColIdx === 0) tieuDeSourceColIdx = 5;
    
    var startDataRow = headerRowIdx + 1;
    var numDataRows = lastRowPublic - headerRowIdx;
    
    // Đọc toàn bộ System ID bên Source để tối ưu hóa tốc độ
    var sourceSysIds = [];
    if (numDataRows >= 1) {
      sourceSysIds = sourceSheet.getRange(startDataRow, sysIdSourceColIdx, numDataRows, 1).getValues().map(function(r) {
        return r[0] ? r[0].toString().trim() : "";
      });
    }
    
    var successCount = 0;
    var notFoundCount = 0;
    
    for (var i = 0; i < data.length; i++) {
      var row = data[i];
      var sysId = row[sysIdPoolCol].toString().trim();
      var tieuDeVal = row[tieuDePoolCol].toString().trim();
      
      if (!sysId || !tieuDeVal) continue;
      
      var matchIdx = sourceSysIds.indexOf(sysId);
      if (matchIdx !== -1) {
        var foundRow = matchIdx + startDataRow;
        // Ghi duy nhất cột tieu_de bên Source
        sourceSheet.getRange(foundRow, tieuDeSourceColIdx).setValue(tieuDeVal);
        successCount++;
      } else {
        notFoundCount++;
      }
    }
    
    SpreadsheetApp.getActiveSpreadsheet().toast('Đã hoàn tất đồng bộ tiêu đề!', 'Thành công');
    SpreadsheetApp.getUi().alert("✅ Đã đồng bộ thành công " + successCount + " tiêu đề sang Source!\n" +
                                 (notFoundCount > 0 ? "⚠️ Có " + notFoundCount + " dòng không tìm thấy khớp bên Source (chưa đồng bộ lần nào)." : ""));
                                 
  } catch (err) {
    SpreadsheetApp.getUi().alert("❌ Lỗi xảy ra: " + err.message);
  }
}

function batchRegenerateKhangNgoId() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var range = sheet.getActiveRange();
  var startRow = range.getRow();
  var numRows = range.getNumRows();
  
  if (startRow <= 1) {
    SpreadsheetApp.getUi().alert("Vui lòng bôi đen các dòng dữ liệu (từ dòng 2 trở đi) cần Gen lại mã!");
    return;
  }
  
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var idCol = headers.indexOf("Mã Khang Ngô (ID)");
  var soNhaCol = headers.indexOf("Ngõ/Số nhà");
  var duongCol = headers.indexOf("Đường");
  var quanCol = headers.indexOf("Quận");
  
  if (idCol === -1 || soNhaCol === -1 || duongCol === -1) {
    SpreadsheetApp.getUi().alert("Lỗi: Không tìm đủ các cột cấu thành Mã Khang Ngô.");
    return;
  }
  
  var data = sheet.getRange(startRow, 1, numRows, sheet.getLastColumn()).getValues();
  var count = 0;
  
  for (var i = 0; i < data.length; i++) {
    var soNha = data[i][soNhaCol];
    var duong = data[i][duongCol];
    var quan = data[i][quanCol];
    
    if (soNha && duong && quan) {
      var newId = genIdKhangNgo(soNha, duong, quan);
      sheet.getRange(startRow + i, idCol + 1).setValue(newId);
      count++;
    }
  }
  
  SpreadsheetApp.getUi().alert("✅ Đã Gen lại thành công Mã Khang Ngô mới cho " + count + " dòng!");
}

function genIdKhangNgo(soNha, duong, quan) {
  soNha = (soNha || "").toString().trim();
  // Nếu có 2 số nhà (chứa dấu +), chỉ lấy phần đầu tiên
  if (soNha.includes('+')) {
    soNha = soNha.split('+')[0].trim();
  }
  
  duong = (duong || "").toString().trim();
  quan = (quan || "").toString().trim();
  
  // 1. Mã hóa số nhà (Số -> Chữ in hoa, Ký tự -> thường)
  var digitMap = {
    '1': 'M', '2': 'H', '3': 'B', '4': 'A', '5': 'N',
    '6': 'S', '7': 'Z', '8': 'T', '9': 'C', '0': 'O',
    '/': 'I', '.': 'I'
  };
  var maSoNha = "";
  for (var i = 0; i < soNha.length; i++) {
    var char = soNha[i];
    if (digitMap[char]) {
      maSoNha += digitMap[char];
    } else if (char.match(/[a-zA-Z]/)) {
      maSoNha += char.toLowerCase();
    }
  }
  
  // 2. Normalization: Các tên đường có biến thể đặc biệt
  var normalizedDuong = duong;
  if (normalizedDuong.match(/cách mạng tháng (tám|8)|cmt8/i)) {
    normalizedDuong = "CMTT";
  } else if (normalizedDuong.match(/ba tháng hai|3 tháng 2|3\/2|3\-2/i)) {
    normalizedDuong = "BTH";
  } else if (normalizedDuong.match(/đường số (\d+)/i)) {
    var match = normalizedDuong.match(/đường số (\d+)/i);
    normalizedDuong = "DS" + match[1];
  }
  
  // Viết tắt tên đường (Lấy chữ cái đầu của mỗi từ)
  var abbrDuong = "";
  if (normalizedDuong === "CMTT" || normalizedDuong === "BTH") {
    abbrDuong = normalizedDuong;
  } else if (normalizedDuong.startsWith("DS")) {
    abbrDuong = normalizedDuong;
  } else {
    var words = normalizedDuong.split(/\s+/);
    for (var k = 0; k < words.length; k++) {
      var word = words[k];
      if (word.length > 0) {
        var firstChar = word[0].toUpperCase();
        // Loại bỏ dấu tiếng việt cho ký tự đầu (Đ -> D, Ô -> O) để mã hóa thuần ASCII
        firstChar = firstChar.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/Đ/g, 'D');
        abbrDuong += firstChar;
      }
    }
  }
  
  // 3. Đảo ngược chuỗi viết tắt (Reversed)
  var reversedDuong = abbrDuong.split('').reverse().join('');
  
  // 4. Ghép nối: [Mã Số Nhà] + 'I' + [Tên Đường Viết Tắt Đảo Ngược]
  var combined = maSoNha + "I" + reversedDuong;
  
  // 5. Ciphering: Chèn 'W' vào vị trí thứ 2
  if (combined.length > 1) {
    combined = combined.substring(0, 1) + "W" + combined.substring(1);
  } else {
    combined = combined + "W";
  }
  
  return combined;
}

function generateKhangNgoId(address, street) {
  var addressStr = (address || "").trim();
  var streetStr = (street || "").trim();

  // 1. Mã hóa phần Số Nhà
  var map = { '1':'M', '2':'H', '3':'B', '4':'A', '5':'N', '6':'S', '7':'Z', '8':'T', '9':'C', '0':'O', '/':'I', '.':'I' };
  var p1 = "";
  
  for (var i = 0; i < addressStr.length; i++) {
    var c = addressStr[i];
    if (map[c]) {
      p1 += map[c];
    } else if (/[a-zA-Z]/.test(c)) {
      p1 += c.toLowerCase();
    } else {
      p1 += c;
    }
  }

  // 2. Viết tắt tên đường (bỏ dấu, lấy chữ cái đầu)
  var noTones = removeVietnameseTones(streetStr);
  var words = noTones.split(/\s+/);
  var acronym = "";
  for (var i = 0; i < words.length; i++) {
    if (words[i].length > 0) acronym += words[i][0].toUpperCase();
  }
  var reversedAcronym = acronym.split('').reverse().join('');

  // 3. Ghép số nhà đã mã hóa + "I" + Tên đường đảo ngược
  var finalStr = p1 + "I" + reversedAcronym;

  // 4. Chèn W vào vị trí thứ 2
  if (finalStr.length > 1) {
    finalStr = finalStr.substring(0, 1) + "W" + finalStr.substring(1);
  } else if (finalStr.length === 1) {
    finalStr += "W";
  }
  
  return finalStr;
}

function removeVietnameseTones(str) {
  str = str.replace(/à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ/g, "a");
  str = str.replace(/è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ/g, "e");
  str = str.replace(/ì|í|ị|ỉ|ĩ/g, "i");
  str = str.replace(/ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ/g, "o");
  str = str.replace(/ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ/g, "u");
  str = str.replace(/ỳ|ý|ỵ|ỷ|ỹ/g, "y");
  str = str.replace(/đ/g, "d");
  str = str.replace(/À|Á|Ạ|Ả|Ã|Â|Ầ|Ấ|Ậ|Ẩ|Ẫ|Ă|Ằ|Ắ|Ặ|Ẳ|Ẵ/g, "A");
  str = str.replace(/È|É|Ẹ|Ẻ|Ẽ|Ê|Ề|Ế|Ệ|Ể|Ễ/g, "E");
  str = str.replace(/Ì|Í|Ị|Ỉ|Ĩ/g, "I");
  str = str.replace(/Ò|Ó|Ọ|Ỏ|Õ|Ô|Ồ|Ố|Ộ|Ổ|Ỗ|Ơ|Ờ|Ớ|Ợ|Ở|Ỡ/g, "O");
  str = str.replace(/Ù|Ú|Ụ|Ủ|Ũ|Ư|Ừ|Ứ|Ự|Ử|Ữ/g, "U");
  str = str.replace(/Ỳ|Ý|Ỵ|Ỷ|Ỹ/g, "Y");
  str = str.replace(/Đ/g, "D");
  return str;
}

// ==========================================
// TÍCH HỢP AI OPENAI (TÌM PHƯỜNG CŨ)
// 0. CẤU HÌNH API KEY (Sử dụng chung cho toàn bộ tính năng AI)
var OPENAI_API_KEY = "sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"; // Điền OpenAI API Key của bạn vào đây

// Tự động tối ưu bảo mật: Ưu tiên lấy API Key từ Script Properties (Cài đặt -> Thuộc tính dự án) để tránh lộ key trên Git
if (typeof PropertiesService !== 'undefined') {
  var savedKey = PropertiesService.getScriptProperties().getProperty('OPENAI_API_KEY');
  if (savedKey && savedKey.trim().indexOf('sk-') === 0) {
    OPENAI_API_KEY = savedKey.trim();
  }
}

// -----------------------------------------------------
// KHANG NGÔ AI TOOL - HỆ THỐNG GỌI AI HỢP NHẤT (DRY)
// -----------------------------------------------------

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
    moTaGoc: getIdx("Mô tả chi tiết"), phanLoai: getIdx("Phân loại"),
    dtSo: getIdx("DT Trên sổ"), huong: getIdx("Hướng"),
    noiDungChinh: getIdx("Nội dung chính"),
    phuongCuOut: getIdx("Phường cũ (AI)"), tieuDeOut: getIdx("Tiêu đề Public"), moTaOut: getIdx("Mô tả Public")
  };
  
  if (cols.tieuDeOut === -1 || cols.moTaOut === -1 || cols.phuongCuOut === -1) {
    SpreadsheetApp.getUi().alert("Không tìm thấy đủ các cột: Tiêu đề Public, Mô tả Public, Phường cũ (AI).");
    return;
  }
  
  var dataRange = sheet.getRange(startRow, 1, numRows, sheet.getLastColumn());
  var data = dataRange.getValues();
  var successCount = 0;
  
  // Prompt hệ thống chi tiết tuân thủ nghiêm ngặt US-025, US-026 & US-040.2 (Cải tiến prompt)
  var systemPrompt = "Bạn đóng vai một Chuyên gia môi giới nhà phố 15 năm kinh nghiệm tại trung tâm TP.HCM.\n" +
                     "Nhiệm vụ của bạn là nhận thông tin của 1 căn nhà và sinh ra bài đăng chuyên nghiệp, đồng thời tìm ra 'Phường cũ' của địa chỉ nhà trước khi sáp nhập hành chính (nếu có).\n\n" +
                     "🚨 LUẬT KHÔNG BỊA ĐẶT THÔNG SỐ VẬT LÝ (🚨 BẮT BUỘC - TUYỆT ĐỐI KHÔNG VI PHẠM):\n" +
                     "1. Khoảng cách ra mặt tiền / Độ sâu hẻm: Tuyệt đối KHÔNG tự tiện ghi số mét cụ thể (như 5m, 10m) hoặc số bước chân cụ thể (như 2 bước chân, 5 bước chân) ra mặt tiền nếu dữ liệu gốc không ghi rõ. Thay vào đó, nếu hẻm lớn hoặc xe hơi thông thoáng, sử dụng các cụm từ ước lượng cực kỳ cuốn hút và an toàn của môi giới: 'sát mặt tiền đường lớn', 'vài bước chân ra mặt tiền', 'hẻm sạch sẽ thông thoáng sát đường lớn'.\n" +
                     "2. Chi tiết danh sách nội thất: Tuyệt đối KHÔNG tự tiện liệt kê cụ thể từng thiết bị điện tử, gia dụng (như sofa, máy lạnh, tivi, tủ lạnh side by side, bộ bàn ăn, giường nệm...) nếu dữ liệu gốc không ghi chi tiết. Thay vào đó, hãy dùng các câu bao quát, cao cấp: 'tặng full nội thất cao cấp sang xịn mịn, khách dọn vào ở ngay' hoặc 'nội thất hoàn thiện tinh tế hiện đại'.\n" +
                     "3. Dòng tiền thuê cụ thể: Tuyệt đối KHÔNG tự đoán số tiền thuê phòng hoặc tổng thu nhập cụ thể (như 8 triệu/phòng, thu nhập 30 triệu/tháng). Thay vào đó, hãy định vị tiềm năng khai thác: 'cực kỳ phù hợp làm CHDV cao cấp cho dòng tiền khủng/thu nhập thụ động cực tốt hằng tháng' hoặc 'khu vực nhu cầu thuê cực cao, thích hợp giữ tiền và khai thác dòng tiền ổn định'.\n" +
                     "4. Lô góc / Nở hậu: Tuyệt đối KHÔNG ghi 'lô góc 2 mặt tiền' hoặc tự bịa số mét nở hậu (như nở hậu 7m) trừ khi dữ liệu thô hoặc mô tả chi tiết có nhắc đến chữ 'lô góc', '2 mặt thoáng', 'nở hậu' hoặc 'nở'. Nếu chỉ có chữ 'nở hậu' chung chung mà không ghi số mét cụ thể, chỉ được ghi 'nhà nở hậu tài lộc' hoặc 'sổ nở hậu đẹp', cấm tự bịa ra số mét nở hậu mặt sau.\n" +
                     "5. Pháp lý / Quy hoạch mặc định: Nếu dữ liệu gốc không nhắc gì đến ngân hàng, thế chấp hoặc nợ, bắt buộc sử dụng câu mẫu chuẩn: 'Pháp lý sạch, hoàn công đầy đủ, sổ hồng riêng cất két, sẵn sàng công chứng ngay'. Về quy hoạch: mặc định ghi 'Khu dân cư hiện hữu ổn định, hoàn toàn không quy hoạch lộ giới' nếu tài sản ở khu vực xây dựng đồng bộ trung tâm.\n\n" +
                     "🚨 CÁC QUY TẮC BẮT BUỘC KHI SINH TIÊU ĐỀ PUBLIC (tieuDe):\n" +
                     "1. CẤU TRÚC TIÊU ĐỀ BẮT BUỘC: Tiêu đề phải tuân thủ nghiêm ngặt theo đúng cấu trúc và thứ tự sau:\n" +
                     "   `[Prefix nếu có][Tên đường] - [Diện tích]m2 - [Kích thước] - [Số tầng] tầng - [Giá]T | [Ưu điểm nổi bật]`\n" +
                     "   - [Prefix nếu có] (🚨 TÙY CHỌN - OPTIONAL): Bắt đầu tiêu đề trực tiếp bằng tiền tố được cung cấp ở yêu cầu (đã được tính toán sẵn từ hệ thống).\n" +
                     "   - [Tên đường]: Tên con đường. Hãy LOẠI BỎ các từ 'Đường', 'Đ.' ở đầu tên đường (Ví dụ: `Trần Quang Diệu`).\n" +
                     "   - [Diện tích]m2: Diện tích thực tế viết sát chữ m2 (Ví dụ: `38m2`).\n" +
                     "   - [Kích thước]: Viết dưới dạng `[ngang]x[dài]` viết sát nhau, TUYỆT ĐỐO KHÔNG có dấu ngoặc đơn ở hai đầu (Ví dụ: `9x5` hoặc `4x12.5`). Hãy ĐỌC dòng đầu của 'Nội dung chính gốc' (dạng `[Số nhà] [Tên đường] [Diện tích m2] [Số tầng] [Chiều ngang] [Chiều dài] [Giá]`. Ví dụ: `40.78 trần quang diệu 38 3 9 5 8.75 tỷ` -> chiều ngang là 9m, chiều dài là 5m -> kích thước là `9x5`). 🚨 LƯU Ý QUAN TRỌNG: Ưu tiên hàng đầu là trích xuất trực tiếp chiều ngang và chiều dài nếu chúng xuất hiện rõ ràng kề nhau trong chuỗi thô. TUYỆT ĐỐI KHÔNG tự động tính toán lại dài = Diện tích / Ngang nếu đã có con số kích thước rõ ràng trong chuỗi.\n" +
                     "   - [Số tầng] tầng: Số tầng của nhà (Ví dụ: `3 tầng`).\n" +
                     "   - [Giá]T: Giá viết sát chữ T (chữ T viết hoa, KHÔNG dùng chữ 'Tỷ' hay 'tỷ' hay 't') (Ví dụ: `8.75T` hoặc `13T`).\n" +
                     "   - \" | \" + [Ưu điểm nổi bật]: Dùng ký tự gạch đứng '|' có khoảng trắng hai bên để phân tách phần kỹ thuật và phần ưu điểm. Các ưu điểm siêu ngắn gọn lấy từ tag USP/Mô tả.\n" +
                     "     🚨 QUY TẮC IN HOA & VIẾT TẮT USP (🚨 CỰC KỲ QUAN TRỌNG):\n" +
                     "     + Các từ viết tắt chuyên ngành sau đây được phép viết in hoa toàn bộ: **`HXH`**, **`CHDV`**, **`HĐ`**, **`PN`**, **`CV`** (Ví dụ: `HĐ thuê`, `CHDV dòng tiền`, `3PN`, `gần CV`). Các từ khác quy về định dạng chữ thường, chỉ viết hoa chữ cái đầu tiên của từ đầu tiên ngay sau dấu '| '.\n" +
                     "     + Nếu có số phòng ngủ: Bắt buộc viết tắt dạng `[Số]PN` (Ví dụ: `3PN`, `4PN`, TUYỆT ĐỐI KHÔNG ghi '3 phòng ngủ' hay '3 phòng').\n" +
                     "     + Nếu có công viên: Bắt buộc viết tắt từ công viên thành `CV` (Ví dụ: `CV Lê Văn Tám`, `gần CV`).\n" +
                     "     + TUYỆT ĐỐI KHÔNG đề cập đến 'hợp đồng điện tử' hoặc 'HĐĐT' trong USP.\n" +
                     "     + TUYỆT ĐỐI KHÔNG đề cập đến 'lãi vốn' hoặc 'chính chủ' trong USP.\n" +
                     "     + TUYỆT ĐỐI KHÔNG đề cập đến 'hẻm nhỏ' hoặc 'hẻm ba gác' hoặc 'hẻm' trong USP.\n" +
                     "     + TUYỆT ĐỐI KHÔNG đề cập lại từ 'hẻm', 'hẻm xe hơi' hoặc 'HXH' trong phần USP nếu ở đầu tiêu đề đã có tiền tố 'HXH '.\n" +
                     "     + Có thể đưa vào USP: Số phòng ngủ viết tắt (`3PN`), Chợ (ví dụ: `gần chợ Tân Định`), Công viên viết tắt (`gần CV Lê Văn Tám`), các địa điểm nổi tiếng lân cận (lấy từ mô tả chi tiết gốc).\n" +
                     "     - *Ví dụ Tiêu đề chuẩn (>4m):* `HXH Trần Quang Diệu - 38m2 - 9x5 - 3 tầng - 8.75T | Lô góc 3PN gần chợ`\n" +
                     "     - *Ví dụ Tiêu đề chuẩn (<=4m):* `Lê Văn Sỹ - 46m2 - 4.6x10 - 4 tầng - 12.8T | Nhà mới đẹp gần CV Lê Văn Tám`\n" +
                     "     - *Ví dụ Tiêu đề chuẩn Mặt tiền:* `Mặt tiền Nguyễn Trọng Tuyển - 80m2 - 4x20 - 5 tầng - 22T | CHDV dòng tiền cao`\n" +
                     "2. KHỐNG CHẾ ĐỘ DÀI VÀ TỐI ƯU KHÔNG GIAN: Tiêu đề sinh ra TUYỆT ĐỐI không vượt quá 99 ký tự tổng cộng. Đặc biệt, phần kỹ thuật từ đầu tiêu đề đến hết chữ \"T\" của giá (bao gồm cả chữ \"T\") TUYỆT ĐỐI không quá 65 ký tự. Nếu còn trống nhiều ký tự sau chữ \"T\" (đến giới hạn 99 ký tự), hãy chắt lọc các điểm nổi bật để chèn vào sau dấu '|'. Ngược lại, nếu gần hết chỗ, hãy cô đọng phần 'Ưu điểm nổi bật' hoặc cắt bớt để không bị quá 99 ký tự.\n\n" +
                     "🚨 CÁC QUY TẮC BẮT BUỘC KHI SINH MÔ TẢ PUBLIC (moTa):\n" +
                     "Mô tả Public phải có cấu trúc nghệ thuật chuyên nghiệp, bắt đầu bằng một dòng Tiêu đề thu hút viết IN HOA TOÀN BỘ để tạo điểm nhấn mạnh mẽ khi khách hàng mở xem chi tiết căn nhà:\n\n" +
                     "1. DÒNG ĐẦU TIÊN (TIÊU ĐỀ THU HÚT - CATCHY BANNER):\n" +
                     "   - Viết IN HOA TOÀN BỘ (UPPERCASE) và bắt đầu bằng emoji còi hú `🚨 `.\n" +
                     "   - Cấu trúc: `🚨 [Cụm từ giật tít/Phân loại in hoa] [Tên đường in hoa] [Tên quận in hoa] - [Các ưu điểm nổi bật in hoa] - DT [Diện tích]M² [Kích thước in hoa] [Thông số phụ nếu có] - CHỈ [Giá nguyên].[Ký hiệu lẻ] TỶ.`\n" +
                     "   - Giải thích chi tiết các thành phần của Banner:\n" +
                     "     + [Cụm từ giật tít/Phân loại in hoa]: Tự sinh cụm từ giật tít mạnh mẽ (Ví dụ: `SIÊU VỊ TRÍ`, `BIỆT THỰ MINI`, `HẺM THÔNG`, `SIÊU PHẨM`, `KHU VIP`, `MẶT TIỀN`, `CẶP SONG SINH 2 CĂN`).\n" +
                     "     + [Tên đường in hoa] [Tên quận in hoa]: Lược bỏ từ 'Đường', 'Đ.' (Ví dụ: `PHAN ĐÌNH PHÙNG PHÚ NHUẬN` hoặc `ĐƯỜNG 3 THÁNG 2 QUẬN 10` - chú ý chữ 'Đường' trong các đường số hoặc đường đặc biệt vẫn giữ).\n" +
                     "     + [Các ưu điểm nổi bật in hoa]: Nêu 2-3 ưu điểm nổi bật nhất lấy từ mô tả chi tiết, phân cách bằng dấu ` - `. Các từ viết tắt chuyên ngành bắt buộc viết in hoa: **`HXH`**, **`CHDV`**, **`HĐ`**, **`PN`**, **`CV`**, **`BTCT`** (Ví dụ: `HĐ THUÊ`, `CHDV DÒNG TIỀN`, `4PN 5WC`, `BTCT`, `HXH VF3`). Được phép dùng emoji ngôi sao `⭐` khi mô tả chất lượng phòng VIP (Ví dụ: `4PN MASTER 5⭐`).\n" +
                     "     + DT [Diện tích]M² [Kích thước in hoa] [Thông số phụ nếu có]: Viết dạng `DT [Diện tích]M² ([Ngang]x[Dài])` viết sát nhau. Có thể ghi thêm đặc trưng nở hậu/xây full nếu dữ liệu gốc xác nhận rõ ràng (Ví dụ: `(4x8) NỞ HẬU`, `(4.8x6.5)`, `6x7.5 XÂY FULL`).\n" +
                     "       *Lưu ý Diện tích sử dụng (`SD [Sàn]M²`):* Nếu diện tích đất nhỏ (dưới 25m2) nhưng nhiều tầng, hãy tính diện tích sử dụng `SD = diện tích * số tầng` và bổ sung vào tiêu đề để tối ưu sức hút (Ví dụ: `SD 39M²` hoặc `SD 121M²`).\n" +
                     "     + CHỈ [Giá nguyên].[Ký hiệu lẻ] TỶ.: Làm tròn xuống phần nguyên của giá và định vị ký hiệu lẻ `.x` hoặc `.xx` theo số chữ số thập phân của giá chào để tạo sự tò mò (Ví dụ: 7.5 tỷ hoặc 8.15 tỷ -> `CHỈ 7.x TỶ.`, nhưng 8.66 tỷ -> `CHỈ 8.xx TỶ.`).\n" +
                     "   - Banner phải kết thúc bằng dấu chấm `.` và có thể kèm một emoji nhỏ xinh ở cuối nếu thích hợp (Ví dụ: `🚨 SIÊU PHẨM PHAN XÍCH LONG PHÚ NHUẬN - ... - CHỈ 8.xx TỶ 🌸`).\n\n" +
                     "2. DÒNG THỨ 2: Để trống hoàn toàn 1 dòng.\n\n" +
                     "3. DÒNG THỨ 3: Ghi chính xác chữ `Mô tả:`.\n\n" +
                     "4. CÁC DÒNG TIẾP THEO (DANH SÁCH CHI TIẾT):\n" +
                     "   - Viết thành một danh sách gồm từ 6 đến 10 dòng/đoạn ngắn, mỗi đoạn bắt đầu bằng ký tự `+ ` (dấu cộng và khoảng trắng), cách nhau bởi đúng 1 dòng trống.\n" +
                     "   - HẠN CHẾ EMOJI TỐI ĐA: TUYỆT ĐỐI không dùng emoji (icon) tràn lan, chỉ được sử dụng tối thiểu trong trường hợp đặc biệt như ký hiệu 5-sao `5⭐` khi mô tả căn phòng đẳng cấp, còn lại giữ văn phong chữ viết truyền thống sạch sẽ.\n" +
                     "   - Các dòng/đoạn cần bao trùm đầy đủ các thông tin hấp dẫn sau (sử dụng văn phong chuyên gia, giàu sức thuyết phục):\n" +
                     "     + + Vị trí: Mô tả vị trí đắc địa thực tế, sầm uất, kết nối cực nhanh sang các quận trung tâm (Q1, Bình Thạnh...) hoặc sân bay qua các trục đường lớn cụ thể (nêu tên cụ thể như Võ Thị Sáu, CMT8, Điện Biên Phủ, Phan Đăng Lưu, Hai Bà Trưng...), gần các landmark quan trọng (bệnh viện Hoàn Mỹ, công viên Lê Văn Tám...). Tuyệt đối KHÔNG ghi số nhà thật. 🚨 RẤT QUAN TRỌNG: Nếu nhà trong hẻm (loai_hinh = Hẻm), tuyệt đối KHÔNG ghi 'Mặt tiền [Tên đường]' ở vị trí. Thay vào đó, dùng các cụm từ như 'Ngay khu [Tên đường]', 'Ngay trung tâm [Tên đường]', hoặc 'Sát mặt tiền [Tên đường]'. Chỉ ghi 'Mặt tiền [Tên đường]' nếu loai_hinh thực tế là 'Mặt tiền'.\n" +
                     "     + + Đặc điểm hẻm/đường: Nêu rõ độ rộng hẻm thực tế từ thông số thô (ví dụ: hẻm rộng 4m, hẻm xe hơi rộng rãi) và khẳng định hẻm thông thoáng sạch sẽ, ô tô đỗ cửa đỗ bên ngoài. TUYỆT ĐỐI cấm bịa đặt số mét hoặc số bước chân cụ thể ra mặt tiền đường chính (chỉ dùng ước lượng 'sát mặt tiền', 'vài bước chân ra mặt tiền đường lớn').\n" +
                     "     + + Khu dân cư/Môi trường sống: Dân trí cao, an ninh, yên tĩnh, hàng xóm hiền lành, thân thiện, khu vực thích hợp mua ở thực.\n" +
                     "     + + Kết cấu: Nêu chi tiết kết cấu kiên cố (BTCT vững chắc, đúc kiên cố). BẮT BUỘC dịch chuẩn số tầng sang định dạng miền Nam: 2 tầng ➡️ 'Trệt, lầu đúc kiên cố'; 3 tầng ➡️ 'Trệt, 2 lầu BTCT'; 4 tầng ➡️ 'Trệt, 3 lầu BTCT'; 5 tầng ➡️ 'Trệt, 4 lầu BTCT'. Nêu chi tiết số phòng ngủ (PN) khép kín (kèm 5⭐ nếu có phòng master đẳng cấp), số WC, phòng khách rộng rãi, bếp mở thông thoáng, ban công bao quanh lấy gió trời và ánh sáng tự nhiên.\n" +
                     "     + + Ưu điểm/Nội thất (nếu có): Nếu dữ liệu thô có nhắc đến nội thất, ghi chung chung nhưng cao cấp: 'Tặng full nội thất cao cấp sang xịn mịn, thiết kế đồng bộ hiện đại, khách mua chỉ việc xách vali vào ở ngay'. Nếu nhà ở vị trí góc, ghi 'Ưu điểm lô góc cực kỳ thoáng đãng đón gió mát tự nhiên cả ngày'. Tuyệt đối không tự bịa danh sách thiết bị gia dụng chi tiết.\n" +
                     "     + + Diện tích: Nêu diện tích thực tế công nhận trên sổ `DT [Diện tích]m² ([Ngang]x[Dài])`, nở hậu tài lộc (nếu dữ liệu thô xác nhận rõ có nở hậu, tuyệt đối không bịa số mét nở cụ thể), diện tích sàn/sử dụng nếu có.\n" +
                     "     + + Mục đích phù hợp/Lợi thế khai thác: Phù hợp khách mua ở thực hoặc khai thác căn hộ dịch vụ (CHDV) cho dòng tiền ổn định cực tốt hằng tháng. Tuyệt đối không bịa đặt số tiền thuê phòng hoặc tổng thu nhập cụ thể.\n" +
                     "     + + Quy hoạch: Khẳng định thuộc khu dân cư hiện hữu ổn định, hoàn toàn không quy hoạch, không lộ giới.\n" +
                     "     + + Pháp lý: Thực hiện đối chiếu nghiêm ngặt theo đúng thực tế: Mặc định (nếu thông tin gốc KHÔNG nhắc gì đến thế chấp/vay/ngân hàng) thì bắt buộc ghi 'Pháp lý sạch, hoàn công đầy đủ, sổ hồng riêng cất két, sẵn sàng công chứng ngay'. Chỉ khi thông tin gốc ghi rõ đang thế chấp/gửi ngân hàng thì tuyệt đối KHÔNG ghi 'sổ cất két' hay 'công chứng ngay' mà phải ghi đúng thực tế (Ví dụ: 'Sổ hồng gửi ngân hàng cực kỳ an toàn, sẵn sàng giải chấp công chứng nhanh').\n" +
                     "     + + Giá: Dòng cuối cùng BẮT BUỘC là thông tin giá: `+ Giá: [Giá trị] tỷ [bớt lộc / thương lượng].` (ví dụ: `+ Giá: 8.66 tỷ.`).\n\n" +
                     "🚨 TRÁNH LẶP TỪ VÀ THỪA THÔNG TIN: Đảm bảo các bullet points bổ trợ lẫn nhau và không lặp lại cùng một thông tin kỹ thuật (Ví dụ: Nếu ở mục 'Pháp lý' đã ghi 'hoàn công đầy đủ' thì ở mục 'Ưu điểm' không ghi lại nữa để bài viết cô đọng, sắc sảo).\n\n" +
                     "🚨 CÁC QUY TẮC PHƯỜNG CŨ:\n" +
                     "Suy luận tên Phường gốc của căn nhà dựa vào tên đường, địa chỉ trước đợt sáp nhập hành chính. Trả về trống nếu không đổi hoặc không chắc chắn.\n\n" +
                     "TRẢ VỀ ĐÚNG FORMAT JSON DƯỚI ĐÂY, KHÔNG ĐƯỢC CHỨA BẤT KỲ VĂN BẢN NÀO KHÁC BÊN NGOÀI:\n" +
                     "{\n" +
                     "  \"tieuDe\": \"Nội dung tiêu đề\",\n" +
                     "  \"moTa\": \"Nội dung mô tả\",\n" +
                     "  \"phuongCu\": \"Tên phường cũ\"\n" +
                     "}";
  
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
    
    // Xác định Tiền tố (Prefix) theo Luật mới của người dùng (Mặt tiền / HXH / rỗng)
    var soNhaRaw = (rowData[cols.soNha] || "").toString().trim();
    var rongHemRaw = (rowData[cols.rongHem] || "").toString().trim();
    var widthVal = parseFloat(rongHemRaw);
    var loaiHem = (rowData[cols.hem] || "").toString().toLowerCase().trim();
    
    var isMatTien = false;
    if (soNhaRaw !== "") {
      if (!soNhaRaw.includes(".")) {
        isMatTien = true;
      }
    } else if (loaiHem.includes("mặt tiền") || loaiHem.includes("mặt phố")) {
      isMatTien = true;
    }
    
    var tienTo = "";
    if (isMatTien) {
      tienTo = "Mặt tiền ";
    } else if (!isNaN(widthVal) && widthVal >= 4.0) {
      tienTo = "HXH ";
    }
    
    var userPrompt = "THÔNG TIN CĂN NHÀ:\n" +
      "- Địa chỉ: " + (rowData[cols.soNha]||"") + " " + (rowData[cols.duong]||"") + ", Phường " + (rowData[cols.phuong]||"") + ", Quận " + (rowData[cols.quan]||"") + "\n" +
      "- Nội dung chính gốc (chứa kích thước ở đầu): " + (rowData[cols.noiDungChinh]||"") + "\n" +
      "- DT Thực tế: " + (rowData[cols.dt]||"") + "m2 | DT Trên sổ: " + (rowData[cols.dtSo]||"") + "m2\n" +
      "- Chiều ngang (mặt tiền): " + (rowData[cols.ngang]||"") + "m\n" +
      "- Hướng: " + (rowData[cols.huong]||"") + "\n" +
      "- Kết cấu: " + (rowData[cols.tang]||"") + " tầng, " + (rowData[cols.phongNgu]||"") + " PN, " + (rowData[cols.wc]||"") + " WC\n" +
      "- Hẻm: " + (rowData[cols.hem]||"") + " (Rộng: " + (rowData[cols.rongHem]||"") + "m)\n" +
      "- Giá: " + giaFormat + "\n" +
      "- Phân loại / Tag USP: " + (rowData[cols.phanLoai]||"") + "\n" +
      "- Điểm nổi bật của căn nhà (nguồn USP chính): " + (rowData[cols.moTaGoc]||"") + "\n\n" +
      "LƯU Ý QUAN TRỌNG: Đọc kỹ 'Nội dung chính gốc', 'Phân loại / Tag USP' và 'Điểm nổi bật' — bắt buộc phản ánh các thông số kỹ thuật và ưu điểm vào Tiêu đề và Mô tả. BẮT BUỘC bắt đầu phần tiêu đề trực tiếp bằng tiền tố '" + tienTo + "' kết hợp liền mạch với Tên đường (TUYỆT ĐỐI không chèn thêm bất kỳ dấu gạch ngang, dấu chấm hay ký tự đặc biệt nào giữa tiền tố này và tên đường, Ví dụ: " + (tienTo ? "'" + tienTo + "Trần Quang Diệu - ...'" : "'Trần Quang Diệu - ...'") + ").";
      
    var resultObj = callOpenAI_Unified(systemPrompt, userPrompt);
    
    if (resultObj) {
      if (resultObj.tieuDe && !rowData[cols.tieuDeOut]) {
        // Áp dụng bộ lọc Auto-Trimmer JS khống chế nghiêm ngặt độ dài tối đa 99 ký tự
        var cleanTitle = trimTieuDeBds(resultObj.tieuDe);
        sheet.getRange(startRow + i, cols.tieuDeOut + 1).setValue(cleanTitle);
      }
      if (resultObj.moTa && !rowData[cols.moTaOut]) sheet.getRange(startRow + i, cols.moTaOut + 1).setValue(resultObj.moTa);
      if (resultObj.phuongCu && !rowData[cols.phuongCuOut]) sheet.getRange(startRow + i, cols.phuongCuOut + 1).setValue(resultObj.phuongCu);
      successCount++;
    }
  }
  SpreadsheetApp.getUi().alert("✅ Đã xử lý xong Content AI & Phường cũ cho " + successCount + " dòng!");
}

/**
 * Bộ lọc Auto-Trimmer JS khống chế nghiêm ngặt độ dài tối đa 99 ký tự (US-026)
 * Giữ nguyên phần thông số kỹ thuật đến hết giá trị "T" (<= 65 ký tự) và cắt tỉa phần đuôi.
 * Đồng thời tích hợp Scrubber lập trình tự động loại bỏ hẻm/xe hơi khỏi USP nếu đầu là HXH.
 */
function trimTieuDeBds(tieuDe) {
  if (!tieuDe) return "";
  tieuDe = tieuDe.trim();
  
  var idxBar = tieuDe.indexOf(" | ");
  
  // A. BỘ LỌC PROGRAMMATIC SCRUBBER CHỐNG LẶP HẺM/XE HƠI KHI ĐẦU ĐÃ CÓ TIỀN TỐ HXH
  if (tieuDe.startsWith("HXH ") && idxBar !== -1) {
    var techPart = tieuDe.substring(0, idxBar);
    var uspPart = tieuDe.substring(idxBar + 3).trim();
    
    var cleanUsp = uspPart
      .replace(/hẻm\s+xe\s+hơi/ig, "")
      .replace(/hẻm\s+ô\s+tô/ig, "")
      .replace(/hẻm/ig, "")
      .replace(/ô\s+tô/ig, "")
      .replace(/xe\s+hơi/ig, "")
      .replace(/oto/ig, "")
      .replace(/đỗ\s+cửa/ig, "")
      .replace(/đỗ/ig, "")
      .replace(/đậu/ig, "")
      .replace(/\s+/g, " ")
      .trim();
      
    if (cleanUsp.toLowerCase().startsWith("sát ")) {
      cleanUsp = "Sát " + cleanUsp.substring(4);
    }
    
    if (cleanUsp === "") {
      tieuDe = techPart;
      idxBar = -1;
    } else {
      cleanUsp = cleanUsp.charAt(0).toUpperCase() + cleanUsp.slice(1);
      tieuDe = techPart + " | " + cleanUsp;
      idxBar = tieuDe.indexOf(" | ");
    }
  }

  // 1. Tự động viết hoa chữ cái đầu tiên sau dấu " | "
  if (idxBar !== -1) {
    var techPart = tieuDe.substring(0, idxBar);
    var uspPart = tieuDe.substring(idxBar + 3).trim();
    if (uspPart.length > 0) {
      uspPart = uspPart.charAt(0).toUpperCase() + uspPart.slice(1);
    }
    tieuDe = techPart + " | " + uspPart;
  }

  // 2. Cắt tỉa nếu vượt quá 99 ký tự
  if (tieuDe.length <= 99) {
    return tieuDe;
  }
  
  if (idxBar !== -1) {
    var techPart = tieuDe.substring(0, idxBar);
    var uspPart = tieuDe.substring(idxBar + 3).trim();
    if (uspPart.length > 0) {
      uspPart = uspPart.charAt(0).toUpperCase() + uspPart.slice(1);
    }
    
    if (techPart.length + 3 <= 65) {
      var allowedUspLen = 99 - (techPart.length + 3);
      tieuDe = techPart + " | " + uspPart.substring(0, allowedUspLen).trim();
    } else {
      tieuDe = tieuDe.substring(0, 99).trim();
    }
  } else {
    tieuDe = tieuDe.substring(0, 99).trim();
  }
  return tieuDe;
}

