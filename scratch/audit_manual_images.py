import sqlite3
import os
import sys
import re
import json
import requests
import concurrent.futures

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/raw_archive.db"
REPORT_PATH = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/broken_listings_report.md"

def is_manual_image(url):
    if not url:
        return False
    url_lower = url.strip().lower()
    if not url_lower:
        return False
    
    # Local static images
    if "static/images/" in url_lower:
        return True
    # Google Drive share links
    if "drive.google.com" in url_lower or "google.com/drive" in url_lower:
        return True
    # Web uploader pattern
    if "_sodo" in url_lower or "_interior_" in url_lower:
        return True
    # Cloudinary/R2 containing System ID (SYS-)
    if "sys-" in url_lower:
        return True
        
    return False

def verify_image(url):
    """
    Checks if an image is viewable.
    Returns: (is_ok, reason)
    """
    url_clean = url.strip()
    # Check if local path
    if url_clean.startswith("/static/") or "static/images/" in url_clean.lower():
        # Clean relative path
        rel_path = url_clean
        if rel_path.startswith("/"):
            rel_path = rel_path[1:]
        # Standardize path separators for Windows
        abs_path = os.path.join("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo", rel_path.replace("/", os.sep))
        if os.path.exists(abs_path):
            return True, "Cục bộ - Tồn tại"
        else:
            return False, "Cục bộ - File không tồn tại"
            
    # Check if remote URL
    if url_clean.startswith("http://") or url_clean.startswith("https://"):
        try:
            # Use GET with stream=True to fetch headers first (like HEAD, but wider server support)
            res = requests.get(url_clean, timeout=5, stream=True)
            if res.status_code == 200:
                return True, "HTTP 200 OK"
            else:
                return False, f"HTTP Status {res.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Lỗi kết nối: {type(e).__name__}"
            
    return False, "Đường dẫn không hợp lệ"

def scan_manual_images():
    print(f"[*] Đang kết nối CSDL Pool1: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("[❌ Error] Không tìm thấy tệp raw_archive.db")
        return []
        
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get all listings
    rows = c.execute("SELECT * FROM listings").fetchall()
    print(f"[*] Quét qua {len(rows)} căn trong SQLite...")
    
    # Detect image columns
    columns = [col[1] for col in c.execute("PRAGMA table_info(listings)").fetchall()]
    image_cols = [col for col in columns if col.startswith("Anh_") or col.startswith("So_do_thua_dat_") or col.startswith("Hinh_")]
    print(f"[*] Phát hiện {len(image_cols)} cột hình ảnh.")
    
    manual_listings = []
    
    for row in rows:
        tk_id = row["tk_id"]
        sys_id = row["System_ID"]
        kn_id = row["Ma_Khang_Ngo_ID"]
        
        # Info details
        ngo_so_nha = row["Ngo_So_nha"] or ""
        duong = row["Duong"] or ""
        phuong = row["Phuong"] or ""
        quan = row["Quan"] or ""
        
        manual_images = []
        for col in image_cols:
            val = row[col]
            if not val:
                continue
            
            # Since some fields might contain JSON arrays due to legacy issues, parse them if they look like JSON
            urls = []
            val_stripped = str(val).strip()
            if val_stripped.startswith("[") and val_stripped.endswith("]"):
                try:
                    urls = json.loads(val_stripped)
                except Exception:
                    urls = [val_stripped]
            else:
                urls = [val_stripped]
                
            for url in urls:
                if is_manual_image(url):
                    manual_images.append({
                        "col": col,
                        "url": url
                    })
                    
        if manual_images:
            manual_listings.append({
                "tk_id": tk_id,
                "sys_id": sys_id,
                "kn_id": kn_id,
                "address": f"{ngo_so_nha} {duong}, {phuong}, {quan}",
                "images": manual_images
            })
            
    conn.close()
    print(f"[✅] Đã phát hiện {len(manual_listings)} căn có ảnh tự tải lên.")
    return manual_listings

def main():
    manual_listings = scan_manual_images()
    
    # Verify all manual images in parallel
    print("[*] Đang thực hiện kiểm thử tính khả dụng của ảnh tự tải lên...")
    all_images_to_check = []
    for ml in manual_listings:
        for img in ml["images"]:
            all_images_to_check.append(img["url"])
            
    # Deduplicate URLs to check
    unique_urls = list(set(all_images_to_check))
    print(f"[*] Tổng số ảnh tự tải lên độc nhất cần kiểm tra: {len(unique_urls)}")
    
    url_statuses = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(verify_image, url): url for url in unique_urls}
        completed = 0
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                is_ok, reason = future.result()
                url_statuses[url] = {"ok": is_ok, "reason": reason}
            except Exception as e:
                url_statuses[url] = {"ok": False, "reason": f"Lỗi script: {str(e)}"}
            completed += 1
            if completed % 10 == 0 or completed == len(unique_urls):
                print(f" -> Đã kiểm tra: {completed}/{len(unique_urls)}")
                
    # Parse existing broken_listings_report.md
    print(f"[*] Đọc tệp báo cáo cũ tại: {REPORT_PATH}")
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            old_content = f.read()
    else:
        print("[⚠️ Warning] Không tìm thấy file broken_listings_report.md cũ. Sẽ tạo mới.")
        old_content = ""
        
    # Split the old report to extract List 1 and List 2
    # Search for heading ## 🗄️
    list1_text = ""
    list2_text = ""
    
    if old_content:
        # Standardize the file into sections
        # The split marker is the second heading: ## 🗄️
        split_marker = "## 🗄️"
        if split_marker in old_content:
            parts = old_content.split(split_marker)
            # Part 0 has the title and list 1
            list1_part = parts[0].strip()
            # Remove the main title from list1 if we want to format it as ## heading
            # Let's clean up list1_part
            # Replace main `# Báo cáo danh sách căn bị lỗi ảnh (Cloudinary 404)` with `## 📊 Danh sách 1: Các căn lỗi ảnh Cloudinary 404 trên Google Sheets Pool (v1)`
            lines_l1 = list1_part.split("\n")
            cleaned_l1_lines = []
            for line in lines_l1:
                if line.startswith("# Báo cáo danh sách căn"):
                    cleaned_l1_lines.append("## 📊 Danh sách 1: Các căn lỗi ảnh Cloudinary 404 trên Google Sheets Pool (v1)")
                else:
                    cleaned_l1_lines.append(line)
            list1_text = "\n".join(cleaned_l1_lines).strip()
            
            # Part 1 has list 2
            # Reconstruct list 2 heading
            list2_part = parts[1].strip()
            # Let's change the heading of list 2 to include "Danh sách 2"
            lines_l2 = list2_part.split("\n")
            cleaned_l2_lines = []
            if lines_l2 and "Danh sách căn chưa di cư" in lines_l2[0]:
                cleaned_l2_lines.append("## 🗄️ Danh sách 2: Các căn lỗi ảnh Cloudinary 404 trong SQLite raw_archive.db")
            else:
                cleaned_l2_lines.append("## 🗄️ Danh sách 2: Các căn lỗi ảnh Cloudinary 404 trong SQLite raw_archive.db")
                cleaned_l2_lines.append(lines_l2[0])
            cleaned_l2_lines.extend(lines_l2[1:])
            list2_text = "\n".join(cleaned_l2_lines).strip()
        else:
            # Fallback if no split marker found
            list1_text = "## 📊 Danh sách 1: Các căn lỗi ảnh Cloudinary 404 trên Google Sheets Pool (v1)\n\n" + old_content
            list2_text = "## 🗄️ Danh sách 2: Các căn lỗi ảnh Cloudinary 404 trong SQLite raw_archive.db\n\n*(Chưa có dữ liệu)*"
    else:
        list1_text = "## 📊 Danh sách 1: Các căn lỗi ảnh Cloudinary 404 trên Google Sheets Pool (v1)\n\n*(Chưa có dữ liệu)*"
        list2_text = "## 🗄️ Danh sách 2: Các căn lỗi ảnh Cloudinary 404 trong SQLite raw_archive.db\n\n*(Chưa có dữ liệu)*"
        
    # Generate List 3
    print("[*] Đang tổng hợp Danh sách 3: Trạng thái hình ảnh tự tải lên...")
    list3_header = "## 🖼️ Danh sách 3: Trạng thái các căn có hình ảnh tự tải lên (Local / Drive / Cloudflare R2 / Custom Cloudinary)\n\n"
    list3_desc = "Dưới đây là danh sách toàn bộ các căn trong cơ sở dữ liệu SQLite (`raw_archive.db`) có chứa hình ảnh do người dùng tự tải lên trực tiếp (local file, Drive link hoặc custom R2/Cloudinary) và kết quả kiểm toán khả dụng của chúng.\n\n"
    
    list3_table_header = "| STT | Mã Hàng | System ID | Ngõ/Số nhà / Đường | Tổng số ảnh | Trạng thái chi tiết |\n"
    list3_table_sep = "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
    list3_rows = []
    
    total_manual_listings = len(manual_listings)
    total_broken_manual_listings = 0
    total_ok_manual_listings = 0
    
    for idx, ml in enumerate(manual_listings, start=1):
        kn_id = ml["kn_id"] or "(Chưa có)"
        sys_id = ml["sys_id"] or "(Chưa có)"
        address = ml["address"]
        images = ml["images"]
        
        # Check if all images are OK
        broken_details = []
        for img in images:
            url = img["url"]
            col = img["col"]
            status = url_statuses.get(url, {"ok": False, "reason": "Chưa kiểm tra"})
            if not status["ok"]:
                broken_details.append(f"❌ **{col}**: {status['reason']} (Link: {url})")
                
        if not broken_details:
            status_str = "✅ Tất cả OK"
            total_ok_manual_listings += 1
        else:
            status_str = "<br>".join(broken_details)
            total_broken_manual_listings += 1
            
        list3_rows.append(f"| {idx} | **{kn_id}** | `{sys_id}` | {address} | {len(images)} | {status_str} |")
        
    list3_stats = f"**Thống kê hình ảnh tự tải lên:**\n- Tổng số căn có ảnh tự tải lên: {total_manual_listings} căn\n- Số căn hoạt động hoàn hảo: {total_ok_manual_listings} căn\n- Số căn có ảnh lỗi cần xử lý: {total_broken_manual_listings} căn\n\n"
    
    list3_text = list3_header + list3_desc + list3_stats + list3_table_header + list3_table_sep + "\n".join(list3_rows)
    
    # Write the unified consolidated report
    print(f"[*] Ghi đè báo cáo hợp nhất hoàn chỉnh vào: {REPORT_PATH}")
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Báo cáo tổng hợp chất lượng và trạng thái hình ảnh rổ hàng\n\n")
        f.write("Báo cáo này được tự động tạo và cập nhật định kỳ để kiểm toán toàn bộ trạng thái hình ảnh các căn nhà bán.\n\n")
        f.write(list1_text.strip() + "\n\n---\n\n")
        f.write(list2_text.strip() + "\n\n---\n\n")
        f.write(list3_text.strip() + "\n")
        
    print("[✅] Đã hoàn thành cập nhật báo cáo broken_listings_report.md thành công!")

if __name__ == "__main__":
    main()
