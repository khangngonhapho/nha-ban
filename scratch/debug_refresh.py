import os
import requests
import sys

sys.path.append(os.path.abspath(os.getcwd()))
import crawl_pipeline

with open("thienkhoi_cookie.txt", "r", encoding="utf-8") as f:
    cookie_str = f.read().strip()

access_token, refresh_token, cookies_dict = crawl_pipeline.extract_tokens(cookie_str)
print(f"Refresh Token: {refresh_token}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://proptech.thienkhoi.com",
    "Referer": "https://proptech.thienkhoi.com/",
    "Authorization": f"Bearer {access_token}" if access_token else ""
}
payload = {
    "refresh_token": refresh_token,
    "appLogin": "nguonhang",
    "platform": "web"
}
r = requests.post("https://backend.thienkhoi.com/auth/v1/auth/refresh-token", headers=headers, json=payload, timeout=10)
print(f"Status Code: {r.status_code}")
print(f"Response Headers: {r.headers}")
print(f"Response Content: {r.text}")
