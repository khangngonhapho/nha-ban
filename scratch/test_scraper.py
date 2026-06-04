import sys
import os
import json
import sqlite3

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

sys.path.append(os.path.abspath(os.getcwd()))
import crawl_pipeline

# 1. Mock requests.get
class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data
        self.text = json.dumps(json_data)
    
    def json(self):
        return self.json_data

def mock_get(url, headers=None, params=None, timeout=None):
    print(f"[MOCK GET] {url} with params={params}")
    if "users/me" in url:
        return MockResponse(200, {"statusCode": 200, "data": {"name": "Ngô Thái Khang"}})
    elif url == "https://backend.thienkhoi.com/product/v1/property":
        # Load sample list
        with open("scratch/sample_listing_list.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        # Modify the first listing in the sample list to match the UUID of our mock detail to make it link together
        # Mock detail UUID is: 4f92db9e-de71-4df3-91f6-cc198e84d1d3
        listings = data.get("data", {}).get("data", [])
        if listings:
            listings[0]["id"] = "4f92db9e-de71-4df3-91f6-cc198e84d1d3"
            listings[0]["district"] = {"id": 45, "name": "Tân Bình", "provinceId": 2, "provinceName": "TP Hồ Chí Minh"}
        return MockResponse(200, data)
    elif "product/v1/property/4f92db9e-de71-4df3-91f6-cc198e84d1d3" in url:
        with open("scratch/detail_TKQLMB8Q.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return MockResponse(200, data)
    else:
        return MockResponse(404, {"error": "Not Found"})

# Monkeypatch requests
import requests
requests.get = mock_get

# Mock token extraction and refresh to be always successful
crawl_pipeline.extract_tokens = lambda cookie: ("mock_access_token", "mock_refresh_token", {})
crawl_pipeline.try_refresh_tokens = lambda *args, **kwargs: "mock_refreshed_cookie"

# 2. Run scrape_district_proptech
print("=== Running Mocked scrape_district_proptech ===")
# Clear existing listing if any to force recrawl
conn = sqlite3.connect("raw_archive.db")
conn.execute("DELETE FROM listings WHERE tk_id = '4f92db9e-de71-4df3-91f6-cc198e84d1d3'")
conn.commit()
conn.close()

crawl_pipeline.scrape_district_proptech(
    base_list_url="https://proptech.thienkhoi.com/warehouse/sources?districtId=45",
    session_cookie="mock_cookie",
    limit=1,
    filter_district="Tân Bình"
)

# 3. Query the DB to check if it was saved correctly
print("\n=== Checking SQLite Result ===")
conn = sqlite3.connect("raw_archive.db")
conn.row_factory = sqlite3.Row
r = conn.execute("SELECT * FROM listings WHERE tk_id = '4f92db9e-de71-4df3-91f6-cc198e84d1d3'").fetchone()
conn.close()

if r:
    print("[🎉 SUCCESS] Mock listing crawled and saved to SQLite!")
    d = dict(r)
    # Print non-empty keys safely
    for k, v in d.items():
        if v is not None and v != "":
            print(f"  {k}: {repr(v)}")
else:
    print("[❌ FAIL] Listing not found in SQLite.")
