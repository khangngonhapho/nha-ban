import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_api():
    print("--- 1. Testing GET /api/listings with no filters ---")
    res = requests.get(f"{BASE_URL}/api/listings?status=raw_complete")
    if res.status_code != 200:
        print(f"[ERROR] Failed: status_code = {res.status_code}")
        return
    data = res.json()
    listings = data.get("listings", [])
    print(f"[OK] Success! Found {len(listings)} listings in 'raw_complete' status.")
    
    if not listings:
        print("[INFO] No listings in 'raw_complete'. Let's try getting all status types...")
        res_all = requests.get(f"{BASE_URL}/api/listings")
        listings = res_all.json().get("listings", [])
        print(f"[INFO] Found {len(listings)} total listings.")
        
    if listings:
        sample = listings[0]
        quan = sample.get("Quan", "") or sample.get("Qu_n", "")
        duong = sample.get("Duong", "") or sample.get("___ng", "")
        sonha = sample.get("Ngo_So_nha", "") or sample.get("Ng__S__nh_", "")
        tk_id = sample.get("tk_id")
        
        print("\n--- 2. Testing Specific Filters based on Sample Card ---")
        # Use repr() to safely print strings without CP1252 exceptions
        print(f"Sample Address details (safe print): ID={tk_id}, District={repr(quan)}, Street={repr(duong)}, HouseNo={repr(sonha)}")
        
        # Filter by District
        if quan:
            res_q = requests.get(f"{BASE_URL}/api/listings?status=raw_complete&quan={quan}")
            cnt = len(res_q.json().get("listings", []))
            print(f"[OK] Filter by District={repr(quan)} returned {cnt} matches.")
            
        # Filter by Street
        if duong:
            res_d = requests.get(f"{BASE_URL}/api/listings?status=raw_complete&duong={duong}")
            cnt = len(res_d.json().get("listings", []))
            print(f"[OK] Filter by Street={repr(duong)} returned {cnt} matches.")
            
        # Filter by House Number
        if sonha:
            res_s = requests.get(f"{BASE_URL}/api/listings?status=raw_complete&so_nha={sonha}")
            cnt = len(res_s.json().get("listings", []))
            print(f"[OK] Filter by HouseNo={repr(sonha)} returned {cnt} matches.")
            
        # Test Bulk Publish API (Dry run with invalid ID to check endpoint, or mock call)
        print("\n--- 3. Testing POST /api/listings/bulk-publish ---")
        payload = {"ids": ["dummy-test-id-1234"]}
        res_bulk = requests.post(f"{BASE_URL}/api/listings/bulk-publish", json=payload)
        print(f"Bulk Publish response status: {res_bulk.status_code}")
        print(f"Response: {res_bulk.text}")
        
if __name__ == "__main__":
    time.sleep(1) # wait for server to settle
    try:
        test_api()
    except Exception as e:
        print(f"[ERROR] Error connecting to server: {e}")
