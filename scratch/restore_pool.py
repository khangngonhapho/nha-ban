with open('pool_backend_v3.gs', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Restore onOpen
old_on_open = """function onOpen() {
  var ui = SpreadsheetApp.getUi();
  
  // Gộp chung tất cả các Menu vào một chỗ để không bị ghi đè bởi file khác
  ui.createMenu('🤖 AI Tools')
      .addItem('Tự động viết Content & tra Phường cũ', 'batchGenerateContentAndWard')
      .addSeparator()
      .addItem('Chỉ đồng bộ Tiêu đề sang Source (hàng loạt)', 'batchSyncTitleToSource')
      .addItem('Đồng bộ System ID sang Source', 'syncSystemIdToSource')
      .addItem('Gen lại Mã Khang Ngô (dòng chọn)', 'batchRegenerateKhangNgoId')
      .addToUi();
}"""

new_on_open = """function onOpen() {
  var ui = SpreadsheetApp.getUi();
  
  // Gộp chung tất cả các Menu vào một chỗ để không bị ghi đè bởi file khác
  ui.createMenu('🤖 AI Tools')
      .addItem('Tự động viết Content & tra Phường cũ', 'batchGenerateContentAndWard')
      .addSeparator()
      .addItem('Chỉ đồng bộ Tiêu đề sang Source (hàng loạt)', 'batchSyncTitleToSource')
      .addItem('Đồng bộ System ID sang Source', 'syncSystemIdToSource')
      .addItem('Gen lại Mã Khang Ngô (dòng chọn)', 'batchRegenerateKhangNgoId')
      .addSeparator()
      .addItem('Di cư ảnh Cloudinary sang Source (hàng loạt)', 'migrateSourceImages')
      .addToUi();
}"""

if new_on_open in content:
    content = content.replace(new_on_open, old_on_open)
    print("onOpen restored.")
else:
    print("new_on_open not found in file.")

# 2. Remove migrateSourceImages at the end
# The function starts with: /**\n * Tự động di cư hình ảnh đã qua xử lý Cloudinary từ Pool sang Source (Public) sheet (US-046.2)
target_comment = "/**\n * Tự động di cư hình ảnh đã qua xử lý Cloudinary từ Pool sang Source (Public) sheet (US-046.2)"
idx = content.find(target_comment)
if idx != -1:
    content = content[:idx]
    print("migrateSourceImages function removed.")
else:
    print("migrateSourceImages function not found.")

with open('pool_backend_v3.gs', 'w', encoding='utf-8') as f:
    f.write(content)
print("pool_backend_v3.gs restored successfully!")
