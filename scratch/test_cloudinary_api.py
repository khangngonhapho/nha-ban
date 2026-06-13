import requests
import os
import json

# Load config
config_file = "D:/LHTBrain/01_PROJECTS/BDS-KhangNgo/settings.json"
if os.path.exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
        
    cloud_name = cfg.get("cloudinary_cloud_name")
    api_key = cfg.get("cloudinary_api_key")
    api_secret = cfg.get("cloudinary_api_secret")
    
    print(f"Cloud Name: {cloud_name}")
    print(f"API Key: {api_key}")
    
    if cloud_name and api_key and api_secret:
        # Cloudinary Admin API URL to list resources
        url = f"https://api.cloudinary.com/v1_1/{cloud_name}/resources/image"
        try:
            print("Attempting to list resources via REST API...")
            r = requests.get(url, auth=(api_key, api_secret), params={"max_results": 3}, timeout=10)
            print(f"Status Code: {r.status_code}")
            if r.status_code == 200:
                print("API call successful!")
                print(json.dumps(r.json(), indent=2))
            else:
                print(f"API Error Response: {r.text}")
        except Exception as e:
            print(f"Request failed: {e}")
    else:
        print("Missing credentials in settings.json")
else:
    print("settings.json not found")
