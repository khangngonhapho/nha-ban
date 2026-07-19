import os
import sys
import json

# Ensure parent directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure STAGING is not set to target production database and spreadsheets
if "STAGING" in os.environ:
    del os.environ["STAGING"]

import manager
from manager import app

def main():
    tk_id = "00077626-638e-4943-a55c-35a915ab3b8a"
    print(f"=== STARTING END-TO-END TEST CRAWL FOR: {tk_id} ===")
    
    # 1. Read cookie
    cookie_path = "thienkhoi_cookie.txt"
    if not os.path.exists(cookie_path):
        print(f"[❌ ERROR] Cookie file '{cookie_path}' not found!")
        sys.exit(1)
        
    with open(cookie_path, "r", encoding="utf-8") as f:
        cookie = f.read().strip()
    print("Successfully read cookie.")
    
    # Write to local cookie.txt just in case it's used there
    with open("cookie.txt", "w", encoding="utf-8") as f:
        f.write(cookie)
        
    # 2. Simulate POST call to /api/listings/<tk_id>/recrawl
    print(f"\n1. Triggering crawl route for {tk_id}...")
    client = app.test_client()
    
    # We pass the cookie in the JSON body so the route automatically updates/saves it!
    response = client.post(f"/api/listings/{tk_id}/recrawl", json={"cookie": cookie})
    print(f"Status Code: {response.status_code}")
    res_data = response.get_json()
    print("Response Data:", json.dumps(res_data, indent=4, ensure_ascii=False))
    
    if response.status_code != 200 or not res_data or res_data.get("status") != "success":
        print("[❌ ERROR] Crawl failed!")
        sys.exit(1)
        
    # 3. Simulate image migration and auto-sheets publishing
    print(f"\n2. Triggering image migration and publishing thread for {tk_id}...")
    manager.run_image_migration_thread(limit=None, cookie=cookie, target_tk_id=tk_id, skip_sheets_publish=False)
    
    print("\n=== END-TO-END TEST CRAWL COMPLETED ===")

if __name__ == "__main__":
    main()
