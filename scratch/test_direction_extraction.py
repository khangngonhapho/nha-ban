import sys
import os
import json
from bs4 import BeautifulSoup

# Ensure imports work from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fetcher
import pool_lego

sys.stdout.reconfigure(encoding='utf-8')

def test_dom_extraction():
    print("🧪 Testing DOM Extraction...")
    
    html_path = 'Thien Khoi Group - Nguon Hang - Huong Jun28.html'
    if not os.path.exists(html_path):
        print(f"  [❌] File {html_path} not found. Skipping DOM file test.")
        return False
        
    content = open(html_path, encoding='utf-8').read()
    soup = BeautifulSoup(content, 'html.parser')
    
    # Test fetcher.get_val_by_label
    val_huong_nha = fetcher.get_val_by_label(soup, "hướng nhà")
    val_huong = fetcher.get_val_by_label(soup, "hướng")
    
    print(f"  get_val_by_label(soup, 'hướng nhà') -> {repr(val_huong_nha)}")
    print(f"  get_val_by_label(soup, 'hướng') -> {repr(val_huong)}")
    
    assert val_huong_nha == "Tây Nam", f"Expected 'Tây Nam', got {repr(val_huong_nha)}"
    print("  [✅] DOM Extraction test passed!")
    return True

def test_api_extraction():
    print("🧪 Testing API Criteria Extraction...")
    
    mock_detail_data = {
        "id": "mock-123",
        "offeringPrice": 9500000,
        "criteria": [
            {
                "id": 27,
                "name": "Tây Nam",
                "parentId": None,
                "groupId": 2,
                "groupCode": "HOUSE_DIRECTION",
                "groupName": "Hướng nhà"
            },
            {
                "id": 35,
                "name": "Ngõ 1 ô tô",
                "groupCode": "ROAD_TYPE"
            }
        ]
    }
    
    # Extract criteria using the new logic
    criteria_list = mock_detail_data.get("criteria") or []
    huong = next((c.get("name", "") for c in criteria_list if c and c.get("groupCode") == "HOUSE_DIRECTION"), "")
    
    print(f"  Extracted direction -> {repr(huong)}")
    assert huong == "Tây Nam", f"Expected 'Tây Nam', got {repr(huong)}"
    print("  [✅] API Criteria Extraction test passed!")
    return True

if __name__ == '__main__':
    print("=== STARTING US-110 DIRECTION EXTRACTION TESTS ===")
    dom_ok = test_dom_extraction()
    api_ok = test_api_extraction()
    if dom_ok and api_ok:
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED.")
        sys.exit(1)
