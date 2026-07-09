# -*- coding: utf-8 -*-
"""
Curation routes for BDS KhangNgo.
Serves web UI pages and handles AI content generation.
"""

import os
import json
import requests
from flask import Blueprint, Response, jsonify, request
from curator_html_data import CURATOR_HTML_CONTENT

routes_curation = Blueprint('routes_curation', __name__)

@routes_curation.route('/')
def index():
    """Trả về giao diện web biên tập viên kèm headers chống cache trình duyệt cứng"""
    if os.path.exists("curator.html"):
        with open("curator.html", "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = CURATOR_HTML_CONTENT
    resp = Response(content, mimetype='text/html')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@routes_curation.route('/index.html')
def index_html():
    """Trả về giao diện web client index.html"""
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()
    else:
        return "index.html not found", 404
    resp = Response(content, mimetype='text/html')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@routes_curation.route('/canvas')
@routes_curation.route('/canvas.html')
def canvas_view():
    """Trả về giao diện trực quan xem chi tiết căn nhà canvas.html"""
    if os.path.exists("canvas.html"):
        with open("canvas.html", "r", encoding="utf-8") as f:
            content = f.read()
    else:
        return "canvas.html not found", 404
    resp = Response(content, mimetype='text/html')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@routes_curation.route('/view-images')
@routes_curation.route('/view-images.html')
def view_images():
    """Trả về giao diện xem và tải ảnh hàng loạt view-images.html"""
    if os.path.exists("view-images.html"):
        with open("view-images.html", "r", encoding="utf-8") as f:
            content = f.read()
    else:
        return "view-images.html not found", 404
    resp = Response(content, mimetype='text/html')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@routes_curation.route('/api/proxy-download')
def proxy_download():
    """API Proxy tải ảnh từ xa không bị chặn CORS"""
    target_url = request.args.get('url')
    filename = request.args.get('filename', 'image.jpg')
    if not target_url:
        return "Missing url parameter", 400
    try:
        r = requests.get(target_url, stream=True, timeout=10)
        r.raise_for_status()
        
        clean_filename = filename.replace('"', '').replace('\\', '')
        
        headers = {
            'Content-Type': r.headers.get('Content-Type', 'application/octet-stream'),
            'Content-Disposition': f'attachment; filename="{clean_filename}"',
            'Cache-Control': 'public, max-age=2592000'
        }
        return Response(r.content, headers=headers)
    except Exception as e:
        return f"Failed to proxy image: {str(e)}", 500

@routes_curation.route('/manifest.json')
def manifest_json():
    """Trả về tệp cấu hình manifest.json cho PWA"""
    if os.path.exists("manifest.json"):
        with open("manifest.json", "r", encoding="utf-8") as f:
            content = f.read()
    else:
        return "manifest.json not found", 404
    return Response(content, mimetype='application/json')

@routes_curation.route('/sw.js')
def sw_js():
    """Trả về tệp Service Worker sw.js cho PWA"""
    if os.path.exists("sw.js"):
        with open("sw.js", "r", encoding="utf-8") as f:
            content = f.read()
    else:
        return "sw.js not found", 404
    resp = Response(content, mimetype='application/javascript')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return resp

@routes_curation.route('/api/ai/generate', methods=['POST'])
def ai_generate():
    """Gọi OpenAI gpt-4o-mini để sinh Tiêu đề, Mô tả và tìm Phường cũ"""
    import manager
    try:
        data = request.json or {}
        cfg = manager.load_config()
        
        api_key = cfg.get("openai_api_key", "").strip()
        if not api_key:
            return jsonify({
                "status": "error",
                "message": "Chưa cấu hình OpenAI API Key. Vui lòng vào mục 'Cấu hình Hệ thống & API' để thiết lập."
            }), 400
            
        # Tải prompt động từ Google Doc nếu cấu hình
        doc_id = cfg.get("prompt_google_doc_id", "")
        doc_prompt = None
        if doc_id:
            doc_prompt = manager.fetch_google_doc_content(doc_id)
            
        if doc_prompt:
            system_prompt = doc_prompt
        else:
            system_prompt = cfg.get("openai_system_prompt", manager.DEFAULT_CONFIG["openai_system_prompt"])
            
        # Nối chỉ thị JSON để đảm bảo AI trả về cấu trúc chính xác
        json_suffix = (
            "\n\n🚨 BẮT BUỘC ĐỊNH DẠNG ĐẦU RA (OUTPUT FORMAT):\n"
            "Bạn PHẢI trả về kết quả dưới dạng JSON object duy nhất có cấu trúc chính xác sau, không chứa ký tự markdown (như ```json) hay văn bản nào bên ngoài:\n"
            "{\n"
            "  \"tieuDeChinh\": \"Tiêu đề public chính (viết theo hướng dẫn của Mục 1 thuộc Bước 3)\",\n"
            "  \"tieuDePhu\": \"Tiêu đề phụ public (bắt buộc viết hoa toàn bộ, bắt đầu bằng biểu tượng 🏩, viết theo hướng dẫn của Mục 2 thuộc Bước 3)\",\n"
            "  \"moTaChiTiet\": \"Mô tả chi tiết (bắt đầu bằng chữ 'Mô tả:', tiếp nối ngay bên dưới là các dòng con bắt đầu bằng dấu cộng '+' theo hướng dẫn của Mục 3 thuộc Bước 3)\",\n"
            "  \"gocNhinDauTu\": \"Góc nhìn đầu tư (bắt đầu bằng dòng tiêu đề viết hoa toàn bộ 'GÓC NHÌN ĐẦU TƯ...' sau đó là các dòng con bắt đầu bằng dấu chấm tròn nhỏ '•' theo hướng dẫn của Mục 4 thuộc Bước 3. Để trống nếu không thỏa mãn bộ lọc điều kiện)\",\n"
            "  \"phuongCu\": \"Tên phường cũ (nếu có sáp nhập phường, hoặc để trống)\"\n"
            "}"
        )
        if "tieuDeChinh" not in system_prompt or "moTaChiTiet" not in system_prompt:
            system_prompt += json_suffix
        
        # 1. Tính toán Tiền tố địa chỉ (Mặt tiền / HXH)
        so_nha = manager.safe_str(data.get("soNha"))
        duong_truoc_nha = manager.safe_str(data.get("duongTruocNha"))
        phan_loai_hem = manager.safe_str(data.get("phanLoaiHem")).lower()
        
        is_mat_tien = False
        if so_nha:
            if "." not in so_nha:
                is_mat_tien = True
        elif "mặt tiền" in phan_loai_hem or "mặt phố" in phan_loai_hem:
            is_mat_tien = True
            
        try:
            width_val = float(duong_truoc_nha) if duong_truoc_nha else 0.0
        except ValueError:
            width_val = 0.0
            
        tien_to = ""
        if is_mat_tien:
            tien_to = "Mặt tiền "
        elif width_val >= 4.0:
            tien_to = "HXH "
            
        # 2. Xử lý định dạng Giá (tương thích Thiên Khôi)
        gia_chao = data.get("giaChao", "")
        try:
            gia_ty = float(gia_chao)
            if gia_ty > 100:
                gia_ty = gia_ty / 1000
            gia_format = f"{gia_ty} tỷ" if gia_ty > 0 else ""
        except ValueError:
            gia_format = gia_chao
            
        # 3. Tạo User Prompt
        user_prompt = (
            "THÔNG TIN CĂN NHÀ:\n"
            f"- Địa chỉ: {data.get('soNha', '')} {data.get('duong', '')}, Phường {data.get('phuong', '')}, Quận {data.get('quan', '')}\n"
            f"- Nội dung chính gốc (chứa kích thước ở đầu): {data.get('noiDungChinh', '')}\n"
            f"- DT Thực tế: {data.get('dtThucTe', '')}m2 | DT Trên sổ: {data.get('dtTrenSo', '')}m2\n"
            f"- Chiều ngang (mặt tiền): {data.get('matTien', '')}m\n"
            f"- Hướng: {data.get('huong', '')}\n"
            f"- Kết cấu: {data.get('soTang', '')} tầng, {data.get('soPhongNgu', '')} PN, {data.get('soToilet', '')} WC\n"
            f"- Hẻm: {data.get('phanLoaiHem', '')} (Rộng: {data.get('duongTruocNha', '')}m)\n"
            f"- Giá: {gia_format}\n"
            f"- Phân loại / Tag USP: {data.get('phanLoai', '')}\n"
            f"- Điểm nổi bật của căn nhà (nguồn USP chính): {data.get('moTaChiTiet', '')}\n\n"
            "LƯU Ý QUAN TRỌNG: Đọc kỹ 'Nội dung chính gốc', 'Phân loại / Tag USP' và 'Điểm nổi bật' — bắt buộc phản ánh các thông số kỹ thuật và ưu điểm vào Tiêu đề và Mô tả. BẮT BUỘC bắt đầu phần tiêu đề trực tiếp bằng tiền tố '" + tien_to + "' kết hợp liền mạch với Tên đường (TUYỆT ĐỐI không chèn thêm bất kỳ dấu gạch ngang, dấu chấm hay ký tự đặc biệt nào giữa tiền tố này và tên đường, Ví dụ: " + (f"'{tien_to}Trần Quang Diệu - ...'" if tien_to else "'Trần Quang Diệu - ...'") + ").\n"
            "🚨 YÊU CẦU ĐỊNH DẠNG: Bắt buộc phải trả về kết quả dưới định dạng JSON sạch (respond in json format) theo đúng cấu trúc yêu cầu trong System Prompt."
        )
        
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        api_base = cfg.get("openai_api_base", "https://api.openai.com/v1").strip().rstrip('/')
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{api_base}/chat/completions", json=payload, headers=headers, timeout=30)
        res_json = response.json()
        
        if response.status_code == 200:
            ai_message = res_json["choices"][0]["message"]["content"]
            manager.add_log_message(f"[🤖 AI] Nhận kết quả từ OpenAI: {ai_message}")
            ai_data = json.loads(ai_message)
            
            tieu_de_clean, mo_ta_clean, phuong_cu_raw = manager.parse_and_join_ai_response(ai_data)
            return jsonify({
                "status": "success",
                "tieu_de_public": tieu_de_clean,
                "mo_ta_public": mo_ta_clean,
                "phuong_cu": phuong_cu_raw
            })
        else:
            err_msg = res_json.get("error", {}).get("message", "Lỗi không xác định từ OpenAI.")
            return jsonify({"status": "error", "message": f"OpenAI API Error: {err_msg}"}), response.status_code
            
    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi gọi OpenAI API: {str(e)}"}), 500
