# tests/test_r2_recovery.py
import pytest
import json
import manager

def test_get_r2_subfolder():
    # 1. Normal address
    row_dict_1 = {
        "Ngo_So_nha": "123",
        "Duong": "Nguyễn Trãi"
    }
    subfolder_1 = manager.get_r2_subfolder("test-uuid-1", row_dict_1)
    assert subfolder_1 == "test-uuid-1 - 123 Nguyen Trai"

    # 2. Address containing '+' character (Must discard anything after '+')
    row_dict_2 = {
        "Ngo_So_nha": "1168.42+44",
        "Duong": "Ba Tháng Hai"
    }
    subfolder_2 = manager.get_r2_subfolder("test-uuid-2", row_dict_2)
    assert subfolder_2 == "test-uuid-2 - 1168.42 Ba Thang Hai"

    # 3. Special naming conventions
    row_dict_3 = {
        "Ngo_So_nha": "456",
        "Duong": "Cách Mạng Tháng 8"
    }
    subfolder_3 = manager.get_r2_subfolder("test-uuid-3", row_dict_3)
    assert subfolder_3 == "test-uuid-3 - 456 Cach Mang Thang 8"

    row_dict_4 = {
        "Ngo_So_nha": "789",
        "Duong": "Đường số 7"
    }
    subfolder_4 = manager.get_r2_subfolder("test-uuid-4", row_dict_4)
    assert subfolder_4 == "test-uuid-4 - 789 Duong so 7"

def test_rebuild_admin_public_images_json():
    # Curated config with various roles
    curated_config = {
        "images": [
            {"url": "https://pub-xxx.r2.dev/img_1.jpg", "role": "Mặt tiền", "visible": True},
            {"url": "https://pub-xxx.r2.dev/img_2.jpg", "role": "Sơ đồ", "visible": False},
            {"url": "https://pub-xxx.r2.dev/img_3.jpg", "role": "Bìa", "visible": True},
            {"url": "https://pub-xxx.r2.dev/SYS-test_manual.jpg", "role": "Nội thất", "visible": True}
        ]
    }
    manual_images = ["https://pub-xxx.r2.dev/SYS-test_manual.jpg"]
    
    admin_str, public_str = manager.rebuild_admin_public_images_json(curated_config, manual_images)
    
    admin_list = json.loads(admin_str)
    public_list = json.loads(public_str)
    
    assert len(admin_list) == 4
    # Image roles conversion check
    assert admin_list[0]["role"] == "facade"
    assert admin_list[1]["role"] == "diagram"
    assert admin_list[2]["role"] == "cover"
    assert admin_list[3]["role"] == "interior"
    
    # Origin check
    assert admin_list[0]["origin"] == "crawl"
    assert admin_list[3]["origin"] == "self"
    
    # Public images check (must exclude diagram/facade, cover first)
    assert len(public_list) == 2
    assert public_list[0] == "https://pub-xxx.r2.dev/img_3.jpg" # cover
    assert public_list[1] == "https://pub-xxx.r2.dev/SYS-test_manual.jpg" # interior
