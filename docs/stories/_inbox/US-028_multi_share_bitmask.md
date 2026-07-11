---
id: US-028
status: accepted
date: 2026-05-25
size: S
---

# US-028: Đồng bộ cơ chế nén Bitmask gửi khách nhiều căn

## User story
**As an** Admin
**I want** khi tôi chọn nhiều căn để tạo link gửi khách, URL được sinh ra sử dụng cơ chế nén Bitmask siêu ngắn
**So that** link gọn gàng, chuyên nghiệp và tuyệt đối không bị Zalo/Messenger cắt ngắn làm lỗi trang.

## Acceptance
- [x] Khi chọn nhiều căn (> 1 căn) để tạo link gửi khách qua Form Modal, URL được tạo theo định dạng `?b=<bitmask_string>&c=<encoded_cust_name>`.
- [x] URL được nén siêu ngắn giống như cơ chế nén Bitmask trên máy tính, giải quyết triệt để vấn đề URL dài hàng trăm ký tự do nối chuỗi ID.

## Solution

> [!note]- Input
> - Danh sách các ID căn nhà được chọn trong `SELECTED_IDS`.
> - Tên khách hàng `linkCustName` và ghi chú `linkCustNote`.

> [!note]- Output / Format
> - URL chia sẻ siêu gọn: `https://khangngonhapho.vercel.app/?b=A7g&c=QW5oIEjDuW5n` (độ dài chỉ khoảng 60-80 ký tự tổng cộng thay vì hàng trăm ký tự).

> [!note]- Key logic
> - **Thuật toán nén Bitmask nhị phân:**
>   - Tạo một chuỗi bit nhị phân `'1'` hoặc `'0'` tương ứng với trạng thái được chọn của từng căn nhà trong danh sách `allIds`.
>   - Đệm thêm các ký tự `'0'` ở cuối để chuỗi bit có độ dài chia hết cho 6.
>   - Cứ mỗi 6 bit nhị phân được chuyển thành một ký tự Base64 URL-safe (bảng chữ cái `B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'`).
> - **Giải mã Bitmask phía client:**
>   - Khi khách truy cập có tham số `?b=...`, trình duyệt tự động giải mã chuỗi Base64 ngược thành chuỗi bit nhị phân và đối chiếu vị trí `'1'` để phục hồi danh sách `sharedIds` đã chọn.

## Verification Plan

> [!check]- Manual Verification
> 1. Chọn khoảng 15-20 căn nhà trên giao diện Admin.
> 2. Bấm tạo link gửi khách $\rightarrow$ Điền tên khách hàng $\rightarrow$ Tạo link.
> 3. Xác nhận URL được sinh ra cực kỳ ngắn gọn (không quá 80 ký tự tổng cộng).
> 4. Mở thử link này ở trình duyệt khác $\rightarrow$ Xác nhận hiển thị đúng 15-20 căn nhà đã chọn cùng dòng chữ chào mừng khách hàng.

## Files touched
- `index.html` — [Frontend Share Logic]
