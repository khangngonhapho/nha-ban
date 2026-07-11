---
id: US-079
status: accepted
date: 2026-06-08
size: S
---

# US-079: Tích hợp nút Tải toàn bộ hình ảnh căn nhà cho Admin để đăng quảng cáo

## User story
**As an** Admin / Broker Khang Ngô
**I want** 1 nút "Tải toàn bộ ảnh" trong giao diện Curation/Chi tiết của Admin để tải toàn bộ hình ảnh thực tế của căn nhà (loại trừ các ảnh sơ đồ thửa đất / sổ đỏ nhạy cảm) về máy dưới dạng các file ảnh riêng lẻ (không nén ZIP để dùng trên điện thoại dễ dàng).
**So that** tôi có thể dễ dàng tải và đăng hình ảnh lên các kênh quảng cáo, truyền thông của căn nhà đang xem chi tiết mà không cần phải lưu thủ công từng ảnh một và không phải giải nén phức tạp trên thiết bị di động.

## Acceptance
- [x] **Vị trí hiển thị rõ ràng:** Bổ sung nút "📥 Tải toàn bộ ảnh" màu xanh lá bên cạnh nút "Copy link nhanh" trong thanh công cụ Admin của chi tiết căn nhà (`index.html`).
- [x] **Bổ sung vào Speed Dial:** Thêm nút tải ảnh `📥` vào danh sách Speed Dial hành động chi tiết (`renderSpeedDialActions('detail', p)`).
- [x] **Thu thập ảnh chính xác:** Thu thập đầy đủ ảnh mặt tiền (`p.img_mat_tien`) và các ảnh trong `p.imgs` của căn nhà.
- [x] **Loại trừ ảnh sơ đồ pháp lý nhạy cảm:** Bắt buộc loại trừ toàn bộ ảnh sơ đồ thửa đất, ảnh sổ đỏ (sử dụng hàm `window.isListingSodoUrl` để lọc) để đảm bảo không bị lộ thông tin pháp lý nhạy cảm lên các kênh quảng cáo.
- [x] **Không sử dụng nén ZIP:** Tải trực tiếp các tệp tin hình ảnh riêng lẻ thay vì file ZIP để hỗ trợ tốt nhất cho điện thoại (vốn rất khó giải nén).
- [x] **Đặt tên file ảnh khoa học:** Các file ảnh được đặt tên có dạng `[SystemID]-[Index].[ext]` (ví dụ: `SYS-20260608-001-1.jpg`, `SYS-20260608-001-2.jpg`) giúp dễ dàng gom nhóm hình theo căn.
- [x] **Xử lý lỗi & Trạng thái tải:** Hiển thị trạng thái chờ `⏳ Đang tải [STT]/[Tổng]...` trên nút bấm khi đang xử lý tuần tự (có delay 250ms để tránh trình duyệt chặn) và khôi phục trạng thái ban đầu sau khi hoàn thành. Nếu lỗi, hiển thị Toast cảnh báo và tự động mở các ảnh trong tab mới làm phương án fallback.
- [x] **Ghi nhận Tracking:** Ghi log tracking hành động "Tải trọn bộ ảnh" gửi về server tracking để theo dõi.

## Solution

### 1. Nguồn dữ liệu hình ảnh cần tải
Để phục vụ đăng tin quảng cáo, danh sách hình ảnh bao gồm:
- Ảnh mặt tiền (Facade Image): `p.img_mat_tien` hoặc `p.pool_row_data[29]` (đưa lên làm ảnh số 1)
- Các ảnh chi tiết (Interior/Exterior/Alley): `p.imgs`
- **Loại trừ tuyệt đối:** Các ảnh mà `window.isListingSodoUrl(url, p)` trả về `true` (bao gồm ảnh Sơ đồ thửa đất 1-5).
- **Deduplicate:** Loại bỏ các URL trùng lặp (ví dụ: ảnh mặt tiền thường trùng trong `p.imgs`).

### 2. Tải ảnh riêng lẻ không dùng ZIP
Để tối ưu hóa trải nghiệm trên điện thoại, hệ thống tải trực tiếp các tệp tin hình ảnh riêng lẻ sử dụng `fetch` -> `Blob` -> `URL.createObjectURL` -> click thẻ `<a>` ảo.
Để tránh trình duyệt chặn tải hàng loạt (multiple downloads restriction), các ảnh được tải tuần tự với khoảng trễ `250ms` giữa mỗi ảnh:
```javascript
async function downloadSingleImage(url, fileName) {
  try {
    const cleanUrl = url.includes('res.cloudinary.com') ? url : fixImgUrl(url, 'w2000');
    const response = await fetch(cleanUrl);
    if (!response.ok) throw new Error(`HTTP status ${response.status}`);
    const blob = await response.blob();
    // Lấy extension phù hợp
    let ext = 'jpg';
    const urlLower = cleanUrl.toLowerCase();
    if (urlLower.includes('.png')) ext = 'png';
    else if (urlLower.includes('.webp')) ext = 'webp';
    
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = `${fileName}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
  } catch (err) {
    // Fallback: Mở tab mới
    window.open(url, '_blank');
  }
}
```

## 📋 Implementation Plan
- **Logic tải tuần tự**: Viết hàm helper `downloadSingleImage` và `downloadAllListingImages` thực hiện tải ảnh tuần tự kèm delay `250ms`, đặt tên file dạng `[SystemID]-[i + 1]`.
- **Tích hợp giao diện Admin**: 
  - Thêm nút "📥 Tải toàn bộ ảnh" vào thanh `.admin-quick-link-bar` trong `openS` (cho cả listing từ Source và Pool thô).
  - Thêm nút vào Speed Dial chi tiết `renderSpeedDialActions('detail', p)`.
- **Đồng bộ hóa & Test**: Kiểm thử tải ảnh riêng lẻ trên PC và thiết bị di động, đảm bảo không bị chặn và loại trừ hoàn toàn ảnh sổ đỏ/sơ đồ.

## 📝 Task Checklist (TODO)
- [x] **Thiết kế & Khảo sát:**
  - [x] Khảo sát code chi tiết của Admin View (`openS`) và Speed Dial
  - [x] Chốt giải pháp tải ảnh blob tuần tự (không tải ảnh sổ đỏ)
- [x] **Triển khai Code:**
  - [x] Viết hàm `downloadAllListingImages` và `downloadSingleImage` tải ảnh dạng riêng lẻ trong `index.html`
  - [x] Tích hợp nút bấm vào thanh `.admin-quick-link-bar` trong `openS`
  - [x] Thêm nút vào `renderSpeedDialActions` cho detail mode
  - [x] Điều chỉnh delay `250ms` để chống bị chặn tải hàng loạt
- [x] **Kiểm thử sơ bộ:**
  - [x] Test tải ảnh riêng lẻ trên các căn nhà có ảnh Cloudinary, Google Drive
  - [x] Kiểm tra loại trừ ảnh sơ đồ pháp lý nhạy cảm (Sổ đỏ 1-5)
  - [x] Kiểm tra lỗi CORS & Fallback mở tab mới
  - [x] Đóng gói và cập nhật INDEX.md

## 🛠️ Update Logic (Drafting while Doing)
### 1. Nhật lý Debug & Phát kiến ngoài kế hoạch (Debug & Discoveries Log)
- *Sự cố kỹ thuật & Cách khắc phục:*
  - Ban đầu tích hợp ZIP qua JSZip nhưng người dùng báo khó giải nén trên điện thoại di động.
  - Chuyển sang tải ảnh riêng lẻ, đặt tên dạng `[SystemID]-[Index]`. 
  - Khi tải nhiều ảnh đồng thời, trình duyệt (đặc biệt là Safari/Chrome trên điện thoại) chặn tải hàng loạt. Khắc phục bằng cách tải tuần tự có delay `250ms` giúp trình duyệt tải trơn tru.

## 🧠 Retro, Lessons Learned & Good Practices (Bảo tồn vĩnh viễn)
### 1. Thực tiễn tốt đúc kết (Good Practices)
- **Tải tuần tự có delay:** Khi viết các script frontend kích hoạt tải nhiều tệp tin, luôn dùng `await new Promise(r => setTimeout(r, delay))` giữa các lượt để tránh trigger cơ chế chặn của trình duyệt.
- **Duy nhất ảnh thực tế:** Ảnh mặt tiền (facade) và ảnh nội thất được gom chung và loại trừ trùng lặp, đảm bảo không có ảnh sổ đỏ nhạy cảm bị tải xuống công khai.

## Verification Plan

### Automated Tests
- None.

### Manual Verification
- **Bước 1**: Đăng nhập Admin (`?pwd=trang`).
- **Bước 2**: Click chọn xem chi tiết một căn nhà.
- **Bước 3**: Tìm nút "📥 Tải toàn bộ ảnh" cạnh nút "Copy link nhanh" hoặc bấm nút gear ở góc dưới để mở Speed Dial và chọn nút `📥`.
- **Bước 4**: Click nút, kiểm tra nhãn nút đổi sang trạng thái loading, kiểm tra các file ảnh được tải xuống lần lượt thành công.
- **Bước 5**: Kiểm tra tên các file ảnh:
  - Tên file có dạng `[SystemID]-[STT].[ext]` (VD: `SYS-20260608-001-1.jpg`).
  - Không chứa bất kỳ ảnh sổ đỏ/sơ đồ thửa đất nào.
  - Ảnh mặt tiền được đưa lên đầu tiên (file `-1`), sau đó đến các ảnh nội thất khác.

## Files touched
- `index.html` — Bổ sung nút bấm chi tiết, nút Speed Dial và hàm xử lý tải tuần tự ảnh riêng lẻ.

## 🔄 Change Requests (Yêu cầu Thay đổi)
- None.
