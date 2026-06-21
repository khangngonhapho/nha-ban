# -*- coding: utf-8 -*-
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Let's load the data from secure sheets to simulate what lego_core.js gets.
import gspread
from oauth2client.service_account import ServiceAccountCredentials

creds_file = "d:/LHTBrain/01_PROJECTS/BDS-KhangNgo/khangngo-admin-a96043c2f638.json"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if os.path.exists(creds_file):
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    
    POOL_SHEET_ID = '1PJYJgfiCKwhJxQibZu1Pxn-ARlkYoUimw0flP3_yxzw'
    SOURCE_SHEET_ID = '1to1i48iaoKlu8ZizUqe9axZ-Mj-zswpQwdCECTOdTzE'
    
    # Fetch all records
    source_sheet = client.open_by_key(SOURCE_SHEET_ID).worksheet("Source")
    source_rows = source_sheet.get_all_values()
    
    pool_sheet = client.open_by_key(POOL_SHEET_ID).worksheet("Pool")
    pool_rows = pool_sheet.get_all_values()
    
    print(f"Loaded source rows: {len(source_rows)}, pool rows: {len(pool_rows)}")
    
    # Simulate parser logic in lego_core.js for SOURCE + POOL matching
    # Bỏ qua hàng tiêu đề
    source_records = source_rows[1:]
    pool_records = pool_rows[1:]
    
    def parseGia(val):
        if not val: return 0
        s = str(val).strip().replace(',', '.')
        try:
            num = float(s)
            if num > 100: num = num / 1000
            return round(num * 1000) / 1000
        except ValueError:
            return 0
            
    # Map SOURCE
    DATA = []
    for index, sr in enumerate(source_records):
        if len(sr) < 5: continue
        if not sr[3] and not sr[4]: continue
        
        dt = 0
        try: dt = float(sr[5])
        except ValueError: pass
        
        gia = parseGia(sr[8])
        
        rawQ = sr[9] if len(sr) > 9 else ''
        cleanQ = str(rawQ).replace('Quận', '').replace('Q.', '').replace('Q', '').strip()
        if cleanQ.endswith('.0'): cleanQ = cleanQ[:-2]
        
        cleanQLower = cleanQ.lower()
        if 'phú nhuận' in cleanQLower or cleanQLower == 'pn': cleanQ = 'pn'
        elif 'tân bình' in cleanQLower or cleanQLower == 'tb': cleanQ = 'tb'
        elif 'bình thạnh' in cleanQLower or cleanQLower == 'bt': cleanQ = 'bt'
        elif 'gò vấp' in cleanQLower or cleanQLower == 'gv': cleanQ = 'gv'
        elif 'tân phú' in cleanQLower or cleanQLower == 'tp': cleanQ = 'tp'
        elif 'bình tân' in cleanQLower or cleanQLower == 'btan': cleanQ = 'btan'
        elif 'thủ đức' in cleanQLower or cleanQLower == 'td': cleanQ = 'td'
        elif 'hóc môn' in cleanQLower or cleanQLower == 'hm': cleanQ = 'hm'
        elif 'nhà bè' in cleanQLower or cleanQLower == 'nb': cleanQ = 'nb'
        elif 'bình chánh' in cleanQLower or cleanQLower == 'bc': cleanQ = 'bc'
        elif 'củ chi' in cleanQLower or cleanQLower == 'cc': cleanQ = 'cc'
        
        srSystemId = sr[37] if len(sr) > 37 else ''
        srId = sr[3] if len(sr) > 3 else ''
        
        # Find pool match
        poolRow = None
        for pr in pool_records:
            prSystemId = pr[72] if len(pr) > 72 else ''
            prId = pr[55] if len(pr) > 55 else ''
            if (srSystemId and prSystemId == srSystemId) or (srId and prId == srId) or (srSystemId and prId == srSystemId):
                poolRow = pr
                break
                
        p = {
            'id': srId,
            'system_id': srSystemId,
            'q': cleanQ.lower() if (not cleanQ.isdigit() or cleanQ == '') else 'q' + cleanQ,
            'phuong': sr[10] if len(sr) > 10 else '-',
            'is_invisible': 'ẩn' in str(sr[15]).lower() or 'đã bán' in str(sr[15]).lower() or 'invisible' in str(sr[15]).lower() if len(sr) > 15 else False,
            'json_ui_parsed': {}
        }
        if poolRow:
            jsonUiVal = ''
            if len(poolRow) > 93:
                jsonUiVal = poolRow[93]
            if not jsonUiVal or not str(jsonUiVal).strip().startswith('{'):
                for i in range(len(poolRow)-1, -1, -1):
                    val = poolRow[i]
                    if val and str(val).strip().startswith('{') and str(val).strip().endswith('}'):
                        jsonUiVal = val
                        break
            if jsonUiVal:
                try: p['json_ui_parsed'] = json.loads(jsonUiVal)
                except Exception: pass
        DATA.append(p)

    # Map POOL Rows
    MAPPED_POOL_DATA = []
    for index, row in enumerate(pool_records):
        systemId = row[72] if len(row) > 72 else (row[71] if len(row) > 71 else '')
        rawQ = row[3] if len(row) > 3 else ''
        cleanQ = str(rawQ).replace('Quận', '').replace('Q.', '').replace('Q', '').strip()
        if cleanQ.endswith('.0'): cleanQ = cleanQ[:-2]
        
        cleanQLower = cleanQ.lower()
        if 'phú nhuận' in cleanQLower or cleanQLower == 'pn': cleanQ = 'pn'
        elif 'tân bình' in cleanQLower or cleanQLower == 'tb': cleanQ = 'tb'
        elif 'bình thạnh' in cleanQLower or cleanQLower == 'bt': cleanQ = 'bt'
        elif 'gò vấp' in cleanQLower or cleanQLower == 'gv': cleanQ = 'gv'
        elif 'tân phú' in cleanQLower or cleanQLower == 'tp': cleanQ = 'tp'
        elif 'bình tân' in cleanQLower or cleanQLower == 'btan': cleanQ = 'btan'
        elif 'thủ đức' in cleanQLower or cleanQLower == 'td': cleanQ = 'td'
        elif 'hóc môn' in cleanQLower or cleanQLower == 'hm': cleanQ = 'hm'
        elif 'nhà bè' in cleanQLower or cleanQLower == 'nb': cleanQ = 'nb'
        elif 'bình chánh' in cleanQLower or cleanQLower == 'bc': cleanQ = 'bc'
        elif 'củ chi' in cleanQLower or cleanQLower == 'cc': cleanQ = 'cc'
        
        p = {
            'id': row[55] if len(row) > 55 else systemId,
            'system_id': systemId,
            'q': cleanQ.lower() if (not cleanQ.isdigit() or cleanQ == '') else 'q' + cleanQ,
            'phuong': row[4] if len(row) > 4 else '-',
            'json_ui_parsed': {}
        }
        
        jsonUiVal = row[93] if len(row) > 93 else ''
        if not jsonUiVal or not str(jsonUiVal).strip().startswith('{'):
            for i in range(len(row)-1, -1, -1):
                val = row[i]
                if val and str(val).strip().startswith('{') and str(val).strip().endswith('}'):
                    jsonUiVal = val
                    break
        if jsonUiVal:
            try: p['json_ui_parsed'] = json.loads(jsonUiVal)
            except Exception: pass
        MAPPED_POOL_DATA.append(p)
        
    print(f"Mapped DATA: {len(DATA)}, MAPPED_POOL_DATA: {len(MAPPED_POOL_DATA)}")
    
    # Test 1: Get filtered in POOL mode, activeDynamicFilters = {"Criteria_Duong_truoc_nha": "Ngõ ngách (2 - 2.5m)"}
    # And NO other filters
    active_filters = {"Criteria_Duong_truoc_nha": "Ngõ ngách (2 - 2.5m)"}
    a_pool = MAPPED_POOL_DATA
    for field, filterVal in active_filters.items():
        a_pool = [p for p in a_pool if filterVal.lower() in str(p['json_ui_parsed'].get(field, '')).lower()]
    print(f"\nFiltered POOL with dynamic filter: found {len(a_pool)} items:")
    for item in a_pool:
        print(f"  ID: {item['id']}, system_id: {item['system_id']}, q: {item['q']}, phuong: {item['phuong']}, json_ui: {item['json_ui_parsed']}")
        
    # Test 2: Get filtered in PUBLIC mode (window.DATA) with same filter
    a_pub = DATA
    for field, filterVal in active_filters.items():
        a_pub = [p for p in a_pub if filterVal.lower() in str(p['json_ui_parsed'].get(field, '')).lower()]
    print(f"\nFiltered PUBLIC with dynamic filter: found {len(a_pub)} items:")
    for item in a_pub:
        print(f"  ID: {item['id']}, system_id: {item['system_id']}, q: {item['q']}, phuong: {item['phuong']}, is_invisible: {item['is_invisible']}, json_ui: {item['json_ui_parsed']}")
        
else:
    print("Credentials file does not exist")
