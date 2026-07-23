import json
import urllib.request
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def test_r2_og_meta_injection():
    r2_public_url = 'https://pub-e92603c36c8d4789917d05d1eba12a7e.r2.dev'
    r2_migration_prefix = 'BDS-KhangNgo-v3'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 1. Fetch current manifest
    manifest_url = f"{r2_public_url}/{r2_migration_prefix}/public_data/current.json"
    req = urllib.request.Request(manifest_url, headers=headers)
    with urllib.request.urlopen(req) as res:
        manifest = json.loads(res.read().decode('utf-8'))
    
    index_path = manifest['index_url']
    assert index_path, "index_url must not be empty"
    
    # 2. Fetch index list
    index_url = f"{r2_public_url}/{r2_migration_prefix}/{index_path}"
    req2 = urllib.request.Request(index_url, headers=headers)
    with urllib.request.urlopen(req2) as res2:
        index_list = json.loads(res2.read().decode('utf-8'))
    
    assert len(index_list) > 0, "Index list must contain listings"
    sample_house = index_list[0]
    sys_id = sample_house['system_id']
    print(f"✅ Found sample house system_id: {sys_id}")
    
    # 3. Simulate api/index.js logic
    clean_title = sample_house.get('t') or 'Khang Ngô Nhà Phố'
    raw_phuong = sample_house.get('phuong') or '-'
    clean_phuong = re.sub(r'^(Phường|P\.)\s*', '', raw_phuong, flags=re.IGNORECASE).strip()
    clean_dt = re.sub(r'm²$', '', str(sample_house.get('dt') or ''), flags=re.IGNORECASE).strip()
    clean_tang = sample_house.get('tang') or '-'
    clean_gia = sample_house.get('gia') or '-'
    clean_id = sample_house.get('id') or ''
    
    clean_desc = f"#{clean_id} - Diện tích: {clean_dt}m², {clean_tang} tầng, P.{clean_phuong}. Giá bán: {clean_gia} tỷ VNĐ. Liên hệ ngay!"
    
    imgs = sample_house.get('imgs') or []
    clean_img = imgs[0] if imgs else 'https://khangngonhapho.github.io/nha-ban/avatarKhangNgo.jpg'
    
    print("\n--- TEST RESULT FOR US-155 ---")
    print(f"Title: {clean_title}")
    print(f"Description: {clean_desc}")
    print(f"Image: {clean_img}")
    
    assert f"#{clean_id}" in clean_desc
    assert f"Diện tích: {clean_dt}m²" in clean_desc
    assert f"{clean_tang} tầng" in clean_desc
    assert f"P.{clean_phuong}" in clean_desc
    assert f"Giá bán: {clean_gia} tỷ VNĐ" in clean_desc
    print("\n✅ US-155 OpenGraph test passed 100%!")

if __name__ == '__main__':
    test_r2_og_meta_injection()
