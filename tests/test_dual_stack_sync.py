import os

def test_dual_stack_compare_images_matching_sync():
    """Xác minh api/index.js (Node.js) không chứa logic khớp broad firstTok và có định nghĩa foundAddr"""
    index_js_path = os.path.join(os.path.dirname(__file__), "..", "api", "index.js")
    assert os.path.exists(index_js_path), "File api/index.js không tồn tại!"
    
    with open(index_js_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    assert "pAddr.includes(firstTok)" not in content, \
        "🚨 VI PHẠM DUAL-STACK SYNC: api/index.js chứa 'pAddr.includes(firstTok)' gây gom trùng 74 ảnh!"

    assert "const foundAddr =" in content, \
        "🚨 VI PHẠM DUAL-STACK SYNC: api/index.js thiếu khai báo 'const foundAddr =' làm mất thông tin khớp địa chỉ!"
