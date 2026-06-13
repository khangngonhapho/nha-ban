# -*- coding: utf-8 -*-
import sys
import os
import json

sys.path.insert(0, os.getcwd())
from manager import app

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    # Create a test client
    client = app.test_client()
    
    # 1. Test search with full URL without slash
    url = "https://proptech.thienkhoi.com/warehouse/sources/3d296527-12f8-4796-b759-c501ca421f6b"
    response = client.get(f"/api/listings?search={url}")
    print("Response for search without trailing slash:")
    print("Status:", response.status_code)
    data = json.loads(response.data)
    print("Data keys:", data.keys())
    print("Listings count:", len(data.get("listings", [])))
    print("Status counts:", data.get("status_counts"))
    
    # 2. Test get detail endpoint for deleted listing
    tk_id = "3d296527-12f8-4796-b759-c501ca421f6b"
    response_detail = client.get(f"/api/listings/{tk_id}")
    print("\nResponse for detail query:")
    print("Status:", response_detail.status_code)
    print("Body:", response_detail.data.decode('utf-8'))

if __name__ == "__main__":
    main()
