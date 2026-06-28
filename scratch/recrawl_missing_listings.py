import sqlite3
import sys
import os
import requests
import json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path to import try_refresh_tokens
sys.path.append("D:/LHTBrain/01_PROJECTS/BDS-KhangNgo")
from fetcher import try_refresh_tokens, extract_tokens

db_file = "raw_archive.db"

# The 5 listings that have proptech UUIDs
uuids = [
    "0ceb7a3b-206b-422e-8548-5e0f1e7a3310", # Row 8 (TK7UPXZI)
    "19e78de2-069a-4084-92ac-45c2a1649271", # Row 9 (TK7O6RYX)
    "49a99cdb-cb05-47da-b5d5-0d8a3556b697", # Row 11 (TK2L1LCP)
    "3d296527-12f8-4796-b759-c501ca421f6b", # Row 23 (TKQK1W9A)
    "4f92db9e-de71-4df3-91f6-cc198e84d1d3"  # Row 2 (TKQLMB8Q)
]

def main():
    print("=== STARTING DETAIL RE-CRAWL FOR 5 MISSING LISTINGS ===")
    
    # 1. Load cookie & authenticate
    cookie_path = "thienkhoi_cookie.txt"
    if not os.path.exists(cookie_path):
        print(f"[❌ ERROR] Cookie file '{cookie_path}' not found!")
        return
        
    print("[*] Refreshing token...")
    refreshed_cookie = try_refresh_tokens(cookie_path)
    if not refreshed_cookie:
        print("[❌ ERROR] Could not refresh tokens! Cookie might be expired.")
        return
        
    access_token, _, _ = extract_tokens(refreshed_cookie)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://proptech.thienkhoi.com",
        "Referer": "https://proptech.thienkhoi.com/"
    }
    
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    
    success_count = 0
    
    for uuid in uuids:
        print(f"\n[*] Crawling detail for UUID: {uuid}...")
        detail_api_url = f"https://backend.thienkhoi.com/product/v1/property/{uuid}"
        
        try:
            r = requests.get(detail_api_url, headers=headers, timeout=20)
            if r.status_code != 200:
                print(f"  [❌ LỖI] HTTP {r.status_code} khi tải chi tiết cho {uuid}")
                continue
                
            detail_json = r.json()
            detail_data = detail_json.get("data") or {}
            if not detail_data:
                print("  [⚠️ WARNING] Detail data is empty.")
                continue
                
            # Extract raw technical metadata
            raw_json_str = json.dumps(detail_data, ensure_ascii=False)
            current_time_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            lat = str(detail_data.get("latitude") or "")
            lng = str(detail_data.get("longitude") or "")
            place_name = detail_data.get("placeName") or ""
            street_name = (detail_data.get("street") or {}).get("name") if detail_data.get("street") else detail_data.get("streetName", "")
            road_width = str(detail_data.get("minimumRoadWidth") or "")
            comm_type = detail_data.get("commissionType") or ""
            comm_val = str(detail_data.get("commissionValue") or "")
            owner_side_id = str((detail_data.get("ownerSideUser") or {}).get("id") or "")
            created_at = detail_data.get("createdAt") or ""
            updated_at = detail_data.get("updatedAt") or ""
            status_nguon = detail_data.get("status") or ""
            is_signed = 1 if detail_data.get("contractType") else 0
            
            c.execute("""
                UPDATE listings 
                SET raw_json_full = ?, 
                    Last_Crawl = ?,
                    latitude = ?,
                    longitude = ?,
                    placeName = ?,
                    streetName = ?,
                    minimumRoadWidth = ?,
                    commissionType = ?,
                    commissionValue = ?,
                    ownerSideUserId = ?,
                    createdAt = ?,
                    updatedAt = ?,
                    status_nguon = ?,
                    isSigned = ?
                WHERE tk_id = ?
            """, (raw_json_str, current_time_str, lat, lng, place_name, street_name, 
                  road_width, comm_type, comm_val, owner_side_id, 
                  created_at, updated_at, status_nguon, is_signed, uuid))
            
            if c.rowcount > 0:
                print(f"  [✅ SUCCESS] Full technical metadata synced for tk_id '{uuid}' in SQLite listings.")
                success_count += 1
            else:
                print(f"  [⚠️ WARNING] tk_id '{uuid}' not found in listings table. Skipping update.")
                
        except Exception as e:
            print(f"  [❌ ERROR] Exception during crawl for {uuid}: {e}")
            
    conn.commit()
    conn.close()
    
    print(f"\n=== RE-CRAWL FINISHED: Successfully updated {success_count}/{len(uuids)} listings in SQLite! ===")

if __name__ == "__main__":
    main()
