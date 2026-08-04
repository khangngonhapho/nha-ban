import os, re

def test_dual_stack_compare_images_matching_sync():
    """Xác minh api/index.js (Node.js) không chứa logic khớpbroad firstTok gây gom nhầm ảnh nhà khác"""
    index_js_path = os.path.join(os.path.dirname(__file__), "..", "api", "index.js")
    assert os.path.exists(index_js_path), "File api/index.js không tồn tại!"
    
    with open(index_js_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    # Đảm bảo không dính câu lệnh broad substring matching firstTok trong api/index.js
    assert "pAddr.includes(firstTok)" not in content, \
        "🚨 VI PHẠM DUAL-STACK SYNC: api/index.js chứa 'pAddr.includes(firstTok)' gây gom trùng 74 ảnh!"
