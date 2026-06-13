# -*- coding: utf-8 -*-
import os
import sys
import os
import sys
sys.path.insert(0, os.getcwd())
import requests
import json
from fetcher import extract_tokens, try_refresh_tokens

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    cookie_file = "thienkhoi_cookie.txt"
    if not os.path.exists(cookie_file):
        print("Cookie file does not exist!")
        return

    with open(cookie_file, "r", encoding="utf-8") as f:
        cookie = f.read().strip()

    print(f"Cookie size: {len(cookie)}")
    access_token, refresh_token, cookies_dict = extract_tokens(cookie)
    print(f"Access token size: {len(access_token) if access_token else 0}")
    print(f"Refresh token size: {len(refresh_token) if refresh_token else 0}")
    print(f"Cookies keys: {list(cookies_dict.keys()) if cookies_dict else []}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://proptech.thienkhoi.com",
        "Referer": "https://proptech.thienkhoi.com/"
    }

    url = "https://backend.thienkhoi.com/product/v1/property/3d296527-12f8-4796-b759-c501ca421f6b"
    print(f"Fetching: {url}")
    
    # Try fetching with current access token
    r = requests.get(url, headers=headers, cookies=cookies_dict, timeout=15)
    print(f"Response status: {r.status_code}")
    
    if r.status_code in [401, 403]:
        print("Token expired, trying refresh...")
        refreshed = try_refresh_tokens(cookie_file)
        if refreshed:
            print("Refresh successful!")
            with open(cookie_file, "r", encoding="utf-8") as f:
                new_cookie = f.read().strip()
            access_token, _, cookies_dict = extract_tokens(new_cookie)
            headers["Authorization"] = f"Bearer {access_token}"
            r = requests.get(url, headers=headers, cookies=cookies_dict, timeout=15)
            print(f"New response status: {r.status_code}")
        else:
            print("Refresh failed!")

    if r.status_code == 200:
        print("Success! Saving response to scratch/api_test_response.json")
        with open("scratch/api_test_response.json", "w", encoding="utf-8") as f:
            json.dump(r.json(), f, ensure_ascii=False, indent=2)
    else:
        print(f"Failed to fetch! Status: {r.status_code}")
        try:
            print(f"Response text snippet: {r.text[:500]}")
        except Exception:
            pass

if __name__ == "__main__":
    main()
